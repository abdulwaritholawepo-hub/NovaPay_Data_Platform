import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extract_response_validator.response_validator import validate_extracts
from extract_response_validator.customer_extractor import extract_customers
customer_required_fields = ["customer_id", "first_name", "last_name",
                            "phone_number", "email", "created_at", "date_of_birth", 
                            "gender", "wallet_balance", "account_number",
                            "account_status",]

def customer_response_validator(data= None):
    if  data is None:
        return validate_extracts(extracts=extract_customers(), 
                                domain='customer',
                                required_fields=customer_required_fields)
    else:
        return validate_extracts(extracts=data, 
                                domain='customer',
                                required_fields=customer_required_fields)