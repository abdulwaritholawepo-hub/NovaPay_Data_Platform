import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError,OperationalError,DBAPIError
from sqlalchemy import text
from transform.customer_transformer_helper import COLUMN_ORDER
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from processing.incremental_loader import generic_incremental_loader
import time
import logging
from config import logging_config

logger = logging.getLogger(__name__)
engine = analytics_database_engine_connection()
logger.info("Analytics database engine created successfully")

def generic_batch_loader(domain,domain_column_order,batch_domain, transformed_data, ):

    columns = ", ".join(domain_column_order)
    parameters = ", ".join(f":{column}" for column in domain_column_order)
    insert_records = text(f"""
        INSERT INTO {batch_domain} ({columns})
        VALUES({parameters})
        """)

    incremental_domain = generic_incremental_loader(domain=domain,transformed_data=transformed_data)
    logger.info(
        f"Number of {batch_domain} to insert: %d",
        len(incremental_domain)
    )
    batch_size = 5
    start = 0
    batch_no = 0

    insert_batch = None
    maximum_retries = 5
    domain_length = len(incremental_domain)

    for record in range(start, domain_length, batch_size):
        record_batch = incremental_domain[record:record + batch_size]
        batch_no += 1
        logger.info(
            f"Processing batch %d. {batch_domain} in batch: %d",
            batch_no,
            len(record_batch)
        )
        for attempts in range(1, maximum_retries+1):
            try:
                with engine.begin() as conn:
                    insert_batch = conn.execute(insert_records, record_batch)
                    logger.info(
                        f"Batch %d inserted successfully. {batch_domain} inserted: %d",
                        batch_no,
                        len(record_batch)
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
    return insert_batch
