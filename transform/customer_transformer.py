import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.response_validator import validate_customer_data



def transform_customers():
    transform_customers_list  = []
    customer_id_set = set()
    validated_customers= validate_customer_data()
    def clean_transform_value(key,val):
        
        if isinstance(val,str):
            val = val.strip()
           

            if key in{"first_name", "last_name"} and val:
                return val.capitalize()
            if key == "email" and val:
                return val.lower()
            if key == "gender" and val:
                val = val.lower()
                if val in {"male","m"}:
                    return "Male"
                elif val in {"female","f"}:
                    return "Female"
                else:
                    return "Unknown"

            try:
                if key == "created_at" and val:
                    val = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")
                            
                if key == "date_of_birth" and val:
                    val = datetime.strptime(val, "%Y-%m-%d").date()
                return val

            except Exception:
            
                raise
        
            
        return val


    for customer in validated_customers:
        customer_transform = {
        key: clean_transform_value(key=key,val=value) 
        for key, value in customer.items()

            
        }
        if customer_transform["customer_id"] not in customer_id_set:
            customer_id_set.add(customer_transform["customer_id"])
            

        else:
            continue
        transform_customers_list.append(customer_transform)
        
    print(customer_id_set)
    print(len(customer_id_set))
    print(transform_customers_list)
    return transform_customers_list
        
  
transform_customers()