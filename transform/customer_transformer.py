import sys
import os
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.response_validator import validate_customer_data

def transform_customers():
    INVALID_PHONE_NUMBER = "Invalid number format"
    INVALID_EMAIL_ADDRESS = "Invalid email address"
    gmail_operator = "@"
    transform_customers_list  = []
    seen_customer_ids = set()
    MISSING_VALUES = {
        "", "null", "NULL", "None", "none", "N/A", "n/a", "NA", "na", "-"
    }
    validated_customers= validate_customer_data()
    def clean_transform_value(key,val):
        
        if key == "wallet_balance":
                
            if val is None:
                return None
            
            if isinstance(val, str):
               val = val.replace(",", "")
               try:
                val = float(val)
               except ValueError:
                  return None
               
            if isinstance(val, bool):
                return None

            if isinstance(val, (int,float)):
                val = float(val)
            if val < 0:
                return None
            
            val= round(val,2)
            return val 


        if isinstance(val,str):
            val = val.strip()

            

            if val in MISSING_VALUES:
                return None
            if key in{"first_name", "last_name"} and val:
                return val.capitalize()

            if key == "email" and val:
                val = val.lower()
                if val.count(gmail_operator) != 1:
                    return INVALID_EMAIL_ADDRESS
                
                user_name, domain = val.split(gmail_operator)

                if not user_name:
                    return INVALID_EMAIL_ADDRESS
                if not domain:
                    return INVALID_EMAIL_ADDRESS
                if "." not in domain:
                    return INVALID_EMAIL_ADDRESS
                
                return val

            if key == "status" and val:
                val = val.lower()
                if val in {"active", "enabled"}:
                    return "Active"
                elif val in {"inactive", "disabled"}:
                    return "Inactive"
                else:
                    return "Unknown"


            if key == "gender" and val:
                val = val.lower()
                if val in {"male","m"}:
                    return "Male"
                elif val in {"female","f"}:
                    return "Female"
                else:
                    return "Unknown"

            if key == "phone_number" and val:
                val = (
                        val.replace("-", "")
                        .replace("(", "")
                        .replace(")", "")
                        .replace(" ", "")
                    )
                                    
                if val.startswith("0"):
                    val = "+234" + val[1:]

                elif val.startswith("234"):
                    val = "+" + val  

                    
                if(
                    not val.startswith("+234")
                   or not val[1:].isdigit()
                    or len(val) != 14
                    ):
                   return INVALID_PHONE_NUMBER
        
                return val
   
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
        if customer_transform["customer_id"] not in seen_customer_ids:
            seen_customer_ids.add(customer_transform["customer_id"])

            if not customer_transform["first_name"] or not customer_transform["last_name"]:
                full_name = "Unknown"
            else:
                full_name = customer_transform["first_name"] + " " + customer_transform["last_name"]
                
            customer_transform["full_name"] = full_name

            if not customer_transform["date_of_birth"]:
                age = "Unknown"
                customer_segment = "Unknown"
                customer_transform["age"] = age
                customer_transform["customer_segment"] = customer_segment
                
            else:
                age = date.today().year - customer_transform["date_of_birth"].year
                if (customer_transform["date_of_birth"].month, customer_transform["date_of_birth"].day) > (date.today().month, date.today().day):
                    age -= 1
               
                customer_transform["age"] = age

                if 0 <= age <= 17:
                    customer_segment = "Minor"
                
                elif 18 <= age <= 25:
                    customer_segment = "Young Adult"

                elif 26 <= age <= 40:
                    customer_segment = "Adult"
                    
                elif 41 <= age <= 60:
                    customer_segment = "Middle Aged"
                elif age >= 61:
                    customer_segment = "Senior"
                else:
                   customer_segment = "Unknown"
                
                customer_transform["customer_segment"] = customer_segment
            if not customer_transform["created_at"]:
                customer_transform["account_tenure_days"] = None
            else:
                account_tenure_days= (date.today() - customer_transform["created_at"].date()).days
                customer_transform["account_tenure_days"] = account_tenure_days
            wallet_balance = customer_transform["wallet_balance"] 
            if wallet_balance is None:
                wallet_segment == "Unknown"
            elif wallet_balance <= 10000:
                wallet_segment = "Low Value"
            elif  wallet_balance <= 100000:
                wallet_segment = "Medium Value"
            elif wallet_balance <= 500000:
                wallet_segment = "High Value"
            else:
                wallet_segment = "Premium"
            
            customer_transform["wallet_segment"] = wallet_segment
            
                


            transform_customers_list.append(customer_transform)
            
        else:
            continue
    print(transform_customers_list)
    return transform_customers_list
    
  
transform_customers()