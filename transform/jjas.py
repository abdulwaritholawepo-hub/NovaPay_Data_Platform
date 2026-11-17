
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from analytics_database.analytics_DB_connection import (
    analytics_database_engine_connection
)

from production_database.production_DB_connection import (
    production_database_engine_connection
)


def capture_incremental_checkpoints(analytics_engine):
    with analytics_engine.connect() as conn:
        records = conn.execute(
            text("""
                SELECT
                    customer_id,
                    last_event_sequence,
                    updated_at
                FROM gold.customer_incremental_checkpoint
                ORDER BY customer_id
            """)
        ).mappings().all()

    return [dict(record) for record in records]


def capture_event_processed_at(production_engine):
    with production_engine.connect() as conn:
        records = conn.execute(
            text("""
                SELECT
                    event_id,
                    processed_at
                FROM dbo.CustomerChangeEvents
                ORDER BY event_id
            """)
        ).mappings().all()

    return [dict(record) for record in records]


analytics_engine = analytics_database_engine_connection()
production_engine = production_database_engine_connection()

try:
    # 1. Capture database states before retrieval and validation

    checkpoints_before = capture_incremental_checkpoints(
        analytics_engine
    )

    processed_at_before = capture_event_processed_at(
        production_engine
    )

    print(
        "Initial checkpoint records:",
        len(checkpoints_before)
    )

    print(
        "Initial event audit records:",
        len(processed_at_before)
    )

    # 2. Execute the actual retrieval and validation component

    import transform.pending_customer_event_retrieval_component

    # 3. Capture database states after retrieval and validation

    checkpoints_after = capture_incremental_checkpoints(
        analytics_engine
    )

    processed_at_after = capture_event_processed_at(
        production_engine
    )

    # 4. Compare before and after states

    checkpoints_unchanged = (
        checkpoints_before == checkpoints_after
    )

    processed_at_unchanged = (
        processed_at_before == processed_at_after
    )

    print("\n--- IMMUTABILITY TEST RESULTS ---")

    print(
        "Checkpoint records unchanged:",
        checkpoints_unchanged
    )

    print(
        "Production processed_at unchanged:",
        processed_at_unchanged
    )

    if checkpoints_unchanged:
        print("PASS: Incremental checkpoints were not modified.")
    else:
        print("FAIL: Incremental checkpoints changed.")

    if processed_at_unchanged:
        print("PASS: Production processed_at values were not modified.")
    else:
        print("FAIL: Production processed_at values changed.")

finally:
    analytics_engine.dispose()
    production_engine.dispose()
