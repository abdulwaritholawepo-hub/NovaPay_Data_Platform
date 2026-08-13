import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.transform_helpers import (
    calculate_account_tenure,
    get_wallet_segment,
    get_risk_details,
    get_customer_initials,
    get_full_name,
    get_customer_age_details,
    check_duplicate_account_number,
    check_duplicate_customer_id,
    get_duplicate_email_status,
    get_email_domain,
    clean_transform_value,
    COLUMN_ORDER,
    MISSING_VALUES,

)
from extract.response_validator import validate_customer_data



def transform_customers():


    transform_customers_list = []
    seen_customer_ids = set()
    seen_emails = set()
    seen_account_numbers = set()
    validated_customers = validate_customer_data()

    for customer in validated_customers:
        customer_transform = {
            key: clean_transform_value(
                key=key,
                val=value,
                missing_values=MISSING_VALUES,
            )
            for key, value in customer.items()
        }

        if check_duplicate_customer_id(
            customer_transform["customer_id"],
            seen_customer_ids,
        ):

            customer_transform["full_name"] = get_full_name(
                customer_transform["first_name"], customer_transform["last_name"])

            customer_transform["customer_initials"] = get_customer_initials(
                customer_transform["first_name"], customer_transform["last_name"])

            if not check_duplicate_account_number(
                customer_transform["account_number"],
                seen_account_numbers,
            ):
                continue

            customer_transform["duplicate_email"] = get_duplicate_email_status(
                customer_transform["email"],
                seen_emails,
            )

            customer_transform["email_domain"] = get_email_domain(
                customer_transform["email"]
            )

            (
                customer_transform["age"],
                customer_transform["is_adult"],
                customer_transform["eligibility"],
                customer_transform["customer_segment"],
            ) = get_customer_age_details(
                customer_transform["date_of_birth"]
            )

            (
                customer_transform["account_tenure_days"],
                customer_transform["customer_lifetime_stage"]
            ) = calculate_account_tenure(
                customer_transform["created_at"],
                customer_transform["date_of_birth"],
            )

            customer_transform["wallet_segment"] = get_wallet_segment(
                customer_transform["wallet_balance"]
            )

            (
                customer_transform["risk_level"],
                customer_transform["risk_flag"]
            ) = get_risk_details(
                customer_transform["account_status"],
                customer_transform["wallet_balance"])

            ordered_customer = {
                column: customer_transform.get(column)
                for column in COLUMN_ORDER


            }
            transform_customers_list.append(ordered_customer)

        else:
            continue

    print(transform_customers_list)

    return transform_customers_list


if __name__ == "__main__":
    transform_customers()
