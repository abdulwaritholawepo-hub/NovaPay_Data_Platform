
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_database.production_DB_connection import (
    production_database_engine_connection
)
from analytics_database.analytics_DB_connection import (
    analytics_database_engine_connection
)
from gold_batch_loader.customer_incremental_checkpoint_initializer import (
    initialize_customer_incremental_checkpoints
)

from sqlalchemy import text


production_engine = production_database_engine_connection()
analytics_engine = analytics_database_engine_connection()

customer_id = 999999

baseline_run_id = "E47C0DCE-BA90-4DAE-B6AA-8F5655B0AE69"

temporary_record_inserted = False

try:
    # STEP 1: Confirm the temporary customer ID does not exist.

    with production_engine.connect() as conn:
        production_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM dbo.Customers
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).scalar_one()

    if production_count != 0:
        raise ValueError(
            "Temporary customer ID already exists in Production."
        )

    print("PASS: Temporary customer ID does not exist in Production.")

    # STEP 2: Confirm the ID is not already in either checkpoint table.

    with analytics_engine.connect() as conn:

        baseline_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.customer_baseline_checkpoint
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).scalar_one()

        incremental_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.customer_incremental_checkpoint
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).scalar_one()

    if baseline_count != 0 or incremental_count != 0:
        raise ValueError(
            "Temporary customer ID already exists in Analytics."
        )

    print("PASS: Temporary customer ID is unused in Analytics.")

    # STEP 3: Insert a temporary baseline checkpoint record.

    with analytics_engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO gold.customer_baseline_checkpoint (
                    baseline_run_id,
                    customer_id,
                    baseline_event_sequence,
                    captured_at
                )
                VALUES (
                    :baseline_run_id,
                    :customer_id,
                    0,
                    SYSUTCDATETIME()
                )
            """),
            {
                "baseline_run_id": baseline_run_id,
                "customer_id": customer_id
            }
        )

    temporary_record_inserted = True

    print("Temporary invalid baseline customer inserted.")

    # STEP 4: Capture existing incremental checkpoints.

    with analytics_engine.connect() as conn:
        checkpoints_before = conn.execute(
            text("""
                SELECT customer_id, last_event_sequence
                FROM gold.customer_incremental_checkpoint
                ORDER BY customer_id
            """)
        ).mappings().all()

    checkpoints_before = [
        (row["customer_id"], row["last_event_sequence"])
        for row in checkpoints_before
    ]

    # STEP 5: Run the initializer and expect ValueError.

    caught_error = None

    try:
        initialize_customer_incremental_checkpoints(
            production_engine=production_engine,
            analytics_engine=analytics_engine
        )

    except ValueError as error:
        caught_error = error

    if caught_error is None:
        raise AssertionError(
            "Initializer should have rejected the invalid baseline customer."
        )

    print("\nExpected validation error:")
    print(caught_error)

    if str(customer_id) not in str(caught_error):
        raise AssertionError(
            "Error did not identify the invalid baseline customer."
        )

    print("PASS: Invalid baseline customer detected.")

    # STEP 6: Verify incremental checkpoints remain unchanged.

    with analytics_engine.connect() as conn:
        checkpoints_after = conn.execute(
            text("""
                SELECT customer_id, last_event_sequence
                FROM gold.customer_incremental_checkpoint
                ORDER BY customer_id
            """)
        ).mappings().all()

    checkpoints_after = [
        (row["customer_id"], row["last_event_sequence"])
        for row in checkpoints_after
    ]

    assert checkpoints_before == checkpoints_after, (
        "Incremental checkpoints changed unexpectedly."
    )

    print("PASS: Existing incremental checkpoints remain unchanged.")

finally:
    # STEP 7: Remove only the temporary baseline checkpoint.

    if temporary_record_inserted:
        with analytics_engine.begin() as conn:
            conn.execute(
                text("""
                    DELETE FROM gold.customer_baseline_checkpoint
                    WHERE baseline_run_id = :baseline_run_id
                      AND customer_id = :customer_id
                """),
                {
                    "baseline_run_id": baseline_run_id,
                    "customer_id": customer_id
                }
            )

        print("\nTemporary baseline checkpoint cleaned up.")

    production_engine.dispose()
    analytics_engine.dispose()
