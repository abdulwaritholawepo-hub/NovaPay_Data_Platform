
from datetime import date, datetime
from decimal import Decimal

customer_snapshot_keys = [
    "customer_id",
    "first_name",
    "last_name",
    "gender",
    "date_of_birth",
    "phone_number",
    "email",
    "wallet_balance",
    "account_number",
    "account_status",
    "created_at"
]

text_fields = [
    "first_name",
    "last_name",
    "gender",
    "phone_number",
    "email",
    "account_number",
    "account_status"
]


def validate_customer_snapshot(customer_snapshot):
    is_invalid = False

    for key in customer_snapshot_keys:
        value = customer_snapshot.get(key)

        if value is None:
            is_invalid = True
            break

        if key in text_fields:
            if not isinstance(value, str) or not value.strip():
                is_invalid = True
                break

        elif key == "customer_id":
            if not isinstance(value, int) or isinstance(value, bool):
                is_invalid = True
                break

        elif key == "wallet_balance":
            if not isinstance(value, (int, float, Decimal)) or isinstance(value, bool):
                is_invalid = True
                break

        elif key == "date_of_birth":
            if not isinstance(value, date) or isinstance(value, datetime):
                is_invalid = True
                break

        elif key == "created_at":
            if not isinstance(value, datetime):
                is_invalid = True
                break

    return is_invalid


valid_snapshot = {
    "customer_id": 19,
    "first_name": "Test",
    "last_name": "Customer",
    "gender": "Male",
    "date_of_birth": date(1999, 4, 12),
    "phone_number": "08031234560",
    "email": "test@novapay.com",
    "wallet_balance": Decimal("125000.50"),
    "account_number": "1234567890",
    "account_status": "Active",
    "created_at": datetime(2026, 1, 10, 9, 15)
}


test_cases = []

# 1. Valid snapshot
test_cases.append(("Valid snapshot", valid_snapshot.copy(), False))

# 2. Missing required field
test_data = valid_snapshot.copy()
test_data["email"] = None
test_cases.append(("Missing required field", test_data, True))

# 3. Empty text field
test_data = valid_snapshot.copy()
test_data["first_name"] = "   "
test_cases.append(("Empty text field", test_data, True))

# 4. Incorrect text-field type
test_data = valid_snapshot.copy()
test_data["phone_number"] = 8031234560
test_cases.append(("Incorrect text-field type", test_data, True))

# 5. Invalid customer_id
test_data = valid_snapshot.copy()
test_data["customer_id"] = True
test_cases.append(("Invalid customer_id", test_data, True))

# 6. Invalid wallet_balance
test_data = valid_snapshot.copy()
test_data["wallet_balance"] = True
test_cases.append(("Invalid wallet_balance", test_data, True))

# 7. Invalid date_of_birth
test_data = valid_snapshot.copy()
test_data["date_of_birth"] = "1999-04-12"
test_cases.append(("Invalid date_of_birth", test_data, True))

# 8. Invalid created_at
test_data = valid_snapshot.copy()
test_data["created_at"] = date(2026, 1, 10)
test_cases.append(("Invalid created_at", test_data, True))


for test_name, test_snapshot, expected_invalid in test_cases:

    actual_invalid = validate_customer_snapshot(test_snapshot)

    if actual_invalid == expected_invalid:
        print(f"PASS: {test_name}")
    else:
        print(
            f"FAIL: {test_name} | "
            f"Expected invalid={expected_invalid}, "
            f"Got invalid={actual_invalid}"
        )
