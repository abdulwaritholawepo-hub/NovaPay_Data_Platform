
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
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4


production_engine = production_database_engine_connection()
analytics_engine = analytics_database_engine_connection()

customer_id = None

try:
    unique_id = uuid4().hex[:10]

    # STEP 1: Create and commit a temporary customer.
    # Deliberately do NOT create a CustomerChangeEvents record.

    with production_engine.begin() as production_conn:

        customer_id = production_conn.execute(
            text("""
                INSERT INTO dbo.Customers (
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
                )
                OUTPUT INSERTED.customer_id
                VALUES (
                    'Missing',
                    'Event Test',
                    :email,
                    :phone_number,
                    :date_of_birth,
                    'Male',
                    :account_number,
                    :wallet_balance,
                    'Active',
                    :created_at
                )
            """),
            {
                "email": f"missing_event_{unique_id}@novapay.com",
                "phone_number": f"080{uuid4().int % 100000000:08d}",
                "date_of_birth": date(1998, 5, 12),
                "account_number": f"9{uuid4().int % 1000000000:09d}",
                "wallet_balance": Decimal("30000.00"),
                "created_at": datetime.now()
            }
        ).scalar_one()

    print(f"Temporary customer created and committed: {customer_id}")

    # STEP 2: Confirm that the customer has no initial INSERT event.

    with production_engine.connect() as production_conn:

        event_count = production_conn.execute(
            text("""
                SELECT COUNT(*)
                FROM dbo.CustomerChangeEvents
                WHERE customer_id = :customer_id
                  AND event_type = 'customer_insert'
                  AND event_sequence = 1
            """),
            {"customer_id": customer_id}
        ).scalar_one()

    assert event_count == 0, (
        "Test setup failed: an initial INSERT event already exists."
    )

    print("PASS: No initial INSERT event exists.")

    # STEP 3: Run the initializer and expect ValueError.

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
            "Initializer should have rejected the missing initial event."
        )

    print("\nExpected validation error:")
    print(caught_error)

    # Confirm the error identifies our temporary customer.

    if str(customer_id) not in str(caught_error):
        raise AssertionError(
            "The validation error did not identify the temporary customer."
        )

    print("PASS: Missing initial INSERT event detected.")

    # STEP 4: Confirm no checkpoint was created.

    with analytics_engine.connect() as analytics_conn:

        checkpoint_count = analytics_conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.customer_incremental_checkpoint
                WHERE customer_id = :customer_id
            """),
            {"customer_id": customer_id}
        ).scalar_one()

    assert checkpoint_count == 0, (
        "A checkpoint was created despite the missing event."
    )

    print("PASS: No checkpoint was created.")

finally:
    # STEP 5: Clean up only this temporary test customer.

    if customer_id is not None:

        with analytics_engine.begin() as analytics_conn:
            analytics_conn.execute(
                text("""
                    DELETE FROM gold.customer_incremental_checkpoint
                    WHERE customer_id = :customer_id
                """),
                {"customer_id": customer_id}
            )

        with production_engine.begin() as production_conn:
            production_conn.execute(
                text("""
                    DELETE FROM dbo.Customers
                    WHERE customer_id = :customer_id
                """),
                {"customer_id": customer_id}
            )

        print(f"\nTemporary customer {customer_id} cleaned up.")

    production_engine.dispose()
    analytics_engine.dispose()
