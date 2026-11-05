import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text

from production_database.production_DB_connection import (
    production_database_engine_connection
)
from production_database.customer_creation import create_customer


engine = production_database_engine_connection()

with engine.connect() as conn:

    transaction = conn.begin()

    try:
        # 1. Retrieve an existing customer
        existing_customer = conn.execute(
            text("""
                SELECT *
                FROM dbo.Customers
                WHERE customer_id = 1
            """)
        ).mappings().one()

        account_number = existing_customer["account_number"]

        # 2. Count existing events for this customer
        events_before = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM dbo.CustomerChangeEvents
                WHERE customer_id = :customer_id
            """),
            {"customer_id": 1}
        ).scalar_one()

        # 3. Attempt to create the same customer again
        duplicate_customer_data = dict(existing_customer)

        duplicate_customer_id = create_customer(
            conn=conn,
            customer_data=duplicate_customer_data
        )

        # 4. Retrieve customer records after the attempt
        customer_count_after = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM dbo.Customers
                WHERE account_number = :account_number
            """),
            {"account_number": account_number}
        ).scalar_one()

        # 5. Retrieve event count after the attempt
        events_after = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM dbo.CustomerChangeEvents
                WHERE customer_id = :customer_id
            """),
            {"customer_id": 1}
        ).scalar_one()

        # 6. Verify duplicate handling
        assert duplicate_customer_id is None, (
            "Expected None for an existing customer."
        )

        assert customer_count_after == 1, (
            f"Expected 1 customer, found {customer_count_after}."
        )

        assert events_after == events_before, (
            "A duplicate event was unexpectedly created."
        )

        print("DUPLICATE DETECTION: PASS")
        print("NO DUPLICATE CUSTOMER INSERT: PASS")
        print("NO ADDITIONAL EVENT: PASS")
        print(f"Existing customer events: {events_before}")
        print(f"Customer events after attempt: {events_after}")

    finally:
        transaction.rollback()
        print("TEST TRANSACTION ROLLED BACK")

engine.dispose()
