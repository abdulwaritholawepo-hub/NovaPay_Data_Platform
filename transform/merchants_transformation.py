import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.merchants_response_validator import merchants_response_validator
from transform.merchant_transformer_helper import (
    MERCHANT_COLUMN_ORDER,
    INVALID_MERCHANT_ID,
    INVALID_ACCOUNT_NUMBER,
    cleaning_key_value,
    generate_merchant_code,
    transform_email,
    transform_segment,
    transform_location,
    transform_is_active,
    transform_merchant_tenure
)

import logging
from config import logging_config
logger = logging.getLogger(__name__)

def transform_merchants():
    transformed_merchants_list = []
    seen_merchant_ids = set()
    seen_account_numbers = set()
    seen_emails = set()

    total_records = 0
    successful_records = 0
    skipped_records = 0
    duplicate_merchant_ids = 0
    duplicate_account_numbers = 0
    duplicate_emails = 0

    logger.info("START | Merchant transformation started")

    logger.info("VALIDATION | Starting merchant response validation")
    validated_merchants = merchants_response_validator()
    logger.info(
        "VALIDATION | Merchant response validation completed | records=%d",
        len(validated_merchants)
    )
    
    
    
    for merchants in validated_merchants:
        total_records += 1

        logger.info(
            "RECORD TRANSFORMATION | Transforming record=%d",
            total_records
        )

        merchants_dict = {
        key: cleaning_key_value(key=key,value=value)
        for key, value in merchants.items()
        
        }
        merchant_id = merchants_dict["merchant_id"]
        account_number = merchants_dict["account_number"]
        email = merchants_dict["email"]

        if merchant_id == INVALID_MERCHANT_ID or merchant_id is None:
            logger.warning(
                "VALIDATION | Skipping record=%d | invalid/missing merchant_id",
                total_records
            )
            skipped_records += 1
            continue


        if merchant_id in seen_merchant_ids:
            duplicate_merchant_ids += 1
            skipped_records += 1
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate merchant_id=%s",
                total_records,
                merchant_id
            )
            continue

        if account_number == INVALID_ACCOUNT_NUMBER or account_number is None:
            logger.warning(
                "VALIDATION | Skipping record=%d | invalid/missing account_number",
                total_records
            )
            skipped_records += 1
            continue

        if account_number in seen_account_numbers:
            duplicate_account_numbers += 1
            skipped_records += 1
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate account_number",
                total_records
            )
            continue
        seen_merchant_ids.add(merchant_id)
        seen_account_numbers.add(account_number)
        merchants_dict["merchant_code"] = generate_merchant_code(merchant_id)

        email, email_domain, duplicate_email = transform_email(
            email,
            seen_emails
        )

        merchants_dict["email"] = email
        merchants_dict["email_domain"] = email_domain
        merchants_dict["duplicate_email"] = duplicate_email

        if duplicate_email == "Duplicate":
            duplicate_emails += 1
            logger.warning(
                "DUPLICATE DETECTION | Duplicate email detected | record=%d",
                total_records
            ) 


        category= merchants_dict["category"]
        merchants_dict["segment"] = transform_segment(category)


        city = merchants_dict["city"]
        state = merchants_dict["state"]
        merchants_dict["location"] = transform_location(city,state)


        merchant_status = merchants_dict["merchant_status"]
        merchants_dict["is_active"] = transform_is_active(merchant_status)


        created_at = merchants_dict["created_at"]
        merchant_tenure_days, tenure_category = transform_merchant_tenure(
            created_at
        )
        merchants_dict["merchant_tenure_days"] = merchant_tenure_days
        merchants_dict["tenure_category"] = tenure_category

        logger.info(
            "DERIVATION | Derived fields completed | record=%d",
            total_records
        )

        ordered_merchants = {
            column: merchants_dict.get(column)
            for column in MERCHANT_COLUMN_ORDER
            }

        successful_records += 1


        logger.info(
            "SUCCESS | Merchant transformation completed | record=%d | merchant_id=%s",
            total_records,
            merchant_id
        )
                            

            
        transformed_merchants_list.append(ordered_merchants)

    logger.info(
        "SUMMARY | Transformation completed | "
        "total=%d | successful=%d | skipped=%d | "
        "duplicate_merchant_ids=%d | duplicate_account_numbers=%d | "
        "duplicate_emails=%d",
        total_records,
        successful_records,
        skipped_records,
        duplicate_merchant_ids,
        duplicate_account_numbers,
        duplicate_emails
    )

    return transformed_merchants_list
transform_merchants()
