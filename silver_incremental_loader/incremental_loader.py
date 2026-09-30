import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
import logging
from config import logging_config

logger = logging.getLogger(__name__)
DOMAIN_CONFIG = {
    "customer": {
        "table": "Customers",
        "id_column": "customer_id"
    },
    "merchant": {
        "table": "Merchants",
        "id_column": "merchant_id"
    },
    "transaction": {
        "table": "Transactions",
        "id_column": "transaction_id"
    }
}
def generic_incremental_loader(transformed_data, domain, schema):
    
    config = DOMAIN_CONFIG[domain]
    table_name = config["table"]
    id_column = config["id_column"]
    logger.info(
        f"{table_name} transformation completed. Records received: %d",
        len(transformed_data)
    )
    engine = analytics_database_engine_connection()
    logger.info("Analytics database engine created successfully")

    with engine.begin() as conn:
        logger.info(f"Fetching maximum {id_column}  from {table_name}")
        result = conn.execute(
                text(f"""
                    select max({id_column})
                    from {schema}{table_name}
        """))
        max_id= result.scalar()
        logger.info(
            f"Maximum existing {domain} {id_column} retrieved: %s",
            max_id
        )
        new_list = []

        for record in transformed_data:
            record_id_column = record.get(id_column)
            if max_id is None or record_id_column > max_id:
                new_list.append(record)
                logger.info(
                    f"New {domain} identified with {id_column}: %s",
                    record_id_column
                )
        logger.info(
            f"New {domain} identification completed. New {table_name} found: %d",
            len(new_list)
        )
    return new_list