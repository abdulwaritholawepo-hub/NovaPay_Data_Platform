import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor
from gold_batch_loader.customer_incremental_checkpoint_initializer import (
    initialize_customer_incremental_checkpoints
)
from analytics_database.analytics_DB_connection import (
    analytics_database_engine_connection
)
from production_database.production_DB_connection import (
    production_database_engine_connection
)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


production_engine = production_database_engine_connection()
analytics_engine = analytics_database_engine_connection()

customer_id = 20

# Both initializer executions must reach the insertion stage together.
insert_barrier = Barrier(2, timeout=30)

try:
    print(f"Reusing existing test customer: {customer_id}")

    # Confirm customer 20 exists in Production.
    with production_engine.connect() as conn:
        customer_exists = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM dbo.Customers
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).scalar_one()

    if customer_exists != 1:
        raise ValueError(
            f"Customer {customer_id} does not exist in Production."
        )

    # Confirm customer 20 has no incremental checkpoint yet.
    with analytics_engine.connect() as conn:
        existing_checkpoint = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.customer_incremental_checkpoint
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).scalar_one()

    if existing_checkpoint != 0:
        raise ValueError(
            f"Customer {customer_id} already has a checkpoint. "
            "Use a fresh test customer for this concurrency test."
        )

    # Each worker runs an independent initializer invocation.
    def run_initializer():
        initialize_customer_incremental_checkpoints(
            production_engine=production_engine,
            analytics_engine=analytics_engine,
            before_insert=insert_barrier.wait
        )

        return "Initializer completed successfully"

    # Run both initializers concurrently.
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(run_initializer),
            executor.submit(run_initializer)
        ]

        for future in futures:
            print(future.result())

    # Verify the resulting checkpoint.
    with analytics_engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    customer_id,
                    COUNT(*) AS checkpoint_count,
                    MIN(last_event_sequence) AS min_sequence,
                    MAX(last_event_sequence) AS max_sequence
                FROM gold.customer_incremental_checkpoint
                WHERE customer_id = :customer_id
                GROUP BY customer_id
            """),
            {"customer_id": customer_id}
        ).mappings().one_or_none()

    if result is None:
        raise AssertionError("No checkpoint was created.")

    print("\nConcurrency test result:")
    print(dict(result))

    assert result["checkpoint_count"] == 1, (
        "Expected exactly one checkpoint."
    )

    assert result["min_sequence"] == 0, (
        "Expected checkpoint sequence 0."
    )

    assert result["max_sequence"] == 0, (
        "Expected checkpoint sequence 0."
    )

    print("\nPASS: Only one checkpoint was created.")
    print("PASS: The checkpoint started at sequence 0.")

finally:
    production_engine.dispose()
    analytics_engine.dispose()
