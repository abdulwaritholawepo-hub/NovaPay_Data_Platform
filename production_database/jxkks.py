import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from production_database.production_DB_connection import (
    production_database_engine_connection,
)

engine = production_database_engine_connection()
customer_id = 2

with engine.connect() as conn:
    transaction = conn.begin()

    try:
        original_phone = conn.execute(
            text("""
                SELECT phone_number
                FROM dbo.Customers
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id},
        ).scalar_one()

        # Change the customer inside the transaction.
        conn.execute(
            text("""
                UPDATE dbo.Customers
                SET phone_number = :phone_number
                WHERE customer_id = :customer_id
            """),
            {
                "customer_id": customer_id,
                "phone_number": "TEST_ROLLBACK",
            },
        )

        # Deliberately cause an insert failure.
        conn.execute(
            text("""
                INSERT INTO dbo.CustomerChangeEvents (
                    customer_id,
                    event_type,
                    effective_at,
                    event_sequence,
                    first_name,
                    last_name,
                    gender,
                    date_of_birth,
                    phone_number,
                    email,
                    account_number,
                    wallet_balance,
                    account_status,
                    created_at
                )
                VALUES (
                    :customer_id,
                    :event_type,
                    SYSDATETIME(),
                    :event_sequence,
                    :first_name,
                    :last_name,
                    :gender,
                    :date_of_birth,
                    :phone_number,
                    :email,
                    :account_number,
                    :wallet_balance,
                    :account_status,
                    :created_at
                )
            """),
            {
                "customer_id": customer_id,
                "event_type": "INVALID_EVENT_TYPE_THAT_EXCEEDS_LIMIT",
                "event_sequence": 999999,
                "first_name": "Test",
                "last_name": "Rollback",
                "gender": "Other",
                "date_of_birth": "2000-01-01",
                "phone_number": "TEST_ROLLBACK",
                "email": "rollback@example.com",
                "account_number": None,
                "wallet_balance": 0,
                "account_status": "active",
                "created_at": "2026-01-01",
            },
        )

        # This should not be reached if the insert fails as expected.
        transaction.rollback()
        raise RuntimeError(
            "The event insert unexpectedly succeeded; rollback test is inconclusive."
        )

    except Exception as exc:
        if transaction.is_active:
            transaction.rollback()

        print(f"Transaction rolled back after failure: {exc}")

    # Verify the persisted value after rollback.
    final_phone = conn.execute(
        text("""
            SELECT phone_number
            FROM dbo.Customers
            WHERE customer_id = :customer_id
        """),
        {"customer_id": customer_id},
    ).scalar_one()

    print("Original phone:", original_phone)
    print("Phone after rollback:", final_phone)
    print("Rollback successful:", original_phone == final_phone)