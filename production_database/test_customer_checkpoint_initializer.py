import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from production_database.production_DB_connection import production_database_engine_connection
from production_database.customer_creation import create_customer

from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4


production_engine = production_database_engine_connection()

unique_id = uuid4().hex[:10]

customer_data = {
    "first_name": "Test",
    "last_name": "Checkpoint",
    "email": f"checkpoint_test_{unique_id}@novapay.com",
    "phone_number": "08039999999",
    "date_of_birth": date(1998, 5, 12),
    "gender": "Male",
    "account_number": f"9{uuid4().int % 1_000_000_000:09d}",
    "wallet_balance": Decimal("25000.00"),
    "account_status": "Active",
    "created_at": datetime.now()
}

try:
    with production_engine.begin() as conn:
        customer_id = create_customer(
            conn=conn,
            customer_data=customer_data
        )

    if customer_id is None:
        raise ValueError("Customer creation failed: duplicate account number.")

    print(f"Test customer created successfully. Customer ID: {customer_id}")

finally:
    production_engine.dispose()
