import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import text

from production_database.production_DB_connection import (
    production_database_engine_connection
)
from production_database.customer_creation import create_customer


# Generate unique test values
unique_id = uuid4().hex

customer_data = {
    "first_name": "Test",
    "last_name": "Customer",
    "email": f"test_{unique_id}@novapay.com",
    "phone_number": f"09{unique_id[:10]}",
    "date_of_birth": date(1998, 5, 15),
    "gender": "Male",
    "account_number": f"9{unique_id[:10]}",
    "wallet_balance": Decimal("2500.00"),
    "account_status": "Active",
    "created_at": datetime.now(timezone.utc).replace(tzinfo=None)
}


engine = production_database_engine_connection()

with engine.connect() as conn:

    transaction = conn.begin()

    try:
        # 1. Create customer and capture INSERT event
        customer_id = create_customer(
            conn=conn,
            customer_data=customer_data
        )

        assert customer_id is not None, (
            "Customer creation failed or account already exists."
        )

        # 2. Retrieve the persisted customer
        customer = conn.execute(
            text("""
                SELECT *
                FROM dbo.Customers
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).mappings().one()

        # 3. Retrieve the customer's captured events
        events = conn.execute(
            text("""
                SELECT *
                FROM dbo.CustomerChangeEvents
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).mappings().all()

        # 4. Verify exactly one event exists
        assert len(events) == 1, (
            f"Expected 1 event, found {len(events)}."
        )

        event = events[0]

        # 5. Verify event metadata
        assert event["event_type"] == "customer_insert"
        assert event["event_sequence"] == 1

        # 6. Verify timestamps
        assert event["effective_at"] == customer["created_at"]
        assert event["recorded_at"] is not None

        # 7. Verify the complete customer snapshot
        snapshot_columns = [
            "customer_id",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "phone_number",
            "email",
            "account_number",
            "wallet_balance",
            "account_status",
            "created_at"
        ]

        for column in snapshot_columns:
            assert customer[column] == event[column], (
                f"Snapshot mismatch in column: {column}"
            )

        print("CUSTOMER CREATION: PASS")
        print("EVENT CAPTURE: PASS")
        print("EVENT SEQUENCE: PASS")
        print("TIMESTAMP VALIDATION: PASS")
        print("CUSTOMER SNAPSHOT VALIDATION: PASS")
        print(f"Test customer_id: {customer_id}")

    finally:
        # Remove the test customer and event
        transaction.rollback()
        print("TEST TRANSACTION ROLLED BACK")

engine.dispose()
