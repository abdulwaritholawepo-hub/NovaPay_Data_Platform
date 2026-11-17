import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from production_database.production_DB_connection import production_database_engine_connection
from datetime import date, datetime
from decimal import Decimal
engine = production_database_engine_connection()
def retrieve_customer_incremental_checkpoints(analytics_engine ):
    with analytics_engine.begin() as analytics_conn:
        retrieved_checkpoints = analytics_conn.execute(
            text("""
                    select customer_id, last_event_sequence
                    from gold.customer_incremental_checkpoint
                    order by customer_id, last_event_sequence 
                
                """)).mappings().all()
        
    if retrieved_checkpoints:
        return retrieved_checkpoints

    else:
        return []


def pending_customer_retrieval(production_engine):
    retrieved_checkpoints = retrieve_customer_incremental_checkpoints(
        analytics_database_engine_connection())
    unprocessed_event_list = []
    if retrieved_checkpoints:
        with production_engine.begin() as production_conn:
            for checkpoint in retrieved_checkpoints:
        
            
                unprocessed_event = production_conn.execute(
                        text("""
                                select customer_id, event_id, event_type,
                                event_sequence, effective_at, recorded_at,
                                first_name, last_name, gender, 
                                date_of_birth, phone_number,email,
                                wallet_balance,account_status,
                                created_at, account_number
                                from dbo.CustomerChangeEvents
                                where customer_id = :customer_id and 
                                event_sequence > :last_event_sequence
                                order by customer_id, event_sequence
                            """),{"customer_id": checkpoint.get("customer_id"),
                                 "last_event_sequence": checkpoint.get(
                                     "last_event_sequence")}
                                 ).mappings().all()
                for unprocessed in unprocessed_event:
                    unprocessed_event_list.append(unprocessed)
    if unprocessed_event_list:
        return unprocessed_event_list
    else:
        return []

event_metadata_keys = [
    "event_id",
    "event_type",
    "event_sequence",
    "effective_at",
    "recorded_at"
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
pending_customer = pending_customer_retrieval(
    production_database_engine_connection())
batch_size = 5
batch_len = len(pending_customer)
start = 0
batch_no = 0
customer_snapshot_list = []
event_metadata_list = []
event_record_list = []
if pending_customer is not None and pending_customer:
    for customers in range(start, batch_len, batch_size):
        batch_no += 1
        batch_retrieved_customers = pending_customer[customers:customers + batch_size]

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
                "effective_at": one_batch.get("effective_at"),
                "recorded_at":one_batch.get("recorded_at")
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

retrieved_checkpoints = retrieve_customer_incremental_checkpoints(
    analytics_database_engine_connection())


    


text_fields = [
    "first_name",
    "last_name",
    "gender",
    "phone_number",
    "email",
    "account_number",
    "account_status"
]


event_sequence_dict = {}
gap_ids = set()
for snapshot in event_record_list:
    is_invalid = False
    customer_snapshot = snapshot.get("customer_snapshot")
    event_metadata = snapshot.get("event_metadata")
    for checkpoints in retrieved_checkpoints:
        event_sequence = event_metadata.get("event_sequence")
        last_event_sequence = checkpoints.get("last_event_sequence")
        expected_number = last_event_sequence + 1
    
        if checkpoints.get("customer_id") == customer_snapshot.get("customer_id"):
            if customer_snapshot.get("customer_id") not in event_sequence_dict:
                event_sequence_dict[customer_snapshot.get("customer_id")] = expected_number
            dict_expected_number = event_sequence_dict.get(
                    customer_snapshot.get("customer_id"))
            if dict_expected_number != event_sequence:
                is_invalid = True
                gap_ids.add(customer_snapshot.get("customer_id"))
                break
            else:
                event_sequence_dict[customer_snapshot.get("customer_id")] += 1
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
         if not isinstance(value, date):
             is_invalid = True
             break
      elif key == "created_at":
          if not isinstance(value, datetime):
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
            if not  isinstance(value, str):
                is_invalid = True
                break
            value = value.lower()
            if value !=  "customer_insert" and value != "customer_update":
                is_invalid = True
                break
        elif key == "event_sequence":
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                is_invalid = True
                break
        elif key == "effective_at":
            if not isinstance(value, datetime):
                is_invalid = True
                break
        elif key == "recorded_at":
            if not isinstance(value, datetime):
                is_invalid = True
                break

    if is_invalid or customer_snapshot.get("customer_id") in gap_ids:
        invalid_event_records.append({"customer_snapshot": customer_snapshot,
                                      "event_metadata": event_metadata})

    else:
        fully_validated_event_records.append({"customer_snapshot": customer_snapshot,
                                      "event_metadata": event_metadata})

print(f"Total event records retrived {len(event_record_list)}")
print(f"fully validated records {len(fully_validated_event_records)}")
print(f"invalid records {len(invalid_event_records)}")
      