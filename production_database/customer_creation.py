from sqlalchemy import text


def create_customer(conn, customer_data):
    """
    Create a customer and capture the initial customer snapshot
    in CustomerChangeEvents within the caller's transaction.

    Returns:
        int: Newly created customer_id.
        None: Customer already exists.
    """

    existing_customer = conn.execute(
        text("""
            SELECT customer_id
            FROM dbo.Customers WITH (UPDLOCK, HOLDLOCK)
            WHERE account_number = :account_number
        """),
        {
            "account_number": customer_data["account_number"]
        }
    ).scalar_one_or_none()

    if existing_customer is not None:
        return None

    customer_id = conn.execute(
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
                :first_name,
                :last_name,
                :email,
                :phone_number,
                :date_of_birth,
                :gender,
                :account_number,
                :wallet_balance,
                :account_status,
                :created_at
            )
        """),
        customer_data
    ).scalar_one()

    customer_snapshot = conn.execute(
        text("""
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
        """),
        {"customer_id": customer_id}
    ).mappings().one()

    event_timestamp = conn.execute(
        text("SELECT SYSUTCDATETIME()")
    ).scalar_one()
    effective_at = customer_snapshot["created_at"]
    event_data = {
        **customer_snapshot,
        "event_type": "customer_insert",
        "event_sequence": 1,
        "effective_at": effective_at,
        "recorded_at": event_timestamp
    }

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
                created_at,
                recorded_at
            )
            VALUES (
                :customer_id,
                :event_type,
                :effective_at,
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
                :created_at,
                :recorded_at
            )
        """),
        event_data
    )

    return customer_id
