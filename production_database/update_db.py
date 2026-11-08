from sqlalchemy import text


def update_customer(conn, customer_id, phone_number, wallet_balance, account_status):
    event_columns = [
        "customer_id",
        "event_type",
        "effective_at",
        "event_sequence",
        "first_name",
        "last_name",
        "gender",
        "date_of_birth",
        "phone_number",
        "email",
        "account_number",
        "wallet_balance",
        "account_status",
        "created_at",
        "recorded_at"
    ]
    customers_record = conn.execute(text("""
            SELECT customer_id, first_name, last_name,
            gender, date_of_birth, phone_number,
            email, account_number,wallet_balance,
            account_status, created_at
            FROM dbo.Customers WITH (UPDLOCK,HOLDLOCK)
            WHERE customer_id = :customer_id
    """), {"customer_id": customer_id}).mappings().one_or_none()
    if not customers_record:
        raise ValueError(f"Customer with ID {customer_id} does not exist")
    changed_fields = {}

    has_changes = False
    if phone_number != customers_record.get("phone_number") and phone_number is not None:
        changed_fields["phone_number"] = phone_number
    if wallet_balance != customers_record.get("wallet_balance") and wallet_balance is not None:
        changed_fields["wallet_balance"] = wallet_balance
    if account_status != customers_record.get("account_status") and account_status is not None:
        changed_fields["account_status"] = account_status
    if changed_fields:
        has_changes = True

    if has_changes:
        max_event_sequence = conn.execute(text("""
                            SELECT max(event_sequence)
                            FROM dbo.CustomerChangeEvents 
                            WHERE customer_id = :customer_id
                            """), {"customer_id": customer_id}).scalar()
        if max_event_sequence is None:
            raise ValueError
        else:
            next_event_sequence = max_event_sequence + 1

        update_params = changed_fields.copy()
        update_params["customer_id"] = customer_id
        field_list = []
        for field in changed_fields:
            set_assignment = f"{field} = :{field}"
            field_list.append(set_assignment)
        update_query = text(f"""
                    UPDATE dbo.Customers
                    SET {",".join(field_list)}
                        where customer_id = :customer_id
        """)
        update_field = conn.execute(update_query, update_params).rowcount
        if update_field != 1:
            raise ValueError(
                f"Customer update failed: expected to update 1 row for "
                f"customer_id {customer_id}, but {update_field} rows were affected."
            )

        customers_record_after_update = conn.execute(text("""
                SELECT customer_id, first_name, last_name,
                gender, date_of_birth, phone_number,
                email, account_number,wallet_balance,
                account_status, created_at
                FROM dbo.Customers
                WHERE customer_id = :customer_id
                """), {"customer_id": customer_id}).mappings().one()

        sysutcdatetime = conn.execute(text("""
                select
                    sysutcdatetime()
            """)).scalar()

        event_data = {
            "customer_id": customers_record_after_update.get("customer_id"),
            "event_type": "customer_update",
            "event_sequence": next_event_sequence,
            "effective_at": sysutcdatetime,
            "first_name": customers_record_after_update.get("first_name"),
            "last_name": customers_record_after_update.get("last_name"),
            "gender": customers_record_after_update.get("gender"),
            "date_of_birth": customers_record_after_update.get("date_of_birth"),
            "phone_number": customers_record_after_update.get("phone_number"),
            "email": customers_record_after_update.get("email"),
            "account_number": customers_record_after_update.get("account_number"),
            "wallet_balance": customers_record_after_update.get("wallet_balance"),
            "account_status": customers_record_after_update.get("account_status"),
            "created_at": customers_record_after_update.get("created_at"),
            "recorded_at": sysutcdatetime
        }
        columns = ", ".join(event_columns)
        parameters = ", ".join(
            f":{column}" for column in event_columns
        )
        insert_event_data = text(f"""
                        INSERT INTO dbo.CustomerChangeEvents(
                        {columns}
                        )
                        OUTPUT INSERTED.event_id
                        VALUES(
                        {parameters}
                        )
                """)
        event_id = conn.execute(insert_event_data,event_data).scalar_one()

        event_metadata = {
            "customer_id": customers_record_after_update.get("customer_id"),
            "event_id":event_id,
            "event_type": "customer_update",
            "event_sequence": next_event_sequence,
            "effective_at": sysutcdatetime,
            "recorded_at": sysutcdatetime
            }

    if has_changes:
        return event_metadata
    else:
        return None