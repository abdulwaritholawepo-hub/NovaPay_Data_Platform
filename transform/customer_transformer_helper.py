from datetime import datetime, date
import math

INVALID_AGE = "Invalid Age"
INVALID_CUSTOMER_ID = "Invalid customer ID"
INVALID_ACCOUNT_NUMBER = "Invalid account number"
INVALID_EMAIL_ADDRESS = "Invalid email address"
INVALID_PHONE_NUMBER = "Invalid number format"
INVALID_ACCOUNT_DATE = "Invalid Account Date"
gmail_separator = "@"
MISSING_VALUES = {
    "", "null", "NULL", "None", "none", "N/A", "n/a", "NA", "na", "-"
}

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
    "eligibility",
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

def clean_transform_value(key, val, missing_values):
    if val is None:
        return None
    if isinstance(val,str):
        val = val.strip()
        if val in missing_values:
            return None
    if key == "customer_id":
        return clean_customer_id(val=val)

    if key == "wallet_balance":
        return clean_wallet_balance(val=val)


    if isinstance(val, str):

        if key == "account_number" and val:
            return clean_account_number(val=val)

        if key in {"first_name", "last_name"} and val:
            return val.capitalize()

        if key == "email" and val:
            return clean_email(val=val)

        if key == "account_status" and val:
            return clean_account_status(val=val)

        if key == "gender" and val:
            return clean_gender(val=val)

        if key == "phone_number" and val:
            return clean_phone_number(val=val)

        if key in {"created_at", "date_of_birth"} and val:
            return clean_created_at_and_date_of_birth(val=val, key=key)

    return val


def clean_customer_id(val):


    if val is None:
        return None

    if isinstance(val, bool):
        return INVALID_CUSTOMER_ID

    if not isinstance(val, int):
        return INVALID_CUSTOMER_ID

    if val <= 0:
        return INVALID_CUSTOMER_ID
    return val


def clean_wallet_balance(val):
    if val is None:
        return None
    
    if isinstance(val, bool):
        return None

    if isinstance(val, str):
        val = val.replace(",", "")
    try:
        val = float(val)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(val):
        return None

    if val < 0:
        return None

    val = round(val, 2)
    return val


def clean_account_number(val):

    val = (
        val.replace(" ", "")
        .replace("-", "")
        .replace(".", "")
        .replace(",", "")
    )

    if not val.isdigit():
        return INVALID_ACCOUNT_NUMBER

    if len(val) != 10:
        return INVALID_ACCOUNT_NUMBER

    return val


def clean_email(val):
    val = val.lower()
    if any(char.isspace() for char in val):
        return INVALID_EMAIL_ADDRESS
    if val.count(gmail_separator) != 1:
        return INVALID_EMAIL_ADDRESS

    user_name, domain = val.split(gmail_separator)

    if not user_name or not domain:
        return INVALID_EMAIL_ADDRESS
    if "." not in domain:
        return INVALID_EMAIL_ADDRESS
    first_text, separator, second_text = domain.partition(".")
    if not first_text:
        return INVALID_EMAIL_ADDRESS
    if not second_text:
        return INVALID_EMAIL_ADDRESS
    return val


def clean_account_status(val):

    val = val.lower()
    if val in {"active", "enabled"}:
        return "Active"
    elif val in {"inactive", "disabled"}:
        return "Inactive"
    elif val in {"closed"}:
        return "Closed"
    else:
        return "Unknown"


def clean_gender(val):

    val = val.lower()
    if val in {"male", "m"}:
        return "Male"
    elif val in {"female", "f"}:
        return "Female"
    else:
        return "Unknown"


def clean_phone_number(val):


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


    if (
        not val.startswith("+234")
        or not val[1:].isdigit()
        or len(val) != 14
    ):
        return INVALID_PHONE_NUMBER

    return val


def clean_created_at_and_date_of_birth(val, key):


    if key == "created_at" and val:
        val = datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")

    if key == "date_of_birth" and val:
        val = datetime.strptime(val, "%Y-%m-%d").date()
    return val


def calculate_age(date_of_birth,reference_date=None):

    if date_of_birth is None:
        return INVALID_AGE
    elif isinstance(date_of_birth,datetime):
        date_of_birth = date_of_birth.date()
    elif isinstance(date_of_birth,date):
        pass
    else:
        return INVALID_AGE
    if reference_date is None:
        today = date.today()
        age = today.year - date_of_birth.year
        
        if (date_of_birth.month, date_of_birth.day) > (today.month, today.day):
            age -= 1
    elif isinstance(reference_date,datetime):

        reference_date = reference_date.date()
        age = reference_date.year - date_of_birth.year
        
        if (date_of_birth.month, date_of_birth.day) > (reference_date.month, reference_date.day):
            age -= 1
        
    elif isinstance(reference_date,date):
        age = reference_date.year - date_of_birth.year

        if (date_of_birth.month, date_of_birth.day) > (reference_date.month, reference_date.day):
            age -= 1
    else:
        raise TypeError("wrong datatype")

    if age < 0 or age > 120:
        return INVALID_AGE

    return age


def get_customer_segment(age):
    if age is None:
        return "Unknown"
    elif age < 0:
        return "Unknown"
    elif 0 <= age <= 17:
        return "Minor"

    elif 18 <= age <= 25:
        return "Young Adult"

    elif 26 <= age <= 40:
        return "Adult"

    elif 41 <= age <= 60:
        return "Middle Aged"
    elif 61 <= age <= 120:
        return "Senior"
    elif age > 120:
        return "Unknown"
    else:
        return "Unknown"


def calculate_account_tenure(created_at, date_of_birth, reference_date=None):
    if not created_at:
        return None, "Unknown"

    if not isinstance(created_at, datetime):
        return INVALID_ACCOUNT_DATE, "Unknown"

    if date_of_birth is not None and (
        not isinstance(date_of_birth, date) or isinstance(
            date_of_birth, datetime)
    ):
        return INVALID_ACCOUNT_DATE, "Unknown"
    if reference_date is None:
        reference_date = date.today()
    elif isinstance(reference_date, datetime):
        reference_date = reference_date.date()
    elif isinstance(reference_date,date):
        pass
    else:
        raise TypeError("wrong data type")
    
    if date_of_birth is not None and created_at.date() < date_of_birth:
        return INVALID_ACCOUNT_DATE, "Unknown"

    if created_at.date() > reference_date:
        return INVALID_ACCOUNT_DATE, "Unknown"

    account_tenure_days = (reference_date - created_at.date()).days
    
    if 0 <= account_tenure_days <= 30:
        customer_lifetime_stage = "New Customer"
    elif 31 <= account_tenure_days <= 180:
        customer_lifetime_stage = "Growing Customer"
    elif 181 <= account_tenure_days <= 365:
        customer_lifetime_stage = "Established Customer"
    elif 366 <= account_tenure_days <= 1095:
        customer_lifetime_stage = "Loyal Customer"
    elif account_tenure_days >= 1096:
        customer_lifetime_stage = "Veteran Customer"
    else:
        customer_lifetime_stage = INVALID_ACCOUNT_DATE
    return account_tenure_days, customer_lifetime_stage

def get_wallet_segment(wallet_balance):

    if wallet_balance is None:
        return "Unknown"
    elif wallet_balance <= 10000:
        return "Low Value"
    elif wallet_balance <= 100000:
        return "Medium Value"
    elif wallet_balance <= 500000:
        return "High Value"
    else:
        return "Premium"


def get_risk_details(account_status, wallet_balance):

    if wallet_balance is None:
        risk_level, risk_flag = "Unknown", "Unknown"
    else:

        if account_status == "Inactive" and wallet_balance >= 8_000_000:
            risk_level = "Very High"

        elif account_status == "Inactive" and wallet_balance > 500_000:
            risk_level = "High"

        elif account_status == "Inactive":
            risk_level = "Medium"

        elif account_status == "Active" and wallet_balance <= 100_000:
            risk_level = "Low"

        elif account_status == "Active" and wallet_balance <= 500_000:
            risk_level = "Medium"
        elif account_status == "Active" and wallet_balance > 500_000:
            risk_level = "Low"
        
        else:
            risk_level = "Unknown"

        if risk_level in ("Very High", "High"):
            risk_flag = "Review Required"
        elif risk_level in ("Medium","Low"):
            risk_flag = "Normal"
        else:
            risk_flag = "Unknown"

    return risk_level, risk_flag


def get_full_name(first_name, last_name):

    if not first_name or not last_name:
        full_name = "Unknown"
    else:
        full_name = first_name + " " + last_name
    return full_name


def get_customer_initials(first_name, last_name):

    if not first_name or not last_name:
        return "Unknown"

    return (first_name[0] + last_name[0]).upper()


def get_customer_age_details(date_of_birth, reference_date=None):

    if date_of_birth is None:
        return "Unknown", None, "Not Eligible", "Unknown"
    age = calculate_age(date_of_birth, reference_date)
    if age == INVALID_AGE:
        return age, None, "Not Eligible", "Unknown"

    is_adult = age >= 18

    eligibility = (
        "Eligible"
        if is_adult
        else "Not Eligible"
    )

    customer_segment = get_customer_segment(age)

    return age, is_adult, eligibility, customer_segment


def get_email_domain(email):


    if not email or email == INVALID_EMAIL_ADDRESS:
        return None

    _, domain = email.split(gmail_separator)
    return domain
