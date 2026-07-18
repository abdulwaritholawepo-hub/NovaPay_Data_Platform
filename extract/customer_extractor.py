import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.api_client import get_customer_data

def extract_customers():
    customer_data = get_customer_data()
    return customer_data