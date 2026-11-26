import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, datetime, timedelta

from transform.customer_transformer_helper import (
    calculate_account_tenure,
    INVALID_ACCOUNT_DATE
)


def run_test(test_name, created_at, dob, reference_date, expected):
    try:
        result = calculate_account_tenure(
            created_at,
            dob,
            reference_date
        )

        assert result == expected, (
            f"Expected {expected}, got {result}"
        )

        print(f"PASS: {test_name}")

    except AssertionError as error:
        print(f"FAIL: {test_name} - {error}")

    except Exception as error:
        print(f"FAIL: {test_name} - {type(error).__name__}: {error}")


today = date(2026, 11, 19)


# 1. Missing account creation date
run_test(
    "Missing created_at",
    None, None, today,
    (None, "Unknown")
)


# 2. All five customer lifetime stages
stage_cases = [
    (0, "New Customer"),
    (30, "New Customer"),
    (31, "Growing Customer"),
    (180, "Growing Customer"),
    (181, "Established Customer"),
    (365, "Established Customer"),
    (366, "Loyal Customer"),
    (1095, "Loyal Customer"),
    (1096, "Veteran Customer"),
]

for days, expected_stage in stage_cases:
    created = datetime.combine(today - timedelta(days=days),
                               datetime.min.time())

    run_test(
        f"Tenure boundary: {days} days",
        created, None, today,
        (days, expected_stage)
    )


# 3. Reference date supplied as datetime
run_test(
    "Datetime reference date",
    datetime(2026, 11, 1, 10, 0),
    None,
    datetime(2026, 11, 19, 15, 30),
    (18, "New Customer")
)


# 4. Reference date supplied as date
run_test(
    "Date reference date",
    datetime(2026, 11, 1, 10, 0),
    None,
    today,
    (18, "New Customer")
)


# 5. Missing DOB
run_test(
    "Missing DOB",
    datetime(2026, 11, 1, 10, 0),
    None,
    today,
    (18, "New Customer")
)


# 6. Account created before DOB
run_test(
    "Account created before DOB",
    datetime(1999, 1, 1),
    date(2000, 1, 1),
    today,
    (INVALID_ACCOUNT_DATE, "Unknown")
)


# 7. Account created after reference date
run_test(
    "Future account creation date",
    datetime(2026, 11, 20),
    None,
    today,
    (INVALID_ACCOUNT_DATE, "Unknown")
)


# 8. Invalid reference date type
try:
    calculate_account_tenure(
        datetime(2026, 11, 1),
        None,
        "2026-11-19"
    )
    print("FAIL: Invalid reference date type was accepted")

except TypeError:
    print("PASS: Invalid reference date type rejected")

except Exception as error:
    print(f"FAIL: Unexpected exception - {error}")


print("\nTesting completed.")
