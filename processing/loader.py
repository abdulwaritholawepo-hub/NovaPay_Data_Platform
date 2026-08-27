from sqlalchemy.exc import SQLAlchemyError, ProgrammingError,OperationalError,DBAPIError
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.transform_helpers import COLUMN_ORDER
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from processing.incremental_loader import incremental_cutomer_loader
import time
import logging
from config import logging_config

logger = logging.getLogger(__name__)
engine = analytics_database_engine_connection()
logger.info("Analytics database engine created successfully")

def batch_loader():

    columns = ", ".join(COLUMN_ORDER)
    parameters = ", ".join(f":{column}" for column in COLUMN_ORDER)
    insert_customers = text(f"""
        INSERT INTO customers({columns})
        VALUES({parameters})
        """)

    customers = incremental_cutomer_loader()
    logger.info(
        "Number of customers to insert: %d",
        len(customers)
    )
    batch_size = 5
    start = 0
    batch_no = 0

    insert = None
    maximum_retries = 5
    customer_length = len(customers)

    for customer in range(start, customer_length, batch_size):
        customer_batch = customers[customer:customer + batch_size]
        batch_no += 1
        logger.info(
            "Processing batch %d. Customers in batch: %d",
            batch_no,
            len(customer_batch)
        )
        for attempts in range(1, maximum_retries+1):
            try:
                with engine.begin() as conn:
                    insert = conn.execute(insert_customers, customer_batch)
                    logger.info(
                        "Batch %d inserted successfully. Customers inserted: %d",
                        batch_no,
                        len(customer_batch)
                    )
                    break
            except SQLAlchemyError as error:
                error_type = type(error).__name__
                logger.error(
                    "Batch %d failed with %s: %s",
                    batch_no,
                    error_type,
                    error
                )
                if isinstance(error, ProgrammingError):
                    logger.error(
                        "ProgrammingError encountered in batch %d. "
                        "Batch will not be retried.",
                        batch_no
                    )
                    break
                elif isinstance(error, OperationalError):
                    if attempts == maximum_retries:
                        logger.error(
                            "Maximum retries reached for batch %d. Raising the database error.",
                            batch_no
                        )
                        raise error
                    else:
                        wait_time = attempts**2
                        logger.warning(
                            "Batch %d failed. Retrying in %d seconds. Attempt %d of %d.",
                            batch_no,
                            wait_time,
                            attempts,
                            maximum_retries
                        )
                        time.sleep(wait_time)
                elif isinstance(error, DBAPIError):
                    if attempts == maximum_retries:
                        logger.error(
                            "Maximum retries reached for batch %d. Raising the database error.",
                            batch_no
                        )
                        raise error
                    else:
                        wait_time = attempts**2
                        logger.warning(
                            "Batch %d failed. Retrying in %d seconds. Attempt %d of %d.",
                            batch_no,
                            wait_time,
                            attempts,
                            maximum_retries
                        )
                        time.sleep(wait_time)
                else: 
                    logger.error(
                        "Unhandled SQLAlchemy error encountered in batch %d. "
                        "Batch will not be retried.",
                        batch_no
                    )
                    break
    return insert