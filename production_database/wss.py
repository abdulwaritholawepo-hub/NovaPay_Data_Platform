       has_changes = False


       if (
            phone_number != customers_record.get("phone_number")
            or wallet_balance != customers_record.get("wallet_balance")
            or account_status != customers_record.get("account_status")
        ):
            has_changes = True

       
       if has_changes == True:
            sysdatetime = conn.execute(text("""
                select
                    sysdatetime()
            """)).scalar()
            customer_id_rowcount = conn.execute(update_customers,{"customer_id": customer_id,
                                            "phone_number": phone_number,
                                            "wallet_balance": wallet_balance,
                                            "account_status": account_status
                                            }).rowcount
            
            if customer_id_rowcount != 1:
                raise ValueError(
                    f"Customer update failed: expected to update 1 row for "
                    f"customer_id {customer_id}, but {customer_id_rowcount} rows were affected."
                )
            else: 
                print(f"Customer with the id {customer_id} successfully updated")
                event_sequence = conn.execute(text("""
                        SELECT max(event_sequence)
                        FROM dbo.CustomerChangeEvents 
                        WHERE customer_id = :customer_id
                        """), {"customer_id": customer_id}).scalar()
                
                if not event_sequence:
                    event_sequence = 1
                else:
                    event_sequence += 1

                customers_record_after_update = conn.execute(text("""
                SELECT *
                FROM dbo.Customers
                WHERE customer_id = :customer_id
                """), {"customer_id": customer_id}).mappings().one_or_none()
                print(customers_record_after_update)

                if not customers_record_after_update:
                    raise ValueError(
                        f"Customer with ID {customer_id} does not exist")
                
                event_data = {
                 "customer_id": customers_record_after_update.get("customer_id"),
                 "event_type": "customer_update",
                 "event_sequence": event_sequence,
                 "effective_at": sysdatetime,
                 "first_name": customers_record_after_update.get("first_name"),
                 "last_name": customers_record_after_update.get("last_name"),
                 "gender": customers_record_after_update.get("gender"),
                 "date_of_birth": customers_record_after_update.get("date_of_birth"),
                 "phone_number": customers_record_after_update.get("phone_number"),
                 "email": customers_record_after_update.get("email"),
                 "account_number": customers_record_after_update.get("account_number"),
                 "wallet_balance": customers_record_after_update.get("wallet_balance"),
                 "account_status": customers_record_after_update.get("account_status"),
                 "created_at": customers_record_after_update.get("created_at")
                }

                columns = ", ".join(event_snapshot_fields)
                parameters = ", ".join(
                    f":{column}" for column in event_snapshot_fields
                )
                insert_event_data = text(f"""
                        INSERT INTO dbo.CustomerChangeEvents(
                        {columns}
                        )
                        VALUES(
                        {parameters}
                        )
                """)
                conn.execute(insert_event_data,event_data)
       else:
           print(f"No changes detected for customer {customer_id}")
       
       