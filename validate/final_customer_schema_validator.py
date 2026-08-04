import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer import transform_customers

customers_transformed = transform_customers()

REQUIRED_COLUMNS =[
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
    "Eligibility",
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
    
    validation_results = []
    
    for customer in customers_transformed:
        missing_columns = []
        
        
        for column in REQUIRED_COLUMNS:
            
            if column not in customer:
                missing_columns.append(column)
        validation_dict = {'customer_id': customer.get('customer_id'),  'missing_columns': missing_columns}
        validation_results.append(validation_dict)
        if missing_columns:
            print( f"{customer.get('customer_id')}: missing customer columns -> {missing_columns}")
        else:
            print(f"{customer.get('customer_id')}: no missing customer column")
    return validation_results


def validate_data_types():
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
        "Eligibility": str,
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
            "customer_id": customer.get("customer_id"),
            "invalid_types": invalid_types,
            "validation_status": "Passed" if not invalid_types else "Failed"
        }

        validation_results.append(validation_dict)

    return validation_results


def required_values():
    REQUIRED_VALUES = [
        "customer_id",
        "account_number",
        "full_name",
        "customer_initials",
        "gender",
        "age",
        "Eligibility",
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
            "customer_id": customer.get("customer_id"),
            "missing_required_values": missing_required_values,
            "validation_status": "Passed" if not missing_required_values else "Failed"
        }

        validation_results.append(validation_dict)

    return validation_results


def required_domains():
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

        "Eligibility": {
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
            "customer_id": customer.get("customer_id"),
            "invalid_domains": invalid_domains,
            "validation_status": "Passed" if not invalid_domains else "Failed"
        }

        validation_results.append(validation_dict)

    return validation_results


def required_length():
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
                    "validation_status": "Passed" if not invalid_lengths else "Failed"
                }
        validation_results.append(validation_dict)
    return validation_results

def unique_fields():
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
                duplicate_customers.add(column)
        validation_dict = {
                            "customer_id": customer.get("customer_id"),
                            "duplicate_values": duplicate_customers,
                            "validation_status": "Passed" if not duplicate_customers else "Failed"
                        }
        validation_results.append(validation_dict)
    return validation_results