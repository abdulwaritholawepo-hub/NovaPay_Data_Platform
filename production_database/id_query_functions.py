from sqlalchemy import text

from production_database.production_DB_connection import production_database_engine_connection


def get_customer_ids(conn):
    customer_ids = conn.execute(text(
        """
        SELECT customer_id
        FROM customers
        """)).scalars().all()
    return customer_ids


def get_merchant_ids(conn):
    merchant_ids = conn.execute(text(
        """
        SELECT merchant_id
        FROM merchants
        """)).scalars().all()
    return merchant_ids
