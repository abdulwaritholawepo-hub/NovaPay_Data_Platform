import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from gold_incremental_loader.gold_generic_incremental import gold_generic_incremental_loader
import time
import logging
from config import logging_config
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError, OperationalError, DBAPIError
from gold_incremental_loader.gold_transaction_incremental_loader import gold_transaction_incremental_load
logger = logging.getLogger(__name__)
engine = analytics_database_engine_connection()
logger.info("Analytics database engine created successfully")


transaction_column_order = [
    "transaction_id",
    "sender_customer_key",
    "receiver_customer_key",
    "receiver_merchant_key",
    "date_key",
    "amount",
    "currency",
    "receiver_type",
    "payment_method",
    "transaction_category",
    "transaction_direction",
    "status",
    "reference_number",
    "narration",
    "created_at"
    ]

def transaction_batch_loader():
    with engine.begin() as conn:
        result = conn.execute(text("""
    select dt.transaction_id,
    gsc.customer_key AS sender_customer_key,
    grc.customer_key AS receiver_customer_key,
    grm.merchant_key AS receiver_merchant_key,
    dd.date_key AS date_key,
    dt.amount,
    dt.currency,
    dt.receiver_type,
    dt.payment_method,
    dt.transaction_category,
    dt.transaction_direction,
    dt.status,
    dt.reference_number,
    dt.narration,
    dt.created_at
    from dbo.transactions dt
    left join gold.dim_customer gsc
    on dt.sender_id = gsc.customer_id
    left join gold.dim_customer grc
    on dt.receiver_id = grc.customer_id
    and dt.receiver_type = 'customer' 
    left join gold.dim_merchant grm
    on dt.receiver_id = grm.merchant_id
    and dt.receiver_type = 'merchant' 
    left join gold.dim_date dd
    on cast(dt.created_at as date) = dd.full_date
    """)).mappings().all()
    print("SOURCE TRANSACTIONS:", len(result))
    with engine.begin() as conn:
       transaction_id_list = conn.execute(text("""
            select transaction_id
            from gold.fact_transaction
        """)).scalars().all()
       
    columns = ", ".join(transaction_column_order)
    parameters = ", ".join(
        f":{column}" for column in transaction_column_order
    )

    insert_records = text(f"""
        INSERT INTO gold.fact_transaction
        ( 
        {columns}

        )
        VALUES
        (
            {parameters}   )       
    """)
    
    
    
    batch_size = 5
    start = 0
    batch_no = 0

    insert_batch = None
    maximum_retries = 5
    
    incremental_domain = []
    for r in result:
        if r.get("transaction_id") not in transaction_id_list:
                incremental_domain.append(r)
    domain_length = len(incremental_domain)
    logger.info(
        "Number of transactions to insert: %d",
        len(incremental_domain)
    )
    print("huidincnj",incremental_domain)
    for record in range(start, domain_length, batch_size):
        
        record_batch = incremental_domain[record:record + batch_size]
        batch_no += 1
        logger.info(
        f"Processing batch %d. transactions in batch: %d",
            batch_no,
            len(record_batch)
        )
        for attempts in range(1, maximum_retries+1):
            try:
                with engine.begin() as conn:
                    insert_batch = conn.execute(insert_records, record_batch)
                    logger.info(
                        f"Batch %d inserted successfully. transactions inserted: %d",
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
transaction_batch_loader()  