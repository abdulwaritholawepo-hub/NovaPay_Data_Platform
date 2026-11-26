import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import math

from transform.customer_transformer_helper import (
    clean_phone_number, INVALID_PHONE_NUMBER
    )


def test_clean_phone_number():

    test_cases = [
        # Valid numbers starting with 0
        ("08012345678", "+2348012345678"),
        ("07012345678", "+2347012345678"),
        ("09012345678", "+2349012345678"),
        ("08112345678", "+2348112345678"),

        # Valid numbers starting with 234
        ("2348012345678", "+2348012345678"),
        ("2347012345678", "+2347012345678"),

        # Valid numbers already starting with +234
        ("+2348012345678", "+2348012345678"),
        ("+2347012345678", "+2347012345678"),

        # Formatting variations
        ("080-1234-5678", "+2348012345678"),
        ("080 1234 5678", "+2348012345678"),
        ("(080) 1234 5678", "+2348012345678"),
        ("080-123-45678", "+2348012345678"),
        ("+234-801-234-5678", "+2348012345678"),

        # Invalid lengths
        ("0801234567", INVALID_PHONE_NUMBER),
        ("080123456789", INVALID_PHONE_NUMBER),
        ("234801234567", INVALID_PHONE_NUMBER),
        ("+234801234567", INVALID_PHONE_NUMBER),

        # Invalid prefixes
        ("07012345678", "+2347012345678"),
        ("+2349012345678", "+2349012345678"),
        ("12345678901", INVALID_PHONE_NUMBER),
        ("+1234567890123", INVALID_PHONE_NUMBER),

        # Invalid characters
        ("08012345ABC", INVALID_PHONE_NUMBER),
        ("08012345@78", INVALID_PHONE_NUMBER),
        ("abcdefghijk", INVALID_PHONE_NUMBER),

        # Empty and incomplete values
        ("", INVALID_PHONE_NUMBER),
        ("+", INVALID_PHONE_NUMBER),
        ("234", INVALID_PHONE_NUMBER),
    ]

    for value, expected in test_cases:
        actual = clean_phone_number(value)

        assert actual == expected, (
            f"Input: {value!r}, Expected: {expected}, Actual: {actual}"
        )

    print(f"All {len(test_cases)} phone number tests passed!")


if __name__ == "__main__":
    test_clean_phone_number()
