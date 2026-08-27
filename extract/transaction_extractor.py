
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.transaction_api_client import get_transaction_data

def extract_transactions():
    transaction_data = get_transaction_data()
    return transaction_data
