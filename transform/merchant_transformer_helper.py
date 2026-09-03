from datetime import datetime, date



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
def cleaning_key_value(key, value):
    if value is None:
        return None
    if key == "merchant_id":

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
        if not isinstance(value,str):
            return INVALID_MERCHANT_NAME
        return value

    if key == "category":
        if not isinstance(value,str):
            return INVALID_MERCHANT_CATEGORY
        value = value.lower()
        value = CATEGORY_MAPPING.get(value, INVALID_MERCHANT_CATEGORY)
        return value

    if key == "email":
        if not isinstance(value,str):
            return INVALID_MERCHANT_EMAIL
        value = value.lower()
        if value.count("@") != 1:
            return INVALID_MERCHANT_EMAIL
        user_name, domain = value.split("@")
        if not user_name or not domain:
            return INVALID_MERCHANT_EMAIL
        if "." not in domain:
            return INVALID_MERCHANT_EMAIL
        return value

    if key == "phone_number":
        if not isinstance(value,str):
            return INVALID_PHONE_NUMBER
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
        if not isinstance(value,str):
            return INVALID_MERCHANT_CITY
        value = value.title()
        return value

    if key == "state":
        if not isinstance(value,str):
            return INVALID_MERCHANT_STATE
        value = value.lower()
        value = STATE_MAPPING.get(value,value)
        value = value.title()
        return value

    if key == "account_number":
        if not isinstance(value,str):
            return INVALID_ACCOUNT_NUMBER
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
        if not isinstance(value,str):
            return INVALID_MERCHANT_STATUS
        value = value.capitalize()
        if value not in CANONICAL_STATUSES:
            return INVALID_MERCHANT_STATUS
        return value

    if key == "created_at":
        if not isinstance(value,str):
            return INVALID_CREATED_AT
        try:
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return INVALID_CREATED_AT
        return value

    return value


def generate_merchant_code(merchant_id):
    return f"MER{merchant_id:06d}"


def transform_email(email, seen_emails):
    if email is None or email == INVALID_MERCHANT_EMAIL or not email:
        return None, None, None

    domain = email.split("@")[1]

    if email not in seen_emails:
        seen_emails.add(email)
        duplicate_email = "Unique"
    else:
        duplicate_email = "Duplicate"

    return email, domain, duplicate_email


def transform_segment(category):
    if category is None or category == INVALID_MERCHANT_CATEGORY:
        return None

    return CATEGORY_SEGMENT.get(category)


def transform_location(city, state):
    if city is None or state is None:
        return None

    if city == INVALID_MERCHANT_CITY or state == INVALID_MERCHANT_STATE:
        return None

    return f"{city}, {state}"


def transform_is_active(merchant_status):
    if (
        merchant_status == INVALID_MERCHANT_STATUS
        or merchant_status is None
        or not merchant_status
    ):
        return None

    return IS_ACTIVE_MAPPING.get(merchant_status)


def transform_merchant_tenure(created_at):
    if created_at is None or created_at == INVALID_CREATED_AT:
        return None, None

    merchant_tenure_days = (date.today() - created_at.date()).days

    if merchant_tenure_days < 365:
        tenure_category = "New"
    elif merchant_tenure_days <= 1094:
        tenure_category = "Established"
    elif merchant_tenure_days <= 1824:
        tenure_category = "Experienced"
    else:
        tenure_category = "Veteran"

    return merchant_tenure_days, tenure_category
