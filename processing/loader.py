import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer import transform_customers
from transform.transform_helpers import COLUMN_ORDER
from sqlalchemy import text
from sql_server_database.analytics_DB_connection import analytics_database_engine_connection

engine = analytics_database_engine_connection()
transformed_customer_data = transform_customers()

columns = ", ".join(COLUMN_ORDER)
parameters = ", ".join(f":{column}" for column in COLUMN_ORDER)
insert_customers = text(f"""
INSERT INTO customers({columns})
VALUES({parameters})
""")

with engine.begin() as conn:
    conn.execute(insert_customers, transformed_customer_data)
    print("cutomer data inserted succesfully")