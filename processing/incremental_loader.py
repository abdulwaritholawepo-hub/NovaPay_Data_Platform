import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
import logging
from config import logging_config

logger = logging.getLogger(__name__)

def generic_incremental_loader(transformed_data, domain):
    DOMAIN_CONFIG = {
        "customer": {
            "table": "customers",
            "id_column": "customer_id"
        },
        "merchant": {
            "table": "merchants",
            "id_column": "merchant_id"
        },
        "transaction": {
            "table": "transactions",
            "id_column": "transaction_id"
        }
    }
    config = DOMAIN_CONFIG[domain]
    table_name = config["table"]
    id_column = config["id_column"]
    logger.info(
        f"{config} transformation completed. Records received: %d",
        len(transformed_data)
    )
    engine = analytics_database_engine_connection()
    logger.info("Analytics database engine created successfully")

    with engine.begin() as conn:
        logger.info(f"Fetching maximum {config} ID from {table_name}")
        result = conn.execute(
                text(f"""
                    select max({id_column})
                    from {table_name}
        """))
        max_id = result.scalar()
        logger.info(
            f"Maximum existing {config} ID retrieved: %s",
            max_id
        )
        new_list = []

        for record in transformed_data:
            record_id = record.get(id_column)
            if max_id is None or record_id > max_id:
                new_list.append(record)
                logger.info(
                    f"New {id_column} identified: %s",
                    record_id
                )
        logger.info(
            f"New {config} identification completed. New {table_name} found: %d",
            len(new_list)
        )
    return new_list