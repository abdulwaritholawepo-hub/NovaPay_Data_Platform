import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from threading import Barrier
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from sqlalchemy import text
from production_database.production_DB_connection import production_database_engine_connection
from production_database.update_db import update_customer
engine = production_database_engine_connection()

def get_customer(conn, customer_id):
    return conn.execute(text("""
        SELECT
            customer_id,
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
        FROM dbo.Customers
        WHERE customer_id = :customer_id
    """), {"customer_id": customer_id}).mappings().one_or_none()


def get_event_count(conn, customer_id):
    return conn.execute(text("""
        SELECT COUNT(*)
        FROM dbo.CustomerChangeEvents
        WHERE customer_id = :customer_id
    """), {"customer_id": customer_id}).scalar_one()


def test_successful_update(engine, customer_id):
    """Test customer update and complete event capture."""

    with engine.connect() as conn:
        transaction = conn.begin()

        try:
            customer_before = get_customer(conn, customer_id)

            assert customer_before is not None

            previous_max_sequence = conn.execute(text("""
                SELECT MAX(event_sequence)
                FROM dbo.CustomerChangeEvents
                WHERE customer_id = :customer_id
            """), {"customer_id": customer_id}).scalar()

            assert previous_max_sequence is not None

            expected_sequence = previous_max_sequence + 1

            new_wallet_balance = (
                Decimal(str(customer_before["wallet_balance"]))
                + Decimal("1.00")
            )

            event_metadata = update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=None,
                wallet_balance=new_wallet_balance,
                account_status=None
            )

            assert event_metadata is not None

            expected_metadata_fields = {
                "customer_id",
                "event_id",
                "event_type",
                "event_sequence",
                "effective_at",
                "recorded_at"
            }

            assert set(event_metadata.keys()) == expected_metadata_fields
            assert event_metadata["customer_id"] == customer_id
            assert event_metadata["event_type"] == "customer_update"
            assert event_metadata["event_sequence"] == expected_sequence
            assert event_metadata["event_id"] is not None
            assert event_metadata["effective_at"] is not None
            assert event_metadata["recorded_at"] is not None
            assert (
                event_metadata["effective_at"]
                == event_metadata["recorded_at"]
            )

            customer_after = get_customer(conn, customer_id)

            assert customer_after["wallet_balance"] == new_wallet_balance

            event_record = conn.execute(text("""
                SELECT *
                FROM dbo.CustomerChangeEvents
                WHERE event_id = :event_id
            """), {
                "event_id": event_metadata["event_id"]
            }).mappings().one()

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
                assert event_record[column] == customer_after[column], (
                    f"Snapshot mismatch for {column}"
                )

            assert event_record["event_type"] == "customer_update"
            assert event_record["event_sequence"] == expected_sequence
            assert event_record["effective_at"] is not None
            assert event_record["recorded_at"] is not None

            print("CUSTOMER UPDATE: PASS")
            print("EVENT CAPTURE: PASS")
            print("EVENT SEQUENCE: PASS")
            print("EVENT METADATA: PASS")
            print("CUSTOMER SNAPSHOT: PASS")

        finally:
            transaction.rollback()

    print("TEST TRANSACTION ROLLED BACK")


def test_unchanged_values(engine, customer_id):
    """Test that unchanged values do not create another event."""

    with engine.connect() as conn:
        transaction = conn.begin()

        try:
            customer_before = get_customer(conn, customer_id)
            assert customer_before is not None

            event_count_before = get_event_count(conn, customer_id)

            event_metadata = update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=customer_before["phone_number"],
                wallet_balance=customer_before["wallet_balance"],
                account_status=customer_before["account_status"]
            )

            assert event_metadata is None

            event_count_after = get_event_count(conn, customer_id)

            assert event_count_after == event_count_before

            # Also verify that supplying None for every field
            # does not create an update event.
            event_metadata_none = update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=None,
                wallet_balance=None,
                account_status=None
            )

            assert event_metadata_none is None

            assert get_event_count(conn, customer_id) == event_count_before

            print("UNCHANGED VALUES: PASS")
            print("NO EVENT FOR UNCHANGED VALUES: PASS")
            print("ALL NONE VALUES: PASS")
            print("NO ADDITIONAL EVENTS: PASS")

        finally:
            transaction.rollback()

    print("TEST TRANSACTION ROLLED BACK")


def test_missing_customer(engine):
    """Test that a missing customer raises ValueError."""

    with engine.connect() as conn:
        transaction = conn.begin()

        try:
            try:
                update_customer(
                    conn=conn,
                    customer_id=-999999,
                    phone_number=None,
                    wallet_balance=Decimal("100.00"),
                    account_status=None
                )

            except ValueError:
                print("MISSING CUSTOMER DETECTION: PASS")

            else:
                raise AssertionError(
                    "Expected ValueError for a missing customer"
                )

        finally:
            transaction.rollback()


def test_transaction_rollback(engine, customer_id):
    """Test that customer changes and event insertion roll back together."""

    with engine.connect() as conn:
        customer_before = get_customer(conn, customer_id)
        assert customer_before is not None

        original_wallet_balance = customer_before["wallet_balance"]
        original_event_count = get_event_count(conn, customer_id)

    event_id = None

    try:
        with engine.begin() as conn:
            new_wallet_balance = (
                Decimal(str(original_wallet_balance))
                + Decimal("5.00")
            )

            event_metadata = update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=None,
                wallet_balance=new_wallet_balance,
                account_status=None
            )

            assert event_metadata is not None

            event_id = event_metadata["event_id"]

            updated_customer = get_customer(conn, customer_id)

            assert updated_customer["wallet_balance"] == new_wallet_balance

            # Deliberately trigger an exception to test rollback.
            raise RuntimeError("Intentional rollback test")

    except RuntimeError as error:
        assert str(error) == "Intentional rollback test"

    else:
        raise AssertionError("Expected transaction rollback")

    # Verify the results using a fresh connection.
    with engine.connect() as conn:
        customer_after_rollback = get_customer(conn, customer_id)

        event_count_after_rollback = get_event_count(
            conn,
            customer_id
        )

        event_after_rollback = conn.execute(text("""
            SELECT event_id
            FROM dbo.CustomerChangeEvents
            WHERE event_id = :event_id
        """), {"event_id": event_id}).scalar_one_or_none()

        assert (
            customer_after_rollback["wallet_balance"]
            == original_wallet_balance
        )

        assert event_count_after_rollback == original_event_count
        assert event_after_rollback is None

        print("CUSTOMER UPDATE ROLLBACK: PASS")
        print("EVENT INSERT ROLLBACK: PASS")
        print("ATOMICITY VALIDATION: PASS")


def test_concurrent_updates(engine, customer_id):
    """Test concurrent updates to the same customer."""

    with engine.connect() as conn:
        customer_before = get_customer(conn, customer_id)

        assert customer_before is not None

        original_wallet_balance = customer_before["wallet_balance"]
        original_phone_number = customer_before["phone_number"]

        previous_max_sequence = conn.execute(text("""
            SELECT MAX(event_sequence)
            FROM dbo.CustomerChangeEvents
            WHERE customer_id = :customer_id
        """), {"customer_id": customer_id}).scalar()

        assert previous_max_sequence is not None

        original_event_count = get_event_count(conn, customer_id)

    expected_sequence_1 = previous_max_sequence + 1
    expected_sequence_2 = previous_max_sequence + 2

    new_wallet_balance = (
        Decimal(str(original_wallet_balance)) + Decimal("10.00")
    )

    new_phone_number = "+234" + uuid.uuid4().hex[:10]

    barrier = Barrier(2)

    def update_wallet():
        with engine.begin() as conn:
            barrier.wait(timeout=20)

            return update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=None,
                wallet_balance=new_wallet_balance,
                account_status=None
            )

    def update_phone():
        with engine.begin() as conn:
            barrier.wait(timeout=20)

            return update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=new_phone_number,
                wallet_balance=None,
                account_status=None
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:

            wallet_future = executor.submit(update_wallet)
            phone_future = executor.submit(update_phone)

            wallet_metadata = wallet_future.result()
            phone_metadata = phone_future.result()

        assert wallet_metadata is not None
        assert phone_metadata is not None

        # Verify that both updates produced different events.
        event_ids = {
            wallet_metadata["event_id"],
            phone_metadata["event_id"]
        }

        assert len(event_ids) == 2

        # Verify that the events received consecutive sequences.
        event_sequences = {
            wallet_metadata["event_sequence"],
            phone_metadata["event_sequence"]
        }

        assert event_sequences == {
            expected_sequence_1,
            expected_sequence_2
        }

        # Verify that exactly two events were added.
        with engine.connect() as conn:

            event_count_after = get_event_count(
                conn,
                customer_id
            )

            assert event_count_after == original_event_count + 2

            final_customer = get_customer(conn, customer_id)

            assert final_customer["wallet_balance"] == new_wallet_balance
            assert final_customer["phone_number"] == new_phone_number

            events = conn.execute(text("""
                SELECT *
                FROM dbo.CustomerChangeEvents
                WHERE customer_id = :customer_id
                  AND event_sequence IN (:sequence_1, :sequence_2)
                ORDER BY event_sequence
            """), {
                "customer_id": customer_id,
                "sequence_1": expected_sequence_1,
                "sequence_2": expected_sequence_2
            }).mappings().all()

            assert len(events) == 2

            first_event = events[0]
            second_event = events[1]

            # The first event must contain exactly one of the two changes.
            first_event_has_wallet_change = (
                first_event["wallet_balance"] == new_wallet_balance
                and first_event["phone_number"] == original_phone_number
            )

            first_event_has_phone_change = (
                first_event["wallet_balance"] == original_wallet_balance
                and first_event["phone_number"] == new_phone_number
            )

            assert (
                first_event_has_wallet_change
                or first_event_has_phone_change
            )

            # The second event must contain both changes.
            assert second_event["wallet_balance"] == new_wallet_balance
            assert second_event["phone_number"] == new_phone_number

            # Validate the complete second event snapshot.
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
                assert second_event[column] == final_customer[column], (
                    f"Concurrent snapshot mismatch for {column}"
                )

        print("CONCURRENT UPDATES: PASS")
        print("TWO DISTINCT EVENTS: PASS")
        print("CONSECUTIVE EVENT SEQUENCES: PASS")
        print("NO LOST UPDATE: PASS")
        print("EVENT SNAPSHOT ORDER: PASS")
        print("FINAL CUSTOMER STATE: PASS")

    finally:
        # Restore the original customer values.
        # This restoration is itself captured as an update event.
        with engine.begin() as conn:

            update_customer(
                conn=conn,
                customer_id=customer_id,
                phone_number=original_phone_number,
                wallet_balance=original_wallet_balance,
                account_status=None
            )

        # Confirm that the original values have been restored.
        with engine.connect() as conn:

            restored_customer = get_customer(conn, customer_id)

            assert (
                restored_customer["phone_number"]
                == original_phone_number
            )

            assert (
                restored_customer["wallet_balance"]
                == original_wallet_balance
            )

        print("CUSTOMER VALUES RESTORED: PASS")


def test_missing_event_history(engine):
    customer_data = {
        "first_name": "Test",
        "last_name": "MissingHistory",
        "gender": "Male",
        "date_of_birth": "1998-05-15",
        "phone_number": "+234" + str(uuid.uuid4().int)[:10],
        "email": f"missing_history_{uuid.uuid4().hex[:10]}@test.com",
        "account_number": str(uuid.uuid4().int)[:20],
        "wallet_balance": Decimal("1000.00"),
        "account_status": "active"
    }

    with engine.connect() as conn:
        transaction = conn.begin()

        try:
            # 1. Insert a customer directly without creating an event.
            customer_id = conn.execute(text("""
                INSERT INTO dbo.Customers (
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
                OUTPUT INSERTED.customer_id
                VALUES (
                    :first_name,
                    :last_name,
                    :gender,
                    :date_of_birth,
                    :phone_number,
                    :email,
                    :account_number,
                    :wallet_balance,
                    :account_status,
                    sysutcdatetime()
                )
            """), customer_data).scalar_one()

            print("TEMPORARY CUSTOMER CREATION: PASS")

            # 2. Confirm that the customer has no event history.
            event_count = get_event_count(conn, customer_id)

            assert event_count == 0, (
                f"Expected no events, found {event_count}"
            )

            print("MISSING EVENT HISTORY CONFIRMED: PASS")

            # 3. Attempt an update.
            try:
                update_customer(
                    conn=conn,
                    customer_id=customer_id,
                    phone_number=None,
                    wallet_balance=Decimal("1500.00"),
                    account_status=None
                )

            except ValueError:
                print("MISSING EVENT HISTORY DETECTION: PASS")

            else:
                raise AssertionError(
                    "Expected ValueError for customer with no event history"
                )

            # 4. Verify that the customer was not updated.
            customer_after = get_customer(conn, customer_id)

            assert customer_after["wallet_balance"] == Decimal("1000.00"), (
                "Customer was updated despite missing event history"
            )

            print("CUSTOMER STATE UNCHANGED: PASS")

            # 5. Verify that no event was inserted.
            event_count_after = get_event_count(conn, customer_id)

            assert event_count_after == 0, (
                f"Expected zero events, found {event_count_after}"
            )

            print("NO EVENT INSERTED: PASS")

        finally:
            # 6. Remove the temporary customer through rollback.
            transaction.rollback()

        # 7. Confirm that the temporary customer no longer exists.
        remaining_customer = conn.execute(text("""
            SELECT customer_id
            FROM dbo.Customers
            WHERE customer_id = :customer_id
        """), {"customer_id": customer_id}).scalar_one_or_none()

        assert remaining_customer is None, (
            "Temporary customer was not rolled back"
        )

        print("TEST TRANSACTION ROLLED BACK: PASS")




def run_tests(engine, customer_id=1):
    print("\n========== TEST 1: SUCCESSFUL UPDATE ==========")
    test_successful_update(engine, customer_id)

    print("\n========== TEST 2: UNCHANGED VALUES ==========")
    test_unchanged_values(engine, customer_id)

    print("\n========== TEST 3: MISSING CUSTOMER ==========")
    test_missing_customer(engine)

    print("\n========== TEST 4: TRANSACTION ROLLBACK ==========")
    test_transaction_rollback(engine, customer_id)
   
    print("\n========== TEST 5: CONCURRENT UPDATES ==========")
    test_concurrent_updates(engine, customer_id)

    print("\n========== TEST 6: MISSING EVENT HISTORY ==========")
    test_missing_event_history(engine)

    print("\n========== ALL TESTS COMPLETED ==========")


if __name__ == "__main__":
    run_tests(engine=engine, customer_id=1)
    
