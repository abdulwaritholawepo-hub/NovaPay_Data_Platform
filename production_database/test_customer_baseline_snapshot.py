import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from production_database.customer_baseline_snapshot import (
    get_customer_baseline_snapshot,
)

baseline_snapshot = get_customer_baseline_snapshot()

print("Snapshot timestamp:", baseline_snapshot["snapshot_at"])
print(
    "Customer count:",
    len(baseline_snapshot["customer_snapshot_list"])
)
print(
    "First customer:",
    baseline_snapshot["customer_snapshot_list"][0]
)
