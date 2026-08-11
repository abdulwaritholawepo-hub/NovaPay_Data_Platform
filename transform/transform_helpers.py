from datetime import datetime, date

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


    if key == "customer_id":
     return clean_customer_id(val=val)

    if key == "wallet_balance":
        return clean_wallet_balance(val=val)


    if isinstance(val, str):
        val = val.strip()

        if val in missing_values:
            return None

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

    if isinstance(val, str):
        val = val.replace(",", "")
    try:
        val = float(val)
    except (ValueError, TypeError):
        return None

    if isinstance(val, bool):
        return None

    if isinstance(val, (int, float)):
        val = float(val)
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
    if val.count(gmail_separator) != 1:
        return INVALID_EMAIL_ADDRESS

    user_name, domain = val.split(gmail_separator)

    if not user_name or not domain:
        return INVALID_EMAIL_ADDRESS
    if "." not in domain:
        return INVALID_EMAIL_ADDRESS

    return val


def clean_account_status(val):

    val = val.lower()
    if val in {"active", "enabled"}:
        return "Active"
    elif val in {"inactive", "disabled"}:
        return "Inactive"
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


def calculate_age(date_of_birth):

    if date_of_birth is None:
        return INVALID_AGE

    today = date.today()

    age = today.year - date_of_birth.year

    if (date_of_birth.month, date_of_birth.day) > (today.month, today.day):
        age -= 1

    if age < 0 or age > 120:
        return INVALID_AGE

    return age


def get_customer_segment(age):

    if 0 <= age <= 17:
        return "Minor"

    elif 18 <= age <= 25:
        return "Young Adult"

    elif 26 <= age <= 40:
        return "Adult"

    elif 41 <= age <= 60:
        return "Middle Aged"
    elif 61 <= age <= 120:
        return "Senior"
    else:
        return "Unknown"


def calculate_account_tenure(created_at, date_of_birth):

    if not created_at:
        return None, "Unknown"

    if (date_of_birth is not None) and (created_at.date() < date_of_birth or created_at.date() > date.today()):

        return INVALID_ACCOUNT_DATE, "Unknown"

    account_tenure_days = (date.today() - created_at.date()).days

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

        else:
            risk_level = "Low"

        if risk_level in ("Very High", "High"):
            risk_flag = "Review Required"
        else:
            risk_flag = "Normal"

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


def get_customer_age_details(date_of_birth):

    if not date_of_birth:
        return "Unknown", None, "Not Eligible", "Unknown"

    age = calculate_age(date_of_birth)

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


def check_duplicate_account_number(account_number, seen_account_numbers):


    if account_number not in seen_account_numbers:
        seen_account_numbers.add(account_number)
        return True

    return False


def check_duplicate_customer_id(customer_id, seen_customer_ids):


    if customer_id not in seen_customer_ids:
        seen_customer_ids.add(customer_id)
        return True

    return False


def get_duplicate_email_status(email, seen_emails):


    if email in seen_emails:
        return "Duplicate"

    seen_emails.add(email)
    return "Unique"


def get_email_domain(email):


    if not email or email == INVALID_EMAIL_ADDRESS:
        return None

    _, domain = email.split(gmail_separator)
    return domain
