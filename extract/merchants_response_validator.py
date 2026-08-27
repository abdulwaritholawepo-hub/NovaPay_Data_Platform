import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extract.response_validator import validate_extracts
from extract.merchants_extractor import extract_merchants
merchants_required_fields = ['merchant_id', 'merchant_name', 'category', 'email',
                             'phone_number', 'city', 'state', 'account_number', 'merchant_status', 'created_at']
def merchants_response_validator():
    return validate_extracts(domain='merchant',
                             extracts=extract_merchants(),
                             required_fields=merchants_required_fields)
