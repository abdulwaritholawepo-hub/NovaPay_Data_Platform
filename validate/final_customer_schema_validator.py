from config import logging_config
import logging
from datetime import datetime, date
from transform.customer_transformer import transform_customers
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

customers_transformed = transform_customers()

logger.info(
    "Transformed customer data received for schema validation. Records: %d",
    len(customers_transformed)
)


REQUIRED_COLUMNS = [
    "customer_id",
    "account_number",
    "first_name",
    "last_name",
    "full_name",
    "customer_initials",
    "gender",
    "date_of_birth",
    "age",
    "is_adult",
    "eligibility",
    "customer_segment",
    "phone_number",
    "email",
    "email_domain",
    "duplicate_email",
    "account_status",
    "wallet_balance",
    "wallet_segment",
    "risk_level",
    "risk_flag",
    "created_at",
    "account_tenure_days",
    "customer_lifetime_stage",
]


def required_columns():

    logger.info("Starting required columns validation")

    validation_results = []

    for customer in customers_transformed:
        missing_columns = []

        for column in REQUIRED_COLUMNS:

            if column not in customer:
                missing_columns.append(column)

        validation_dict = {
            'customer_id': customer.get('customer_id'),
            'missing_columns': missing_columns,
            "validation_status": "Passed" if not missing_columns else "Failed"
        }

        validation_results.append(validation_dict)

        if missing_columns:
            logger.error(
                "Customer %s is missing required columns: %s",
                customer.get("customer_id"),
                missing_columns
            )
        else:
            logger.info(
                "Customer %s passed required columns validation",
                customer.get("customer_id")
            )

    logger.info(
        "Required columns validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def validate_data_types():

    logger.info("Starting data type validation")

    validation_results = []

    EXPECTED_TYPES = {
        "customer_id": int,
        "account_number": str,
        "first_name": (str, type(None)),
        "last_name": (str, type(None)),
        "full_name": str,
        "customer_initials": str,
        "gender": str,
        "date_of_birth": (date, type(None)),
        "age": (int, str),
        "is_adult": (bool, type(None)),
        "eligibility": str,
        "customer_segment": str,
        "phone_number": (str, type(None)),
        "email": (str, type(None)),
        "email_domain": (str, type(None)),
        "duplicate_email": str,
        "account_status": str,
        "wallet_balance": (float, type(None)),
        "wallet_segment": str,
        "risk_level": str,
        "risk_flag": str,
        "created_at": (datetime, type(None)),
        "account_tenure_days": (int, str, type(None)),
        "customer_lifetime_stage": str
    }

    for customer in customers_transformed:
        invalid_types = []

        for column, expected_type in EXPECTED_TYPES.items():

            if not isinstance(customer.get(column), expected_type):
                invalid_types.append(column)

        validation_dict = {
            'customer_id': customer.get("customer_id"),
            'invalid_types': invalid_types,
            "validation_status": "Passed" if not invalid_types else "Failed"
        }

        validation_results.append(validation_dict)

        if invalid_types:
            logger.error(
                "Customer %s has invalid data types for columns: %s",
                customer.get("customer_id"),
                invalid_types
            )

    logger.info(
        "Data type validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def required_values():

    logger.info("Starting required values validation")

    REQUIRED_VALUES = [
        "customer_id",
        "account_number",
        "full_name",
        "customer_initials",
        "gender",
        "age",
        "eligibility",
        "customer_segment",
        "duplicate_email",
        "account_status",
        "wallet_segment",
        "risk_level",
        "risk_flag",
        "customer_lifetime_stage",
    ]

    validation_results = []

    for customer in customers_transformed:
        missing_required_values = []

        for column in REQUIRED_VALUES:

            if customer.get(column) is None:
                missing_required_values.append(column)

        validation_dict = {
            'customer_id': customer.get("customer_id"),
            'missing_required_values': missing_required_values,
            "validation_status": "Passed"
            if not missing_required_values else "Failed"
        }

        validation_results.append(validation_dict)

        if missing_required_values:
            logger.error(
                "Customer %s has missing required values: %s",
                customer.get("customer_id"),
                missing_required_values
            )

    logger.info(
        "Required values validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def required_domains():

    logger.info("Starting required domain validation")

    EXPECTED_DOMAINS = {
        "gender": {
            "Male",
            "Female",
            "Unknown"
        },

        "account_status": {
            "Active",
            "Inactive",
            "Unknown"
        },

        "duplicate_email": {
            "Unique",
            "Duplicate"
        },

        "eligibility": {
            "Eligible",
            "Not Eligible"
        }
    }

    validation_results = []

    for customer in customers_transformed:
        invalid_domains = []

        for domain_keys, domain_values in EXPECTED_DOMAINS.items():

            if customer.get(domain_keys) not in domain_values:
                invalid_domains.append(domain_keys)

        validation_dict = {
            'customer_id': customer.get("customer_id"),
            'invalid_domains': invalid_domains,
            "validation_status": "Passed"
            if not invalid_domains else "Failed"
        }

        validation_results.append(validation_dict)

        if invalid_domains:
            logger.error(
                "Customer %s has invalid domain values for: %s",
                customer.get("customer_id"),
                invalid_domains
            )

    logger.info(
        "Required domain validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def required_length():

    logger.info("Starting field length validation")

    EXPECTED_LENGTHS = {
        "account_number": 10,
        "customer_initials": (2, 7),
        "phone_number": (14, None),
    }

    validation_results = []

    for customer in customers_transformed:

        invalid_lengths = []

        for column, length in EXPECTED_LENGTHS.items():

            if isinstance(length, int):

                if customer.get(column) is None:
                    continue

                elif length != len(customer.get(column)):
                    invalid_lengths.append(column)

            elif isinstance(length, tuple):

                if customer.get(column) is None:
                    continue

                elif len(customer.get(column)) not in length:
                    invalid_lengths.append(column)

        validation_dict = {
            "customer_id": customer.get("customer_id"),
            "invalid_lengths": invalid_lengths,
            "validation_status": "Passed"
            if not invalid_lengths else "Failed"
        }

        validation_results.append(validation_dict)

        if invalid_lengths:
            logger.error(
                "Customer %s has invalid field lengths for: %s",
                customer.get("customer_id"),
                invalid_lengths
            )

    logger.info(
        "Field length validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def unique_fields():

    logger.info("Starting unique fields validation")

    UNIQUE_COLUMNS = [
        "customer_id",
        "account_number",
    ]

    validation_results = []

    unique_customers = set()

    for customer in customers_transformed:

        duplicate_customers = []

        for column in UNIQUE_COLUMNS:

            if customer.get(column) not in unique_customers:
                unique_customers.add(customer.get(column))
            else:
                duplicate_customers.append(column)

        validation_dict = {
            "customer_id": customer.get("customer_id"),
            "duplicate_values": duplicate_customers,
            "validation_status": "Passed"
            if not duplicate_customers else "Failed"
        }

        validation_results.append(validation_dict)

        if duplicate_customers:
            logger.error(
                "Customer %s has duplicate values in: %s",
                customer.get("customer_id"),
                duplicate_customers
            )

    logger.info(
        "Unique fields validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def validate_ranges():

    logger.info("Starting range validation")

    EXPECTED_RANGES = {
        "age": (0, 120),
        "wallet_balance": (0, None),
        "account_tenure_days": (0, None),
    }

    validation_results = []

    for customer in customers_transformed:

        INVALID_RANGE = []

        for column, expected_range in EXPECTED_RANGES.items():

            value = customer.get(column)
            min_range, max_range = expected_range

            if value is None:
                continue

            elif max_range is None:

                if value >= min_range:
                    continue
                else:
                    INVALID_RANGE.append(column)

            elif min_range <= value <= max_range:
                continue

            else:
                INVALID_RANGE.append(column)

        validation_dict = {
            "customer_id": customer.get("customer_id"),
            "invalid_ranges": INVALID_RANGE,
            "validation_status": "Passed"
            if not INVALID_RANGE else "Failed"
        }

        validation_results.append(validation_dict)

        if INVALID_RANGE:
            logger.error(
                "Customer %s has values outside expected ranges for: %s",
                customer.get("customer_id"),
                INVALID_RANGE
            )

    logger.info(
        "Range validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def referential_integrity():

    logger.info("Starting referential integrity validation")

    validation_results = []

    for customer in customers_transformed:

        reference_errors = []

        age = customer.get("age")
        is_adult = customer.get("is_adult")
        eligibility = customer.get("eligibility")

        if age is not None and is_adult is not None:

            if age >= 18 and is_adult is not True:
                reference_errors.append("is_adult")

            elif age < 18 and is_adult is not False:
                reference_errors.append("is_adult")

        if age is not None and eligibility is not None:

            if age >= 18 and eligibility != "Eligible":
                reference_errors.append("eligibility")

            elif age < 18 and eligibility != "Not Eligible":
                reference_errors.append("eligibility")

        wallet_balance = customer.get("wallet_balance")
        wallet_segment = customer.get("wallet_segment")

        if wallet_balance is None and wallet_segment != "Unknown":
            reference_errors.append("wallet_segment")

        if wallet_balance is not None:

            if 0 <= wallet_balance <= 10000 and wallet_segment != "Low Value":
                reference_errors.append("wallet_segment")

            elif 10000 < wallet_balance <= 100000 and wallet_segment != "Medium Value":
                reference_errors.append("wallet_segment")

            elif 100000 < wallet_balance <= 500000 and wallet_segment != "High Value":
                reference_errors.append("wallet_segment")

            elif wallet_balance > 500000 and wallet_segment != "Premium":
                reference_errors.append("wallet_segment")

        risk_flag = customer.get("risk_flag")
        risk_level = customer.get("risk_level")

        if risk_flag is not None:

            if (
                risk_flag == "Review Required"
                and risk_level not in ("Very High", "High")
            ):
                reference_errors.append("risk_level")

            elif (
                risk_flag == "Normal"
                and risk_level not in ("Low", "Medium")
            ):
                reference_errors.append("risk_level")

        validation_dict = {
            "customer_id": customer.get("customer_id"),
            "referential_errors": reference_errors,
            "validation_status": "Passed"
            if not reference_errors else "Failed"
        }

        validation_results.append(validation_dict)

        if reference_errors:
            logger.error(
                "Customer %s failed referential integrity validation: %s",
                customer.get("customer_id"),
                reference_errors
            )

    logger.info(
        "Referential integrity validation completed. Records validated: %d",
        len(validation_results)
    )

    return validation_results


def schema_validation_summary():

    logger.info("Starting schema validation")

    VALIDATION_FUNCTIONS = {
        "Required Columns": required_columns,
        "Data Types": validate_data_types,
        "Required Values": required_values,
        "Required Domains": required_domains,
        "Required Length": required_length,
        "Unique Fields": unique_fields,
        "Validate Ranges": validate_ranges,
        "Referential Integrity": referential_integrity,
    }

    validation_summary = []

    for validation_name, validation_function in VALIDATION_FUNCTIONS.items():

        logger.info(
            "Running validation: %s",
            validation_name
        )

        validation_value = validation_function()

        passed_count = 0
        failed_count = 0
        total_records = len(validation_value)

        for value in validation_value:

            validation_status = value.get("validation_status")

            if validation_status == "Passed":
                passed_count += 1

            elif validation_status == "Failed":
                failed_count += 1

        summary_dict = {
            "validation_name": validation_name,
            "total_records": total_records,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "validation_status": "passed"
            if failed_count == 0 else "failed"
        }

        validation_summary.append(summary_dict)

        logger.info(
            "%s validation completed. Passed: %d, Failed: %d",
            validation_name,
            passed_count,
            failed_count
        )

    logger.info(
        "Schema validation completed. Validation checks performed: %d",
        len(validation_summary)
    )

    return validation_summary


if __name__ == "__main__":
    schema_validation_summary()
