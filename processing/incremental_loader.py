import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer import transform_customers
from sqlalchemy import text
from sql_server_database.analytics_DB_connection import analytics_database_engine_connection
import logging
from config import logging_config

logger = logging.getLogger(__name__)

def incremental_cutomer_loader():
    transformed_customer_data = transform_customers()
    logger.info(
        "Customer transformation completed. Records received: %d",
        len(transformed_customer_data)
    )
    engine = analytics_database_engine_connection()
    logger.info("Analytics database engine created successfully")

    with engine.begin() as conn:
        logger.info("Fetching maximum customer ID from customers table")
        result = conn.execute(
                text("""
                    select max(customer_id)
                    from customers
        """))
        max_customer_id = result.scalar()
        logger.info(
            "Maximum existing customer ID retrieved: %s",
            max_customer_id
        )
        new_customers_list = []

        for customer in transformed_customer_data:
            customer_id = customer.get("customer_id")
        if customer_id > max_customer_id:
            new_customers_list.append(customer)
            logger.info(
                "New customer identified: %s",
                customer_id
            )
        logger.info(
            "New customer identification completed. New customers found: %d",
            len(new_customers_list)
        )
    return new_customers_list