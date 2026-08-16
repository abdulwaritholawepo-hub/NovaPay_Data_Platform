import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extract.customer_extractor import extract_customers

required_fields = ["customer_id", "first_name", "last_name", "phone_number", "email", "created_at", "date_of_birth", "gender", "account_status"]
    

def validate_customer_data():
    
    customer_data = extract_customers()
  
    if isinstance(customer_data, list):
        print("This is a list")
    else:
        raise  TypeError("Customer data is not a list")
    if not customer_data:
      raise ValueError("extracted customer data is empty")
    print("Customer data is not empty")
    
    for customer in customer_data:
        if isinstance(customer, dict):
          print("This is a dictionary")
        else:
          raise TypeError("Customer data is not a dictionary")
        for field in required_fields:
          if field in customer:
            print(f"{field} is present in the customer data")
          else:
            raise ValueError(f"{field} is not present in the customer data")
        for key, value in customer.items():
          if value == "":
            raise ValueError(f"{key} contains empty values")
          if value is None:
            raise ValueError(f"{key} contains None values")
           
    
    return customer_data
validate_customer_data()