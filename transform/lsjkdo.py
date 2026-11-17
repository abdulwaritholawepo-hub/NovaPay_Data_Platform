
from datetime import datetime

test_event_types = [
    "customer_insert",
    "customer_update",
    "customer_delete"
]

event_metadata_keys = [
    "event_id",
    "event_type",
    "event_sequence",
    "effective_at",
    "recorded_at"
]

for test_type in test_event_types:
    test_event_record = {
        "event_id": 100,
        "event_type": test_type,
        "event_sequence": 1,
        "effective_at": datetime.now(),
        "recorded_at": datetime.now()
    }

    is_invalid = False

    for key in event_metadata_keys:
        value = test_event_record.get(key)

        if value is None:
            is_invalid = True
            break

        if key == "event_id":
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                is_invalid = True
                break

        elif key == "event_type":
            value = value.lower()
            if value != "customer_insert" and value != "customer_update":
                is_invalid = True
                break

        elif key == "event_sequence":
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                is_invalid = True
                break

        elif key in ("effective_at", "recorded_at"):
            if not isinstance(value, datetime):
                is_invalid = True
                break

    expected_invalid = test_type == "customer_delete"

    if is_invalid == expected_invalid:
        print(f"PASS: {test_type}")
    else:
        print(f"FAIL: {test_type}")
