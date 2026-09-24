import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logging_config
import logging
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from sqlalchemy import text


logger = logging.getLogger(__name__)
DOMAIN_CONFIG = {
    "customer": {
        "table": "dim_customer",
        "created_at_column": "created_at"
    },
    "merchant": {
        "table": "dim_merchants",
        "created_at_column": "created_at"
    },
    "transaction": {
        "table": "fact_transactions",
        "created_at_column": "created_at"
    },
    "date": {
        "table": "dim_date",
        "created_at_column": "created_at"
    }
}


def gold_generic_incremental_loader(transformed_data, domain, schema):

    config = DOMAIN_CONFIG[domain]
    table_name = config["table"]
    created_at = config["created_at_column"]
    logger.info(
        f"{table_name} transformation completed. Records received: %d",
        len(transformed_data)
    )
    engine = analytics_database_engine_connection()
    logger.info("Analytics database engine created successfully")

    with engine.begin() as conn:
        logger.info(f"Fetching maximum {created_at}  from {table_name}")
        result = conn.execute(
            text(f"""
                    select max({created_at})
                    from {schema}{table_name}
        """))
        max_created_at = result.scalar()
        logger.info(
            f"Maximum existing {domain} created_at retrieved: %s",
            max_created_at
        )
        new_list = []

        for record in transformed_data:
            
            record_created_at = record.get(created_at)
            if max_created_at is None or record_created_at > max_created_at:
                new_list.append(record)
                logger.info(
                    f"New {domain} identified with created_at: %s",
                    record_created_at
                )
        logger.info(
            f"New {domain} identification completed. New {table_name} found: %d",
            len(new_list)
        )
    return new_list
