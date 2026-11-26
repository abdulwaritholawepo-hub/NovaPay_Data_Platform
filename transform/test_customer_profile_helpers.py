import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer_helper import (
    get_full_name,
    get_customer_initials,
    get_email_domain,
    get_wallet_segment,
    get_risk_details,
    INVALID_EMAIL_ADDRESS
)


# ==========================================
# 1. TEST get_full_name()
# ==========================================

def test_get_full_name():

    test_cases = [
        ("Abdulwarith", "Olawepo", "Abdulwarith Olawepo"),
        ("John", "Doe", "John Doe"),
        (None, "Doe", "Unknown"),
        ("John", None, "Unknown"),
        (None, None, "Unknown"),
        ("", "Doe", "Unknown")
    ]

    for first_name, last_name, expected in test_cases:
        assert get_full_name(first_name, last_name) == expected

    print("get_full_name: ALL TESTS PASSED")


# ==========================================
# 2. TEST get_customer_initials()
# ==========================================

def test_get_customer_initials():

    test_cases = [
        ("Abdulwarith", "Olawepo", "AO"),
        ("John", "Doe", "JD"),
        ("mary", "jones", "MJ"),
        (None, "Doe", "Unknown"),
        ("John", None, "Unknown"),
        (None, None, "Unknown"),
        ("", "Doe", "Unknown")
    ]

    for first_name, last_name, expected in test_cases:
        assert get_customer_initials(first_name, last_name) == expected

    print("get_customer_initials: ALL TESTS PASSED")


# ==========================================
# 3. TEST get_email_domain()
# ==========================================

def test_get_email_domain():

    test_cases = [
        ("user@gmail.com", "gmail.com"),
        ("user@yahoo.com", "yahoo.com"),
        ("admin@company.org", "company.org"),
        (None, None),
        ("", None),
        (INVALID_EMAIL_ADDRESS, None)
    ]

    for email, expected in test_cases:
        assert get_email_domain(email) == expected

    print("get_email_domain: ALL TESTS PASSED")


# ==========================================
# 4. TEST get_wallet_segment()
# ==========================================

def test_get_wallet_segment():

    test_cases = [
        (0, "Low Value"),
        (10000, "Low Value"),
        (10000.01, "Medium Value"),
        (100000, "Medium Value"),
        (100000.01, "High Value"),
        (500000, "High Value"),
        (500000.01, "Premium"),
        (8000000, "Premium"),
        (None, "Unknown")
    ]

    for wallet_balance, expected in test_cases:
        assert get_wallet_segment(wallet_balance) == expected

    print("get_wallet_segment: ALL TESTS PASSED")


# ==========================================
# 5. TEST get_risk_details()
# ==========================================

def test_get_risk_details():

    test_cases = [
        ("Inactive", 8000000, ("Very High", "Review Required")),
        ("Inactive", 7999999, ("High", "Review Required")),
        ("Inactive", 500000, ("Medium", "Normal")),
        ("Active", 100000, ("Low", "Normal")),
        ("Active", 100001, ("Medium", "Normal")),
        ("Active", 500000, ("Medium", "Normal")),
        ("Active", 500001, ("Low", "Normal")),
        ("Unknown", 10000000, ("Unknown", "Unknown")),
        ("Active", None, ("Unknown", "Unknown")),
        ("Unknown", None, ("Unknown", "Unknown"))
    ]

    for account_status, wallet_balance, expected in test_cases:

        actual = get_risk_details(account_status, wallet_balance)

        print(
            f"Status: {account_status}, "
            f"Balance: {wallet_balance}, "
            f"Expected: {expected}, "
            f"Actual: {actual}"
        )

        assert actual == expected

    print("get_risk_details: ALL TESTS PASSED")


# ==========================================
# RUN ALL FIVE TEST FUNCTIONS
# ==========================================

if __name__ == "__main__":

    test_get_full_name()
    test_get_customer_initials()
    test_get_email_domain()
    test_get_wallet_segment()
    test_get_risk_details()

    print("\nALL FIVE HELPER FUNCTIONS PASSED.")
