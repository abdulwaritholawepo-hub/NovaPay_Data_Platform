
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.transaction_response_validator import transaction_response_validator
from transform.transaction_transformer_helper import( 
    TRANSACTION_COLUMN_ORDER, cleaning_transactions_value,
    INVALID_VALUES,
)
import logging
from config import logging_config

logger = logging.getLogger(__name__)
def transform_transactions():
    total_records = 0
    successful_records = 0
    skipped_records = 0
    duplicate_transaction_ids = 0
    duplicate_reference_numbers = 0
    logger.info("START | Transaction transformation started")

    logger.info("VALIDATION | Starting transaction response validation")
    validated_transactions = transaction_response_validator()

    logger.info(
        "VALIDATION | Transaction response validation completed | records=%d",
        len(validated_transactions)
    )
    seen_transaction_id = set()
    seen_reference_number = set()
    valid_transactions_list = []
    for transaction in validated_transactions:
        total_records += 1
        logger.info(
            "RECORD TRANSFORMATION | Transforming record=%d",
            total_records
        )
        
        transaction_valid = True
        transactions_dict = {
        key: cleaning_transactions_value(key=key,value=value)
        for key, value in transaction.items()
        }
        for k, v in transactions_dict.items():
            if v is None or v in INVALID_VALUES:
                skipped_records += 1
                logger.warning(
                    "VALIDATION | Skipping record=%d | invalid/missing transaction data",
                    total_records
                )
                transaction_valid = False
                break
        if transaction_valid is False:
            continue

        transaction_id = transactions_dict["transaction_id"] 

        if transaction_id not in seen_transaction_id:
            seen_transaction_id.add(transaction_id)
        else:
            duplicate_transaction_ids += 1
            skipped_records += 1

            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate transaction_id=%s",
                total_records,
                transaction_id
            )
            continue
        reference_number = transactions_dict["reference_number"]
        if reference_number not in seen_reference_number:
            seen_reference_number.add(reference_number)
        else:
            duplicate_reference_numbers += 1
            skipped_records += 1
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate reference_number=%s",
                total_records,
                reference_number
            )
            continue

        ordered_transactions = {
            column: transactions_dict.get(column)
            for column in TRANSACTION_COLUMN_ORDER
            }
        valid_transactions_list.append(ordered_transactions)
        successful_records += 1

        logger.info(
            "SUCCESS | Transaction transformation completed | record=%d | transaction_id=%s",
            total_records,
            transaction_id
        )
    logger.info(
        "SUMMARY | Transformation completed | "
        "total=%d | successful=%d | skipped=%d | "
        "duplicate_transaction_ids=%d | duplicate_reference_numbers=%d",
        total_records,
        successful_records,
        skipped_records,
        duplicate_transaction_ids,
        duplicate_reference_numbers
    )
    return valid_transactions_list