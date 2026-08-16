from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.transform_helpers import COLUMN_ORDER
from sql_server_database.analytics_DB_connection import analytics_database_engine_connection
from processing.incremental_loader import new_customers_list
import time
from transform.customer_transformer import transform_customers
engine = analytics_database_engine_connection()

columns = ", ".join(COLUMN_ORDER)
parameters = ", ".join(f":{column}" for column in COLUMN_ORDER)
insert_customers = text(f"""
    INSERT INTO customers({columns})
    VALUES({parameters})
    """)

transformed_customer_data = transform_customers()
customers = new_customers_list
print("Number of customers:", len(customers))
print("Customers:", customers)
batch_size = 5
start = 0
batch_no = 0

maximum_retries = 5
customer_length = len(customers)

for customer in range(start, customer_length, batch_size):
    customer_batch = customers[customer:customer + batch_size]
    batch_no += 1
    print(f"batch {batch_no}")
    for attempts in range(1,maximum_retries+1):
        try:
            with engine.begin() as conn:
                insert = conn.execute(insert_customers, customer_batch)
                print("cutomer data inserted succesfully")
                break
        except SQLAlchemyError as error:
            if attempts == maximum_retries:
                print("maximum retries reached")
                raise error
            else:
                wait_time = attempts**2
                print(f"retrying in {wait_time} seconds")
                time.sleep(wait_time)


