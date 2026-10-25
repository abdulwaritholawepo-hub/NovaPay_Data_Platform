import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from production_database.production_DB_connection import production_database_engine_connection
from datetime import date, datetime
from decimal import Decimal
engine = production_database_engine_connection()

with engine.begin() as conn:
   event_metadata_keys = [
       "event_id",
       "event_type",
       "event_sequence",
       "effective_at"
   ]

   customer_snapshot_keys = [
       "customer_id",
       "first_name",
       "last_name",
       "gender",
       "date_of_birth",
       "phone_number",
       "email",
       "wallet_balance",
       "account_number",
       "account_status",
       "created_at"
   ]
   retrieved_customers = conn.execute(text("""
        select customer_id, event_id, event_type,
        event_sequence, effective_at,
        first_name, last_name, gender, 
        date_of_birth, phone_number,email,
        wallet_balance,account_status,
        created_at, account_number
        from dbo.CustomerChangeEvents a
        where a.processed_at is null and NOT EXISTS(
        select 1
        from dbo.CustomerChangeEvents b
        where a.customer_id = b.customer_id and a.event_sequence > b.event_sequence and b.processed_at is null
        
        )
        order by customer_id, event_sequence
    """)).mappings().all()
   batch_size = 5
   batch_len = len(retrieved_customers)
   start = 0
   batch_no = 0
   customer_snapshot_list = []
   event_metadata_list = []
   event_record_list = []
   if retrieved_customers is not None and retrieved_customers:
       for customers in range(start, batch_len, batch_size):
           batch_no += 1
           batch_retrieved_customers = retrieved_customers[customers:customers + batch_size]

           for one_batch in batch_retrieved_customers:
               event_id_batch = one_batch.get('event_id')
               customer_id_batch = one_batch.get('customer_id')
               event_sequence_batch = one_batch.get('event_sequence')
               print(
                   f"event_id {event_id_batch}, customer_id {customer_id_batch}, event_sequence {event_sequence_batch} for batch {batch_no}")
               customer_snapshot = {
                   "customer_id": one_batch.get("customer_id"),
                   "first_name": one_batch.get("first_name"),
                   "last_name": one_batch.get("last_name"),
                   "gender": one_batch.get("gender"),
                   "date_of_birth": one_batch.get("date_of_birth"),
                   "phone_number": one_batch.get("phone_number"),
                   "email": one_batch.get("email"),
                   "wallet_balance": one_batch.get("wallet_balance"),
                   "account_number": one_batch.get("account_number"),
                   "account_status": one_batch.get("account_status"),
                   "created_at": one_batch.get("created_at")
               }
               customer_snapshot_list.append(customer_snapshot)
               event_metadata = {
                   "event_id": one_batch.get("event_id"),
                   "event_type": one_batch.get("event_type"),
                   "event_sequence": one_batch.get("event_sequence"),
                   "effective_at": one_batch.get("effective_at")
               }
               event_metadata_list.append(event_metadata)
               event_record = {
                   "customer_snapshot": customer_snapshot,
                   "event_metadata": event_metadata
               }
               event_record_list.append(event_record)

   else:
       print("batch is empty")
event_metadata_len = len(event_metadata_list)
customer_snapshot_len = len(customer_snapshot_list)
if event_metadata_len == customer_snapshot_len:
    print("equal")
else:
    print("not equal")
validated_customer_snapshot = []
invalid_customer_snapshot = []


text_fields = [
    "first_name",
    "last_name",
    "gender",
    "phone_number",
    "email",
    "account_number",
    "account_status"
]

fully_validated_event_records = []
invalid_event_records = []

for snapshot in event_record_list:
    is_invalid = False
    customer_snapshot = snapshot.get("customer_snapshot")
    event_metadata = snapshot.get("event_metadata")

    for key in customer_snapshot_keys:
      value = customer_snapshot.get(key)

      if value is None:
         is_invalid = True
         break

      if key in text_fields:
         if not isinstance(value, str) or not value.strip():
             is_invalid = True
             break

      elif key == "customer_id":
         if not isinstance(value, int) or isinstance(value, bool):
             is_invalid = True
             break

      elif key == "wallet_balance":
         if not isinstance(value, (int, float, Decimal)) or isinstance(value, bool):
             is_invalid = True
             break

      elif key == "date_of_birth":
         if not isinstance(value, (date, datetime)):
             is_invalid = True
             break
      elif key == "created_at":
          if not isinstance(value, (date, datetime)):
              is_invalid = True
              break

    for key in event_metadata_keys:
        value = event_metadata.get(key)
        if value is None:
            is_invalid = True
            break
        if key == "event_id":
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                is_invalid = True
                break
        elif key == "event_type":
            if not isinstance(value, str) or not value.strip():
                is_invalid = True
                break
        elif key == "event_sequence":
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                is_invalid = True
                break
        elif key == "effective_at":
            if not isinstance(value, (date, datetime)):
                is_invalid = True
                break

    if is_invalid:
        invalid_event_records.append({"customer_snapshot": customer_snapshot,
                                      "event_metadata": event_metadata})

    else:
        fully_validated_event_records.append({"customer_snapshot": customer_snapshot,
                                      "event_metadata": event_metadata})

print(f"Total event records retrived {len(event_record_list)}")
print(f"fully validated records {len(fully_validated_event_records)}")
print(f"invalid records {len(invalid_event_records)}")
      