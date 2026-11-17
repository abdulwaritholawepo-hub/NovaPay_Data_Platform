import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch, MagicMock


from transform.pending_customer_event_retrieval_component import (
    retrieve_and_validate_customer_events
)


def test_empty_customer_event_batch():

    analytics_engine = MagicMock()
    production_engine = MagicMock()

    try:
        # Simulate existing checkpoints
        mock_checkpoints = [
            {
                "customer_id": 19,
                "last_event_sequence": 1
            },
            {
                "customer_id": 20,
                "last_event_sequence": 1
            }
        ]

        # Simulate no pending events in Production
        mock_empty_events = []

        mock_analytics_result = MagicMock()
        mock_analytics_result.mappings.return_value.all.return_value = (
            mock_checkpoints
        )

        mock_production_result = MagicMock()
        mock_production_result.mappings.return_value.all.return_value = (
            mock_empty_events
        )

        mock_analytics_context = MagicMock()
        mock_analytics_context.__enter__.return_value.execute.return_value = (
            mock_analytics_result
        )

        mock_production_context = MagicMock()
        mock_production_context.__enter__.return_value.execute.return_value = (
            mock_production_result
        )

        analytics_engine.begin.return_value = mock_analytics_context
        production_engine.begin.return_value = mock_production_context

        # Execute actual component
        with patch(
            "transform.pending_customer_event_retrieval_component."
            "analytics_engine",
            analytics_engine,
            create=True
        ):
            valid_records, invalid_records = (
                retrieve_and_validate_customer_events(
                    analytics_engine,
                    production_engine
                )
            )

        # Test 1: Both results must be lists
        assert isinstance(valid_records, list)
        assert isinstance(invalid_records, list)

        print("PASS: Function returned two lists.")

        # Test 2: Both lists must be empty
        assert valid_records == []
        assert invalid_records == []

        print("PASS: Empty batch returned two empty lists.")

        # Test 3: Production should be queried for pending events
        assert production_engine.begin.called

        print("PASS: Production retrieval was executed.")

        # Test 4: No event records were returned
        assert len(valid_records) + len(invalid_records) == 0

        print("PASS: No event records were returned.")

        print("\n--- EMPTY BATCH TEST SUMMARY ---")
        print(f"Valid records: {len(valid_records)}")
        print(f"Invalid records: {len(invalid_records)}")
        print("\nALL EMPTY BATCH TESTS PASSED.")

    finally:
        pass


if __name__ == "__main__":
    test_empty_customer_event_batch()
