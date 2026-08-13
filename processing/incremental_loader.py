import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer import transform_customers
from sqlalchemy import text
from sql_server_database.analytics_DB_connection import analytics_database_engine_connection
transformed_customer_data = transform_customers()
engine = analytics_database_engine_connection()

with engine.begin() as conn:
   result = conn.execute(
        text("""
            select max(customer_id)
            from customers
"""))
   max_customer_id = result.scalar()
   print(max_customer_id)
new_customers_list = []
for customer in transformed_customer_data:
   customer_id = customer.get("customer_id")
   if customer_id > max_customer_id:
    new_customers_list.append(customer)
    print(customer.get("customer_id"))