
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from datetime import datetime

TRANSACTION_COLUMN_ORDER = [
    "transaction_id",
    "sender_id",
    "receiver_id",
    "receiver_type",
    "amount",
    "currency",
    "payment_method",
    "transaction_category",
    "transaction_direction",
    "status",
    "reference_number",
    "narration",
    "created_at"
]

MISSING_VALUES = {
    "", "null", "NULL", "None", "none", "N/A", "n/a", "NA", "na", "-"
}
INVALID_TRANSACTION_ID = "Invalid transaction ID"
INVALID_SENDER_ID = "Invalid sender ID"
INVALID_RECEIVER_ID = "Invalid receiver ID"
INVALID_RECEIVER_TYPE = "Invalid receiver type"
INVALID_AMOUNT = "Invalid amount"
INVALID_CURRENCY = "Invalid currency"
INVALID_PAYMENT_METHOD = "Invalid payment method"
INVALID_TRANSACTION_CATEGORY = "Invalid transaction category"
INVALID_TRANSACTION_DIRECTION = "Invalid transaction direction"
INVALID_STATUS = "Invalid status"
INVALID_REFERENCE_NUMBER = "Invalid reference number"
INVALID_NARRATION = "Invalid narration"
INVALID_CREATED_AT = "Invalid created at"
INVALID_VALUES = (INVALID_TRANSACTION_ID,INVALID_SENDER_ID, INVALID_RECEIVER_ID, 
                  INVALID_RECEIVER_TYPE, INVALID_AMOUNT, INVALID_CURRENCY, 
                  INVALID_PAYMENT_METHOD,  INVALID_TRANSACTION_CATEGORY, 
                  INVALID_TRANSACTION_DIRECTION, INVALID_STATUS, INVALID_REFERENCE_NUMBER,
                    INVALID_NARRATION, INVALID_CREATED_AT)
ALLOWED_RECEIVER_TYPES = ("merchant", "customer")
ALLOWED_CURRENCIES = ("NGN",)
ALLOWED_PAYMENT_METHODS = ("qr_code", "bank_transfer", "debit_card", "wallet")
ALLOWED_TRANSACTION_CATEGORIES = ("merchant_payment", "data_purchase", "airtime_purchase",
                        "electricity_bill", "wallet_transfer")
ALLOWED_TRANSACTION_DIRECTIONS = ("debit", "credit")
ALLOWED_STATUSES = ("successful", "failed")
def cleaning_transactions_value(key,value):
    if value is None:
        return None
    if key == "transaction_id":
        if isinstance(value, bool):
            return INVALID_TRANSACTION_ID
        if not isinstance(value,int):
            return  INVALID_TRANSACTION_ID
        if value <= 0:
            return INVALID_TRANSACTION_ID
        return value

    if key == "sender_id":
        if isinstance(value, bool):
            return INVALID_SENDER_ID
        if not isinstance(value,int):
            return  INVALID_SENDER_ID
        if value <= 0:
            return INVALID_SENDER_ID
        return value

    if key == "receiver_id":
        if isinstance(value, bool):
            return INVALID_RECEIVER_ID
        if not isinstance(value,int):
            return  INVALID_RECEIVER_ID
        if value <= 0:
            return INVALID_RECEIVER_ID
        return value

    if key == "amount":
        if isinstance(value, bool):
            return INVALID_AMOUNT
        try:
            value = Decimal(value)
        except InvalidOperation  :
            return INVALID_AMOUNT
        if value.is_infinite() or value.is_nan() or value.is_subnormal():
            return INVALID_AMOUNT
        value = value.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
        if value <= 0:
            return INVALID_AMOUNT
        return value


    if isinstance(value,str):
        value = " ".join(value.split())
        if value in MISSING_VALUES:
            return None

    if key == "receiver_type":
        if not value or not isinstance(value,str):
            return INVALID_RECEIVER_TYPE
        value = value.lower()
        if value not in ALLOWED_RECEIVER_TYPES:
            return INVALID_RECEIVER_TYPE

    if key == "currency":
        if not isinstance(value,str) or not value:
            return INVALID_CURRENCY
        value = value.upper()
        if value not in ALLOWED_CURRENCIES:
            return INVALID_CURRENCY

    if key == "payment_method":
        if not isinstance(value,str) or not value:
            return INVALID_PAYMENT_METHOD
        value = value.lower()
        if value not in ALLOWED_PAYMENT_METHODS:
            return INVALID_PAYMENT_METHOD

    if key == "transaction_category":
        if not isinstance(value,str) or not value:
            return INVALID_TRANSACTION_CATEGORY
        value = value.lower()
        if value not in ALLOWED_TRANSACTION_CATEGORIES:
            return INVALID_TRANSACTION_CATEGORY

    if key == "transaction_direction":
        if not isinstance(value,str) or not value:
            return INVALID_TRANSACTION_DIRECTION
        value = value.lower()
        if value not in ALLOWED_TRANSACTION_DIRECTIONS:
            return INVALID_TRANSACTION_DIRECTION

    if key == "status":
        if not isinstance(value,str) or not value:
            return INVALID_STATUS
        value = value.lower()
        if value not in ALLOWED_STATUSES:
            return INVALID_STATUS

    if key == "reference_number":
        if not isinstance(value,str) or not value:
            return INVALID_REFERENCE_NUMBER
        if not value.startswith("NVP"):
            return INVALID_REFERENCE_NUMBER
        if not value[3:].isnumeric():
            return INVALID_REFERENCE_NUMBER

    if key == "narration":
        if not isinstance(value,str) or not value:
            return INVALID_NARRATION
    if key == "created_at":
        if not isinstance(value,str) or not value:
            return INVALID_CREATED_AT
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return INVALID_CREATED_AT
        return value

    return value