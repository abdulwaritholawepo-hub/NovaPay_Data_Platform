import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from production_database.production_DB_connection import production_database_engine_connection
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from sqlalchemy import text


def initialize_customer_incremental_checkpoints(
    production_engine,
    analytics_engine,
    before_insert=None
):
  
    with production_engine.connect() as production_conn:
        dbo_customers = production_conn.execute(
            text("""
                select customer_id
                from dbo.Customers 
            """)).mappings().all()
        customer_events = production_conn.execute(
            text("""
                select customer_id, event_sequence
                from dbo.CustomerChangeEvents
                where event_type = 'customer_insert' and event_sequence = 1
                
            """)).mappings().all()
        customer_set = set()
        events_set = set()
        for production_customers in dbo_customers:
            customer_set.add(production_customers.get("customer_id"))
            
        for events in customer_events:
            events_set.add(events.get("customer_id"))

        missing_events = customer_set.difference(events_set)
        if missing_events:
            raise ValueError(f"customer id {missing_events} missing")


    with analytics_engine.begin() as analytics_conn:
        baseline_customers = analytics_conn.execute(
            text("""
                select checkpoints.customer_id, checkpoints.baseline_event_sequence
                from gold.customer_baseline_run as run
                inner join gold.customer_baseline_control as control
                on run.baseline_run_id = control.active_baseline_run_id
                inner join gold.customer_baseline_checkpoint as checkpoints
                on checkpoints.baseline_run_id = control.active_baseline_run_id
                where run.status = 'completed'
            
            """)).mappings().all()
        existing_checkpoints = analytics_conn.execute(
            text("""
                select customer_id, last_event_sequence
                from gold.customer_incremental_checkpoint
            
            """)).mappings().all()
        baseline_customer_set = set()
        existing_checkpoint_set = set()
        for baseline_customer in baseline_customers:
            baseline_customer_set.add(baseline_customer.get("customer_id"))
        for checkpoint in existing_checkpoints:
            existing_checkpoint_set.add(checkpoint.get("customer_id"))
        customers_without_checkpoints =  customer_set.difference(existing_checkpoint_set)
        missing_baseline_customers = customers_without_checkpoints.intersection(baseline_customer_set)
        missing_post_baseline_customers = customers_without_checkpoints.difference(baseline_customer_set)
        invalid_baseline_customers = baseline_customer_set.difference(customer_set)
        if invalid_baseline_customers:
            raise ValueError(f"customer id {invalid_baseline_customers} missing")
        checkpoints_to_initialize = {}
        
        for missing_baseline in missing_baseline_customers:
            checkpoints_to_initialize[missing_baseline] = 1
        for missing_post in missing_post_baseline_customers:
            checkpoints_to_initialize[missing_post] = 0
        checkpoint_records = []
        for key,value in checkpoints_to_initialize.items():
            checkpoint_records.append({"customer_id": key,
                         "last_event_sequence": value})
        if checkpoint_records:
            insert_query = text("""
                            INSERT INTO gold.customer_incremental_checkpoint
                            (customer_id, last_event_sequence)
                        SELECT
                            :customer_id,
                            :last_event_sequence

                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM gold.customer_incremental_checkpoint WITH (UPDLOCK, HOLDLOCK)
                            WHERE customer_id = :customer_id
                        ) """)
            if before_insert is not None:
                before_insert()
            analytics_conn.execute(insert_query,checkpoint_records)
if __name__ == "__main__":
    p_engine = production_database_engine_connection()
    a_engine = analytics_database_engine_connection()

    try:
        initialize_customer_incremental_checkpoints(
            production_engine=p_engine,
            analytics_engine=a_engine
        )
    finally:
        p_engine.dispose()
        a_engine.dispose()