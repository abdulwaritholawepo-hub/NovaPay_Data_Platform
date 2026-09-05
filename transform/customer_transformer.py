import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer_helper import (
    calculate_account_tenure,
    get_wallet_segment,
    get_risk_details,
    get_customer_initials,
    get_full_name,
    get_customer_age_details,
    get_email_domain,
    clean_transform_value,
    COLUMN_ORDER,
    MISSING_VALUES,
    INVALID_CUSTOMER_ID,
    INVALID_ACCOUNT_NUMBER

)
from extract.customer_response_validator import customer_response_validator
import logging
from config import logging_config

logger = logging.getLogger(__name__)



def transform_customers():
    logger.info("START | Customer transformation started")

    transform_customers_list = []
    seen_customer_ids = set()
    seen_emails = set()
    seen_account_numbers = set()
    total_records = 0


    successful_records = 0
    skipped_records = 0
    duplicate_customer_ids = 0
    duplicate_account_numbers = 0
    duplicate_emails = 0
    logger.info("VALIDATION | Starting customer response validation")


    validated_customers = customer_response_validator()

    logger.info(
        "VALIDATION | Customer response validation completed | records=%d",
        len(validated_customers)
    )

    for customer in validated_customers:
        total_records += 1

        logger.info(
            "RECORD TRANSFORMATION | Transforming record=%d",
            total_records
        )
        customer_dict = {
            key: clean_transform_value(
                key=key,
                val=value,
                missing_values=MISSING_VALUES,
            )
            for key, value in customer.items()
        }

        customer_id = customer_dict["customer_id"]
        if customer_id == INVALID_CUSTOMER_ID or customer_id is None:
            logger.warning(
                "VALIDATION | Skipping record=%d | invalid/missing customer_id",
                total_records
            )
            skipped_records += 1
            continue

        if customer_id in seen_customer_ids:
            duplicate_customer_ids += 1
            skipped_records += 1

            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate customer_id=%s",
                total_records,
                customer_id
            )
            continue
        seen_customer_ids.add(customer_id)


        account_number = customer_dict["account_number"]
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
                "DUPLICATE DETECTION | Skipping record=%d | duplicate account_number=%s",
                total_records,
                account_number
            )
            continue
        seen_account_numbers.add(account_number)


        customer_dict["full_name"] = get_full_name(
            customer_dict["first_name"],customer_dict["last_name"])

        customer_dict["customer_initials"] = get_customer_initials(
        customer_dict["first_name"],customer_dict["last_name"])

        
        email = customer_dict["email"]
        if email in seen_emails:
            duplicate_emails += 1

            logger.warning(
                "DUPLICATE DETECTION | Duplicate email=%s | customer_id=%s",
                email,
                customer_id
            )

            customer_dict["duplicate_email"] = "Duplicate"


        else:
            seen_emails.add(email)
            customer_dict["duplicate_email"] = "Unique"

        customer_dict["email_domain"] = get_email_domain(
            customer_dict["email"]
        )

        (
            customer_dict["age"],
            customer_dict["is_adult"],
            customer_dict["eligibility"],
            customer_dict["customer_segment"],
        ) = get_customer_age_details(
            customer_dict["date_of_birth"]
        )

        (
            customer_dict["account_tenure_days"],
            customer_dict["customer_lifetime_stage"]
        ) = calculate_account_tenure(
            customer_dict["created_at"],
            customer_dict["date_of_birth"],
        )

        customer_dict["wallet_segment"] = get_wallet_segment(
            customer_dict["wallet_balance"]
        )

        (
            customer_dict["risk_level"],
            customer_dict["risk_flag"]
        ) = get_risk_details(
            customer_dict["account_status"],
            customer_dict["wallet_balance"])

        ordered_customer = {
            column: customer_dict.get(column)
            for column in COLUMN_ORDER


        }
        successful_records += 1


        transform_customers_list.append(ordered_customer)

    logger.info(
        "SUMMARY | Transformation completed | "
        "total=%d | successful=%d | skipped=%d | "
        "duplicate_customer_ids=%d | duplicate_account_numbers=%d | "
        "duplicate_emails=%d",
        total_records,
        successful_records,
        skipped_records,
        duplicate_customer_ids,
        duplicate_account_numbers,
        duplicate_emails
    )

    return transform_customers_list

