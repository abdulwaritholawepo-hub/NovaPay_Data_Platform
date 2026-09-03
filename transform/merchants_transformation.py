import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.merchants_response_validator import merchants_response_validator
from datetime import datetime, date
import logging
from config import logging_config
logger = logging.getLogger(__name__)

def transform_merchants():
    total_records = 0
    successful_records = 0
    skipped_records = 0
    duplicate_merchant_ids = 0
    duplicate_account_numbers = 0
    duplicate_emails = 0
    transformed_merchants_list = []
    seen_merchant_ids = set()
    seen_account_numbers = set()
    seen_emails = set()
    MERCHANT_COLUMN_ORDER = [
        "merchant_id",
        "merchant_code",
        "merchant_name",
        "category",
        "segment",
        "email",
        "email_domain",
        "duplicate_email",
        "phone_number",
        "city",
        "state",
        "location",
        "account_number",
        "merchant_status",
        "is_active",
        "created_at",
        "merchant_tenure_days",
        "tenure_category"
    ]
    CATEGORY_SEGMENT = {
        "Supermarket": "Retail",
        "E-commerce":  "Digital Commerce",
        "Telecom":     "Telecommunications",
        "Transport":   "Mobility"
        }
    CATEGORY_MAPPING ={
        "supermarket": "Supermarket",
        "ecommerce": "E-commerce",
        "e commerce": "E-commerce",
        "e-commerce": "E-commerce",
        "telecom": "Telecom",
        "transport": "Transport"
        }
    STATE_MAPPING = {
        "fct": "Federal Capital Territory",
        }
    CANONICAL_STATUSES = [
        "Active",
        "Inactive",
        "Suspended"
    ]
    IS_ACTIVE_MAPPING = {
        "Active": True,
        "Inactive": False,
        "Suspended": False
        }
    INVALID_MERCHANT_ID = "Invalid merchant ID"
    INVALID_MERCHANT_NAME = "Invalid merchant name"
    INVALID_MERCHANT_CATEGORY = "Invalid merchant category"
    INVALID_MERCHANT_EMAIL = "Invalid email"
    INVALID_PHONE_NUMBER = "Invalid phone number"
    INVALID_MERCHANT_CITY = "Invalid city"
    INVALID_MERCHANT_STATE = "Invalid state"
    INVALID_ACCOUNT_NUMBER = "Invalid account number"
    INVALID_MERCHANT_STATUS = "Invalid merchant status"
    INVALID_CREATED_AT = "Invalid created at"
    MISSING_VALUES = {
        "", "null", "NULL", "None", "none", "N/A", "n/a", "NA", "na", "-"
    }
    logger.info("START | Merchant transformation started")


    logger.info("VALIDATION | Starting merchant response validation")
    validated_merchants = merchants_response_validator()
    logger.info(
        "VALIDATION | Merchant response validation completed | records=%d",
        len(validated_merchants)
    )
    
    def cleaning_key_value(key, value):
        
        if key == "merchant_id":
            
            if value is None:
                return None
            if isinstance(value,bool):
                return INVALID_MERCHANT_ID
            if not isinstance(value,int):
                return  INVALID_MERCHANT_ID
            if value <= 0:
                return INVALID_MERCHANT_ID
            return value
        
        if isinstance(value,str):
            value = " ".join(value.split())
            if value in MISSING_VALUES:
              return None

        if key == "merchant_name":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_MERCHANT_NAME
            value =" ".join(value.split())
            return value

        if key == "category":
            if value is None:
                return None
            if not isinstance(value, str):
                return INVALID_MERCHANT_CATEGORY
            value =" ".join(value.split()).lower()
            value = CATEGORY_MAPPING.get(value, INVALID_MERCHANT_CATEGORY)
            return value

        if key == "email":
            if value is None:
                return None
            if not isinstance(value, str):
                return INVALID_MERCHANT_EMAIL
            value =" ".join(value.split()).lower()
            if value.count("@") != 1:
                return INVALID_MERCHANT_EMAIL
            user_name, domain = value.split("@")
            if not user_name or not domain:
                return INVALID_MERCHANT_EMAIL
            if "." not in domain:
                return INVALID_MERCHANT_EMAIL
            return value

        if key == "phone_number":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_PHONE_NUMBER
            value = " ".join(value.split())

            value = (
                value.replace("-", "")
                .replace("(", "")
                .replace(")", "")
            )
            
            if value.startswith("0"):
                value = "+234" + value[1:]
            
            elif value.startswith("234"):
                value = "+" + value
            
            
            if (
                not value.startswith("+234")
                or not value[4:].startswith(('70', '80', '90', '91','71', '81'))
                or not value[1:].isdigit()
                or len(value) != 14
            ):
                return INVALID_PHONE_NUMBER
            return value

        if key == "city":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_MERCHANT_CITY
            value =" ".join(value.split()).title()
            return value

        if key == "state":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_MERCHANT_STATE
            value =" ".join(value.split()).lower()
            value = STATE_MAPPING.get(value,value)
            value = value.title()
            return value

        if key == "account_number":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_ACCOUNT_NUMBER
            value =" ".join(value.split())
            value = (
                value.replace(" ", "")
                .replace("-", "")
                .replace(".", "")
                .replace(",", "")
            )
            if not value.isdigit():
                return INVALID_ACCOUNT_NUMBER
            if len(value) != 10:
                return INVALID_ACCOUNT_NUMBER
            return value
        
        if key == "merchant_status":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_MERCHANT_STATUS
            value =" ".join(value.split()).capitalize()
            if value not in CANONICAL_STATUSES:
                return INVALID_MERCHANT_STATUS
            return value

        if key == "created_at":
            if value is None:
                return None
            if not isinstance(value,str):
                return INVALID_CREATED_AT
            value =" ".join(value.split())
            try:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return INVALID_CREATED_AT
            return value
        
        return value

    
    for merchants in validated_merchants:
        total_records += 1

        logger.info(
            "RECORD TRANSFORMATION | Transforming record=%d",
            total_records
        )

        merchants_dict = {
        key: cleaning_key_value(key=key,value=value)
        for key, value in merchants.items()
        }
        merchant_id = merchants_dict["merchant_id"]
        account_number = merchants_dict["account_number"]
        email = merchants_dict["email"]

        if merchant_id == INVALID_MERCHANT_ID or merchant_id is None:
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | invalid/missing merchant_id",
                total_records
            )
            skipped_records += 1
            continue


        if merchant_id in seen_merchant_ids:
            duplicate_merchant_ids += 1
            skipped_records += 1
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate merchant_id=%s",
                total_records,
                merchant_id
            )
            continue

        if account_number == INVALID_ACCOUNT_NUMBER or account_number is None:
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | invalid/missing account_number",
                total_records
            )
            skipped_records += 1
            continue

        if account_number in seen_account_numbers:
            duplicate_account_numbers += 1
            skipped_records += 1
            logger.warning(
                "DUPLICATE DETECTION | Skipping record=%d | duplicate account_number",
                total_records
            )
            continue
        seen_merchant_ids.add(merchant_id)
        seen_account_numbers.add(account_number)
        merchants_dict["merchant_code"] = f"MER{merchant_id:06d}"

        if email is None or email == INVALID_MERCHANT_EMAIL or not email:
            merchants_dict["email"] = None
            merchants_dict["duplicate_email"] = None
            merchants_dict["email_domain"] = None
        else:
            domain = email.split("@")[1]
            merchants_dict["email_domain"] = domain
            if email not in seen_emails:
                seen_emails.add(email)
                merchants_dict["duplicate_email"] = "Unique"
                
            else:
                duplicate_emails += 1
                merchants_dict["duplicate_email"] = "Duplicate"
                logger.warning(
                    "DUPLICATE DETECTION | Duplicate email detected | record=%d",
                    total_records
                )
                    

        category= merchants_dict["category"]
        if category is None or category == INVALID_MERCHANT_CATEGORY:
            merchants_dict["segment"] = None
        else:
            merchants_dict["segment"] = CATEGORY_SEGMENT.get(category)


        city = merchants_dict["city"]
        state = merchants_dict["state"]
        if city is None or state is None:
            merchants_dict["location"] = None
        elif city == INVALID_MERCHANT_CITY or state == INVALID_MERCHANT_STATE:
            merchants_dict["location"] = None
        else:
            merchants_dict["location"] = f"{city}, {state}"
        merchant_status = merchants_dict["merchant_status"]
        if merchant_status == INVALID_MERCHANT_STATUS or merchant_status is None or not merchant_status:
            merchants_dict["is_active"] = None
        else:
            merchants_dict["is_active"] = IS_ACTIVE_MAPPING.get(merchant_status)

        created_at = merchants_dict["created_at"]
        today = date.today()
        if created_at is None or created_at == INVALID_CREATED_AT:
            merchant_tenure_days = None
        else:
            merchant_tenure_days = (today - created_at.date()).days
        merchants_dict["merchant_tenure_days"] = merchant_tenure_days
        if merchant_tenure_days is None:
            merchants_dict["tenure_category"] = None
        elif merchant_tenure_days < 365:
            merchants_dict["tenure_category"] = "New"
        elif 365 <= merchant_tenure_days <= 1094:
            merchants_dict["tenure_category"] = "Established"
        elif 1095 <= merchant_tenure_days <= 1824:
            merchants_dict["tenure_category"] = "Experienced"
        elif merchant_tenure_days >= 1825:
            merchants_dict["tenure_category"] = "Veteran"

        logger.info(
            "DERIVATION | Derived fields completed | record=%d",
            total_records
        )

        ordered_merchants = {
            column: merchants_dict.get(column)
            for column in MERCHANT_COLUMN_ORDER
            }

        successful_records += 1


        logger.info(
            "SUCCESS | Merchant transformation completed | record=%d | merchant_id=%s",
            total_records,
            merchant_id
        )
                            

            
        transformed_merchants_list.append(ordered_merchants)

    logger.info(
        "SUMMARY | Transformation completed | "
        "total=%d | successful=%d | skipped=%d | "
        "duplicate_merchant_ids=%d | duplicate_account_numbers=%d | "
        "duplicate_emails=%d",
        total_records,
        successful_records,
        skipped_records,
        duplicate_merchant_ids,
        duplicate_account_numbers,
        duplicate_emails
    )

    return transformed_merchants_list
transform_merchants()
