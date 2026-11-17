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

from transform.pending_customer_event_retrieval_component import (
    retrieve_and_validate_customer_events
)


def retrieve_checkpoint_state(analytics_engine):
    with analytics_engine.connect() as conn:
        records = conn.execute(
            text("""
                SELECT customer_id, last_event_sequence, updated_at
                FROM gold.customer_incremental_checkpoint
                ORDER BY customer_id
            """)
        ).mappings().all()

    return [dict(record) for record in records]


def retrieve_processed_at_state(production_engine):
    with production_engine.connect() as conn:
        records = conn.execute(
            text("""
                SELECT event_id, processed_at
                FROM dbo.CustomerChangeEvents
                ORDER BY event_id
            """)
        ).mappings().all()

    return [dict(record) for record in records]


def retrieve_expected_pending_event_ids(
    analytics_engine,
    production_engine
):
    checkpoints = retrieve_checkpoint_state(analytics_engine)
    expected_event_ids = []

    with production_engine.connect() as conn:
        for checkpoint in checkpoints:
            events = conn.execute(
                text("""
                    SELECT event_id
                    FROM dbo.CustomerChangeEvents
                    WHERE customer_id = :customer_id
                    AND event_sequence > :last_event_sequence
                    ORDER BY event_sequence
                """),
                {
                    "customer_id": checkpoint["customer_id"],
                    "last_event_sequence": checkpoint["last_event_sequence"]
                }
            ).mappings().all()

            for event in events:
                expected_event_ids.append(event["event_id"])

    return sorted(expected_event_ids)


def test_customer_event_retrieval_integration():

    analytics_engine = analytics_database_engine_connection()
    production_engine = production_database_engine_connection()

    try:
        # Capture database state before execution
        checkpoints_before = retrieve_checkpoint_state(
            analytics_engine
        )

        processed_at_before = retrieve_processed_at_state(
            production_engine
        )

        expected_event_ids = retrieve_expected_pending_event_ids(
            analytics_engine,
            production_engine
        )

        # Execute the actual reusable component
        valid_records, invalid_records = (
            retrieve_and_validate_customer_events(
                analytics_engine,
                production_engine
            )
        )

        # Capture database state after execution
        checkpoints_after = retrieve_checkpoint_state(
            analytics_engine
        )

        processed_at_after = retrieve_processed_at_state(
            production_engine
        )

        # Extract returned event IDs
        valid_event_ids = [
            record["event_metadata"]["event_id"]
            for record in valid_records
        ]

        invalid_event_ids = [
            record["event_metadata"]["event_id"]
            for record in invalid_records
        ]

        returned_event_ids = valid_event_ids + invalid_event_ids

        # Test 1: Correct return structure
        assert isinstance(valid_records, list)
        assert isinstance(invalid_records, list)

        print("PASS: Function returned two lists.")

        # Test 2: All expected pending events were retrieved
        assert sorted(returned_event_ids) == expected_event_ids

        print("PASS: All expected pending events were retrieved.")

        # Test 3: No duplicate event IDs
        assert len(returned_event_ids) == len(set(returned_event_ids))

        print("PASS: No duplicate event IDs.")

        # Test 4: Valid and invalid records are separated
        assert set(valid_event_ids).isdisjoint(set(invalid_event_ids))

        print("PASS: Valid and invalid event IDs are separated.")

        # Test 5: Checkpoints were not modified
        assert checkpoints_before == checkpoints_after

        print("PASS: Incremental checkpoints remain unchanged.")

        # Test 6: Production processed_at was not modified
        assert processed_at_before == processed_at_after

        print("PASS: Production processed_at values remain unchanged.")

        # Summary
        print("\n--- INTEGRATION TEST SUMMARY ---")
        print(f"Expected pending events: {len(expected_event_ids)}")
        print(f"Returned events: {len(returned_event_ids)}")
        print(f"Valid records: {len(valid_records)}")
        print(f"Invalid records: {len(invalid_records)}")

        print("\nALL INTEGRATION TESTS PASSED.")

    finally:
        analytics_engine.dispose()
        production_engine.dispose()


if __name__ == "__main__":
    test_customer_event_retrieval_integration()
