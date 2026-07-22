import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extract.customer_extractor import extract_customers

required_fields = ["customer_id", "first_name", "last_name", "phone_number", "email", "created_at", "date_of_birth", "gender", "account_status"]
    

def validate_customer_data():
    
    customer_data = extract_customers()
    try:
        if isinstance(customer_data, list):
            print("This is a list")
        else:
            raise Exception("Customer data is not a list")
        if not customer_data:
         raise Exception("extracted customer data is empty")
        print("Customer data is not empty")
        
        for customer in customer_data:
            if isinstance(customer, dict):
              print("This is a dictionary")
            else:
              raise Exception("Customer data is not a dictionary")
            for field in required_fields:
              if field in customer:
                print(f"{field} is present in the customer data")
              else:
                raise Exception(f"{field} is not present in the customer data")
            for key, value in customer.items():
              if value == "":
                raise Exception(f"{key} contains empty values")
              if value is None:
                raise Exception(f"{key} contains None values")
           
    except Exception :
       raise
    return customer_data
validate_customer_data()