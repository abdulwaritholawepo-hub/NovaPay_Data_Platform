import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, datetime

from transform.customer_transformer_helper import (
    calculate_age,
    get_customer_segment,
    get_customer_age_details,
    calculate_account_tenure,
    INVALID_AGE,
    INVALID_ACCOUNT_DATE
)


# ==========================================
# 1. TEST calculate_age()
# ==========================================

def test_calculate_age():

    reference_date = date(2026, 11, 24)

    assert calculate_age(None, reference_date) == INVALID_AGE

    assert calculate_age(
        date(2000, 5, 10), reference_date
    ) == 26

    assert calculate_age(
        datetime(2000, 5, 10, 14, 30), reference_date
    ) == 26

    assert calculate_age(
        "2000-05-10", reference_date
    ) == INVALID_AGE

    assert calculate_age(
        date(2026, 12, 10), reference_date
    ) == INVALID_AGE

    assert calculate_age(
        date(1900, 1, 1), reference_date
    ) == INVALID_AGE

    print("calculate_age: ALL TESTS PASSED")


# ==========================================
# 2. TEST get_customer_segment()
# ==========================================

def test_get_customer_segment():

    test_cases = [
        (0, "Minor"),
        (17, "Minor"),
        (18, "Young Adult"),
        (25, "Young Adult"),
        (26, "Adult"),
        (40, "Adult"),
        (41, "Middle Aged"),
        (60, "Middle Aged"),
        (61, "Senior"),
        (120, "Senior"),
        (None, "Unknown"),
        (-1, "Unknown"),
        (121, "Unknown")
    ]

    for age, expected in test_cases:
        assert get_customer_segment(age) == expected

    print("get_customer_segment: ALL TESTS PASSED")


# ==========================================
# 3. TEST get_customer_age_details()
# ==========================================

def test_get_customer_age_details():

    reference_date = date(2026, 11, 24)

    # Missing date of birth
    assert get_customer_age_details(
        None, reference_date
    ) == ("Unknown", None, "Not Eligible", "Unknown")

    # Adult customer
    assert get_customer_age_details(
        date(2000, 5, 10), reference_date
    ) == (26, True, "Eligible", "Adult")

    # Minor customer
    assert get_customer_age_details(
        date(2010, 5, 10), reference_date
    ) == (16, False, "Not Eligible", "Minor")

    # Datetime DOB
    assert get_customer_age_details(
        datetime(2000, 5, 10, 14, 30), reference_date
    ) == (26, True, "Eligible", "Adult")

    # Invalid DOB
    assert get_customer_age_details(
        "2000-05-10", reference_date
    ) == (INVALID_AGE, None, "Not Eligible", "Unknown")

    print("get_customer_age_details: ALL TESTS PASSED")


# ==========================================
# 4. TEST calculate_account_tenure()
# ==========================================

def test_calculate_account_tenure():

    reference_date = date(2026, 11, 24)
    dob = date(1995, 5, 10)

    test_cases = [
        (
            datetime(2026, 10, 25),
            30,
            "New Customer"
        ),
        (
            datetime(2026, 5, 28),
            180,
            "Growing Customer"
        ),
        (
            datetime(2025, 11, 24),
            365,
            "Established Customer"
        ),
        (
            datetime(2025, 11, 23),
            366,
            "Loyal Customer"
        ),
        (
            datetime(2023, 11, 24),
            1096,
            "Veteran Customer"
        )
    ]

    for created_at, expected_days, expected_stage in test_cases:

        result = calculate_account_tenure(
            created_at,
            dob,
            reference_date
        )

        assert result == (expected_days, expected_stage)

    # Missing creation date
    assert calculate_account_tenure(
        None, dob, reference_date
    ) == (None, "Unknown")

    # Invalid creation date type
    assert calculate_account_tenure(
        "2026-10-25", dob, reference_date
    ) == (INVALID_ACCOUNT_DATE, "Unknown")

    # Account created before date of birth
    assert calculate_account_tenure(
        datetime(1990, 1, 1),
        dob,
        reference_date
    ) == (INVALID_ACCOUNT_DATE, "Unknown")

    # Account created after reference date
    assert calculate_account_tenure(
        datetime(2026, 12, 1),
        dob,
        reference_date
    ) == (INVALID_ACCOUNT_DATE, "Unknown")

    print("calculate_account_tenure: ALL TESTS PASSED")


# ==========================================
# RUN ALL FOUR TEST FUNCTIONS
# ==========================================

if __name__ == "__main__":

    test_calculate_age()
    test_get_customer_segment()
    test_get_customer_age_details()
    test_calculate_account_tenure()

    print("\nALL FOUR HELPER FUNCTIONS PASSED.")
