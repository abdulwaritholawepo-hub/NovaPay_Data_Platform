import sys
import os
from datetime import datetime, date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.response_validator import validate_customer_data

def transform_customers():
    INVALID_PHONE_NUMBER = "Invalid number format"
    INVALID_EMAIL_ADDRESS = "Invalid email address"
    INVALID_ACCOUNT_NUMBER = "Invalid account number"
    INVALID_CUSTOMER_ID = "Invalid customer ID"
    INVALID_AGE = "Invalid Age"
    INVALID_ACCOUNT_DATE = "Invalid Account Date"
    gmail_operator = "@"
    transform_customers_list  = []
    seen_customer_ids = set()
    seen_emails = set()
    seen_account_numbers = set()
    MISSING_VALUES = {
    "", "null", "NULL", "None", "none", "N/A", "n/a", "NA", "na", "-"
    }
    validated_customers= validate_customer_data()
    COLUMN_ORDER = [
    "customer_id",
    "account_number",
    "first_name",
    "last_name",
    "full_name",
    "customer_initials",
    "gender",
    "date_of_birth",
    "age",
    "is_adult",
    "Eligibility",
    "customer_segment",
    "phone_number",
    "email",
    "email_domain",
    "duplicate_email",
    "account_status",
    "wallet_balance",
    "wallet_segment",
    "risk_level",
    "risk_flag",
    "created_at",
    "account_tenure_days",
    "customer_lifetime_stage",
    ]
    def clean_transform_value(key,val):
        if key == "customer_id":
            if val is None:
                return None

    
            if isinstance(val, bool):
                return INVALID_CUSTOMER_ID
            
            if not isinstance(val,int):
                return INVALID_CUSTOMER_ID

            if val <= 0:
                return INVALID_CUSTOMER_ID
            return val
    
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

            

            if key == "account_number" and val:
                val = (
                    val.replace(" ", "")
                    .replace("-", "")
                    .replace(".", "")
                    .replace(",","")
                )

                if not val.isdigit():
                    return INVALID_ACCOUNT_NUMBER

                if len(val) != 10:
                    return INVALID_ACCOUNT_NUMBER
                
                return val
            
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

            if key == "account_status" and val:
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
            first_name = customer_transform["first_name"]
            last_name = customer_transform["last_name"]
            if not first_name or not last_name:
                customer_transform["customer_initials"] = "Unknown"
            else:
                customer_transform["customer_initials"] = (first_name[0] + last_name[0]).upper()

            if customer_transform["account_number"] not in seen_account_numbers:
                seen_account_numbers.add(customer_transform["account_number"])
            else:
                continue

            if customer_transform["email"] in seen_emails:
                customer_transform["duplicate_email"] = "Duplicate"
            else:
                seen_emails.add(customer_transform["email"])
                customer_transform["duplicate_email"] = "Unique"

            email = customer_transform["email"]

            if email and email != INVALID_EMAIL_ADDRESS:
                _, domain = email.split(gmail_operator)
                customer_transform["email_domain"] = domain
            else:
                customer_transform["email_domain"] = None
                
            if not customer_transform["date_of_birth"]:
                age = "Unknown"
                customer_segment = "Unknown"
                customer_transform["age"] = age
                customer_transform["customer_segment"] = customer_segment
                
            else:
                age = date.today().year - customer_transform["date_of_birth"].year
                if (customer_transform["date_of_birth"].month, customer_transform["date_of_birth"].day) > (date.today().month, date.today().day):
                    age -= 1

                
                if age < 0 or age > 120 or age < 18:
                    customer_transform["age"] = INVALID_AGE
                    customer_transform["customer_segment"] = "Unknown"
                    customer_transform["Eligibility"] = "Not Eligible"
                    customer_transform["is_adult"] = None
                else: 
                    customer_transform["age"] = age
                    customer_transform["Eligibility"] = "Eligible"
                    if age >= 18:
                        customer_transform["is_adult"] = True
                    else:
                        customer_transform["is_adult"] = False
                    
                    if 0 <= age <= 17:
                        customer_segment = "Minor"
                    
                    elif 18 <= age <= 25:
                        customer_segment = "Young Adult"

                    elif 26 <= age <= 40:
                        customer_segment = "Adult"
                        
                    elif 41 <= age <= 60:
                        customer_segment = "Middle Aged"
                    elif 61 <= age <= 120:
                        customer_segment = "Senior"
                    else:
                        customer_segment = "Unknown"
                
                    customer_transform["customer_segment"] = customer_segment



            if not customer_transform["created_at"]:
                customer_transform["account_tenure_days"] = None
                customer_transform["customer_lifetime_stage"] = "Unknown"
            else:
                created_at = customer_transform["created_at"] 
                date_of_birth = customer_transform["date_of_birth"]
                
                if (date_of_birth is not None) and (created_at.date() < date_of_birth or created_at.date() > date.today()):
                    
                    customer_transform["account_tenure_days"] = INVALID_ACCOUNT_DATE
                    customer_transform["customer_lifetime_stage"] = "Unknown"
                else:
                    account_tenure_days= (date.today() - created_at.date()).days
                    customer_transform["account_tenure_days"] = account_tenure_days
                    if 0 <= account_tenure_days <= 30:
                        customer_transform["customer_lifetime_stage"] = "New Customer"
                    elif 31 <= account_tenure_days <= 180:
                        customer_transform["customer_lifetime_stage"] = "Growing Customer"
                    elif 181 <= account_tenure_days <= 365:
                        customer_transform["customer_lifetime_stage"] = "Established Customer"
                    elif 366 <= account_tenure_days <= 1095:
                        customer_transform["customer_lifetime_stage"] = "Loyal Customer"
                    elif account_tenure_days >= 1096:
                        customer_transform["customer_lifetime_stage"] = "Veteran Customer"
                    else:
                        customer_transform["customer_lifetime_stage"] = INVALID_ACCOUNT_DATE
            
            wallet_balance = customer_transform["wallet_balance"]
            account_status = customer_transform["account_status"]
            

            if wallet_balance is None:
                wallet_segment = "Unknown"
            elif wallet_balance <= 10000:
                wallet_segment = "Low Value"
            elif  wallet_balance <= 100000:
                wallet_segment = "Medium Value"
            elif wallet_balance <= 500000:
                wallet_segment = "High Value"
            else:
                wallet_segment = "Premium"
                    
            customer_transform["wallet_segment"] = wallet_segment
            if wallet_balance is None:
                customer_transform["risk_level"] = "Unknown"
                customer_transform["risk_flag"] = "Unknown"
            else:
                
                if account_status == "Inactive" and wallet_balance >= 8_000_000:
                    customer_transform["risk_level"] = "Very High"

                elif account_status == "Inactive" and wallet_balance > 500_000:
                    customer_transform["risk_level"] = "High"

                elif account_status == "Inactive":
                    customer_transform["risk_level"] = "Medium"

                elif account_status == "Active" and wallet_balance <= 100_000:
                    customer_transform["risk_level"] = "Low"

                elif account_status == "Active" and wallet_balance <= 500_000:
                    customer_transform["risk_level"] = "Medium"

                else:
                    customer_transform["risk_level"] = "Low"

                if customer_transform["risk_level"] in ("Very High", "High"):
                    customer_transform["risk_flag"] = "Review Required"
                else:
                    customer_transform["risk_flag"] = "Normal"

            ordered_customer = {
            column: customer_transform.get(column)
            for column in COLUMN_ORDER
            

            }
            transform_customers_list.append(ordered_customer)

        
        else:
            continue
        print(transform_customers_list)
        return transform_customers_list
    

transform_customers()
