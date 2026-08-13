from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer import transform_customers
from transform.transform_helpers import COLUMN_ORDER
from sql_server_database.analytics_DB_connection import analytics_database_engine_connection

engine = analytics_database_engine_connection()

columns = ", ".join(COLUMN_ORDER)
parameters = ", ".join(f":{column}" for column in COLUMN_ORDER)
insert_customers = text(f"""
    INSERT INTO customers({columns})
    VALUES({parameters})
    """)

transformed_customer_data = transform_customers()
customers = transformed_customer_data
batch_size = 5
start = 0
batch_no = 0
customer_length = len(customers)

for customer in range(start, customer_length, batch_size):
    customer_batch = customers[customer:customer + batch_size]
    batch_no += 1
    print(f"batch {batch_no}")

    with engine.begin() as conn:
        conn.execute(insert_customers, customer_batch)
        print("cutomer data inserted succesfully")
