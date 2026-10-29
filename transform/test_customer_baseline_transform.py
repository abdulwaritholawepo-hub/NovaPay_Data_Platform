
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from production_database.production_DB_connection import (
    production_database_engine_connection
)
from transform.customer_transformer import transform_customers
from transform.customer_transformer_helper import COLUMN_ORDER


def test_customer_baseline_transform():
    engine = production_database_engine_connection()

    with engine.connect() as connection:
        source_customers = connection.execute(
            text("""
                SELECT
                    customer_id,
                    first_name,
                    last_name,
                    email,
                    phone_number,
                    date_of_birth,
                    gender,
                    account_number,
                    wallet_balance,
                    account_status,
                    created_at
                FROM dbo.Customers
                ORDER BY customer_id
            """)
        ).mappings().all()

    source_customers = [dict(customer) for customer in source_customers]

    print(f"Source customers retrieved: {len(source_customers)}")

    transformed_customers = transform_customers(
        customer_data=source_customers
    )

    print(f"Transformed customers: {len(transformed_customers)}")

    assert source_customers, "No source customers were retrieved"
    assert transformed_customers, "No customers were transformed"

    for customer in transformed_customers:
        assert list(customer.keys()) == COLUMN_ORDER, (
            f"Unexpected output columns for customer "
            f"{customer.get('customer_id')}"
        )

        assert customer["customer_id"] is not None
        assert customer["account_number"] is not None

    transformed_ids = [
        customer["customer_id"]
        for customer in transformed_customers
    ]

    assert len(transformed_ids) == len(set(transformed_ids)), (
        "Duplicate customer IDs found in transformed output"
    )

    print("PASS: Customer baseline transformer test completed.")
    print(f"Source records: {len(source_customers)}")
    print(f"Successful transformations: {len(transformed_customers)}")
    print(
        f"Skipped records: "
        f"{len(source_customers) - len(transformed_customers)}"
    )


if __name__ == "__main__":
    test_customer_baseline_transform()
