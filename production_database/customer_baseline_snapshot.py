import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from production_database.production_DB_connection import production_database_engine_connection
import uuid
import datetime as dt
from analytics_database.analytics_DB_connection import analytics_database_engine_connection

analytics_engine = analytics_database_engine_connection()
engine = production_database_engine_connection()
baseline_run_id = uuid.uuid4()
captured_at = dt.datetime.now()


with engine.connect() as connection:

    connection.execute(
        text("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
    )

    connection.commit()

    with connection.begin():

        select_customers = connection.execute(text("""
            SELECT
                c.customer_id,
                CASE
                    WHEN e.event_sequence IS NULL THEN 0
                    ELSE e.event_sequence
                END AS event_sequence,
                c.first_name,
                c.last_name,
                c.email,
                c.phone_number,
                c.date_of_birth,
                c.gender,
                c.account_number,
                c.wallet_balance,
                c.account_status,
                c.created_at
            FROM dbo.Customers AS c
            LEFT JOIN (
                SELECT
                    customer_id,
                    MAX(event_sequence) AS event_sequence
                FROM dbo.CustomerChangeEvents
                GROUP BY customer_id
            ) AS e
                ON c.customer_id = e.customer_id
        """)).mappings().all()

    print(select_customers)   

    print(f"Customers captured: {len(select_customers)}")
    baseline_checkpoints_list =[]
    select_customers_list = []
    for cs in select_customers:
        baseline_checkpoints = {
            "customer_id": cs.get("customer_id"),
            "baseline_event_sequence": cs.get("event_sequence"),
            "baseline_run_id": baseline_run_id,
            "captured_at": captured_at
        }
        select_customers_list.append(dict(cs))
        baseline_checkpoints_list.append(baseline_checkpoints)
checkpoint_columns = [
    "customer_id",
    "baseline_event_sequence",
    "baseline_run_id",
    "captured_at"
]
columns = ", ".join(checkpoint_columns)
parameters = ", ".join(
    f":{column}" for column in checkpoint_columns
)
with analytics_engine.begin() as conn:
    insert_checkpoints = text(f"""
        INSERT INTO gold.customer_baseline_checkpoint(
        {columns}
        )
        VALUES(
        {parameters}
        )
    """)
    conn.execute(insert_checkpoints,baseline_checkpoints_list)