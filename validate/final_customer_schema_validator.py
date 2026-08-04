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
        validation_dict = {f"'customer_id': {customer.get('customer_id')}, missing_columns: {missing_columns} " }
        
        for column in REQUIRED_COLUMNS:
            validation_results.append(validation_dict)
            if column not in customer:
                missing_columns.append(column)

        if missing_columns:
            print( f"{customer.get('customer_id')}: missing customer columns -> {missing_columns}")
        else:
            print(f"{customer.get('customer_id')}: no missing customer column")
    return validation_results


