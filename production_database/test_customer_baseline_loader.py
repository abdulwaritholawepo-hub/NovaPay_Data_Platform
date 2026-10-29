import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from production_database.customer_baseline_loader import (
    get_customer_baseline_snapshot,
    prepare_customer_baseline_records,
    transform_customer_baseline,
)


def test_customer_baseline_preparation():
    snapshot = get_customer_baseline_snapshot()

    assert snapshot, "Snapshot must contain customer records"

    customer_records, checkpoint_records = (
        prepare_customer_baseline_records(snapshot)
    )

    transformed_customers = transform_customer_baseline(
        customer_records
    )

    snapshot_customer_ids = {
        record["customer_id"] for record in snapshot
    }
    transformed_customer_ids = {
        record["customer_id"] for record in transformed_customers
    }
    checkpoint_customer_ids = {
        record["customer_id"] for record in checkpoint_records
    }

    assert len(snapshot) == len(customer_records)
    assert len(snapshot) == len(checkpoint_records)
    assert snapshot_customer_ids == transformed_customer_ids
    assert snapshot_customer_ids == checkpoint_customer_ids

    assert all(
        "event_sequence" not in record
        for record in customer_records
    )

    assert all(
        "baseline_event_sequence" in record
        for record in checkpoint_records
    )

    print("PASS: Customer baseline preparation test completed.")
    print(f"Snapshot records: {len(snapshot)}")
    print(f"Transformed records: {len(transformed_customers)}")
    print(f"Checkpoint records prepared: {len(checkpoint_records)}")


if __name__ == "__main__":
    test_customer_baseline_preparation()
