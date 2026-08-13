from sqlalchemy import text 

from sql_server_database.production_DB_connection import production_database_engine_connection

def get_customers_records():
    engine = production_database_engine_connection()
    customers_list = []
    with engine.begin() as conn:
        customers = conn.execute(text(
            """
            SELECT *
            FROM customers
            """
        ))
        for customer in customers.mappings():
            customers_list.append(dict(customer))
    return customers_list


