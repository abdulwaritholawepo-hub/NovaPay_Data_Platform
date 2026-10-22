import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from concurrent.futures import ThreadPoolExecutor
from production_database.update_db import update


def main():
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                update,
                customer_id=2,
                phone_number="09123637111",
                wallet_balance=125000,
                account_status="active",
            ),
            executor.submit(
                update,
                customer_id=2,
                phone_number="09123637122",
                wallet_balance=1350000,
                account_status="closed",
            ),
        ]

        errors = []

        for index, future in enumerate(futures, start=1):
            try:
                future.result()
                print(f"Update {index}: completed successfully")
            except Exception as exc:
                errors.append((index, exc))
                print(f"Update {index}: FAILED — {exc!r}")

        if errors:
            raise RuntimeError(
                f"{len(errors)} concurrent update(s) failed."
            ) from errors[0][1]

        print("Both concurrent updates completed successfully.")


if __name__ == "__main__":
    main()
