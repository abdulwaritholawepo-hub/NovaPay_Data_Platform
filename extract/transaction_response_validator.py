
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extract.transaction_extractor import extract_transactions
from extract.response_validator import validate_extracts

transaction_required_fields = ['transaction_id', 'sender_id', 'receiver_id', 'receiver_type', 'amount', 'currency',
                               'payment_method', 'transaction_category', 'transaction_direction', 'status', 'reference_number', 'narration', 'created_at']


def transaction_response_validator():
    return validate_extracts(extracts=extract_transactions(),
                             domain='transaction',
                             required_fields=transaction_required_fields)
transaction_response_validator()