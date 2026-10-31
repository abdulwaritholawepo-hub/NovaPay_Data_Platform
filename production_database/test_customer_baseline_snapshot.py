
import os
import sys

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from production_database.customer_baseline_snapshot import (
    get_customer_baseline_snapshot,
)


def main():
    customer_snapshot = get_customer_baseline_snapshot()

    assert isinstance(customer_snapshot, list), (
        "Snapshot result must be a list."
    )

    expected_fields = {
        "customer_id",
        "event_sequence",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "date_of_birth",
        "gender",
        "account_number",
        "wallet_balance",
        "account_status",
        "created_at",
    }

    for index, customer in enumerate(customer_snapshot):
        assert isinstance(customer, dict), (
            f"Record {index} must be a dictionary."
        )

        assert set(customer.keys()) == expected_fields, (
            f"Record {index} has unexpected fields."
        )

    print("PASS | Snapshot result is a list.")
    print("PASS | All records are dictionaries.")
    print("PASS | All records contain the expected fields.")
    print(f"Customers captured: {len(customer_snapshot)}")

    if customer_snapshot:
        print("First customer:", customer_snapshot[0])


if __name__ == "__main__":
    main()
