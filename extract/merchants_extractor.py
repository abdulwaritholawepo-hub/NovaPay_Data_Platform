import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.merchants_api_client import get_merchants_data

def extract_merchants():
    merchants_data = get_merchants_data()
    print(merchants_data)
    return merchants_data
extract_merchants()