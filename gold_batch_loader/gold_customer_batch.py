import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_batch_loader.gold_generic_batch_loader import generic_batch_loader
from gold_incremental_loader.gold_generic_incremental import DOMAIN_CONFIG
from silver_query.silver_generic_query import generic_silver_query
from gold_incremental_loader.gold_customer_incremental_loader import gold_customer_incremental_load
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from datetime import date
from decimal import Decimal
from collections import Counter

config = DOMAIN_CONFIG["customer"]
table_name = config["table"]
incoming_dim_customer = [
    {
        "customer_id": 1,
        "account_number": "1000000001",
        "first_name": "Abdulwarith",
        "last_name": "Olawepo",
        "full_name": "Abdulwarith Olawepo",
        "customer_initials": "AO",
        "gender": "Male",
        "date_of_birth": date(1999, 4, 12), 
        "age": 27,
        "is_adult": True,
        "eligibility": "Eligible",
        "customer_segment": "Adult",
        "phone_number": "+2348031234560", 
        "email_domain": "novapay.com",
        "duplicate_email": False,
        "account_status": "Active",
        "wallet_balance": Decimal("125000.50"),
        "wallet_segment": "High Value",
        "risk_level": "Medium",
        "risk_flag": "Normal",
        "created_at": "2026-09-24",
        "account_tenure_days": 255,
        "customer_lifetime_stage": "Established Customer",
    },
    {
        "customer_id": 1,
        "account_number": "1000000001",
        "first_name": "Abdulwarith",
        "last_name": "Olawepo",
        "full_name": "Abdulwarith Olawepo",
        "customer_initials": "AO",
        "gender": "Male",
        "date_of_birth": date(1999, 4, 12),
        "age": 27,
        "is_adult": True,
        "eligibility": "Eligible",
        "customer_segment": "Adult",
        "phone_number": "+2348031234560",
        "email_domain": "novapay.com",
        "duplicate_email": False,
        "account_status": "Active",
        "wallet_balance": 75000,
        "wallet_segment": "High Value",
        "risk_level": "Medium",
        "risk_flag": "Normal",
        "created_at": "2026-09-24",
        "account_tenure_days": 255,
        "customer_lifetime_stage": "Established Customer",
    },
    {
        "customer_id": 999,
        "account_number": "1999999999",
        "first_name": "Test",
        "last_name": "Customer",
        "full_name": "Test Customer",
        "customer_initials": "TC",
        "gender": "Male",
        "date_of_birth": date(1995, 1, 1),
        "age": 31,
        "is_adult": True,
        "eligibility": "Eligible",
        "customer_segment": "Standard",
        "phone_number": "08009999999",
        "email_domain": "gmail.com",
        "duplicate_email": False,
        "account_status": "Active",
        "wallet_balance": 25000,
        "wallet_segment": "Medium",
        "risk_level": "Low",
        "risk_flag": "Normal",
        "created_at": "2026-10-04",
        "account_tenure_days": 0,
        "customer_lifetime_stage": "Established Customer",
    },
]
gold_customer_column_order = [
    
    'customer_id',
    'account_number',
    'first_name',
    'last_name',
    'full_name',
    'customer_initials',
    'gender',
    'date_of_birth',
    'age',
    'is_adult',
    'eligibility',
    'customer_segment',
    'phone_number',
    'email_domain',
    'duplicate_email',
    'account_status',
    'wallet_balance',
    'wallet_segment',
    'risk_level',
    'risk_flag',
    'created_at',
    'account_tenure_days',
    'customer_lifetime_stage'
    ]

tracked_attributes = [
    "first_name",
    "last_name",
    "gender",
    "date_of_birth",
    "phone_number",
    "email_domain",
    "account_status",
    "eligibility",
    "customer_segment",
    "wallet_balance",
    "wallet_segment",
    "risk_level",
    "risk_flag",
    "customer_lifetime_stage",
]
cust_list = []
for cust in incoming_dim_customer:
    cust_list.append(cust.get("customer_id"))
frequencies = Counter(cust_list)

duplicates_counts = {item: count 
                    for item, count in frequencies.items()
                    if count > 1}
print(duplicates_counts)

engine = analytics_database_engine_connection()
incoming_dim_customer = incoming_dim_customer

with engine.begin() as conn:
    gold_dim_customer = conn.execute(text(f"""
    select *
    from gold.dim_customer
    where is_current = 1
    """)).mappings().all()

print("Total current Gold records:", len(gold_dim_customer))

print(
    "Current Gold customer IDs:",
    [gold_dim.get("customer_id") for gold_dim in gold_dim_customer]
)

customer_1_exists = any(
    gold_dim.get("customer_id") == 1
    for gold_dim in gold_dim_customer
)

print("Does customer 1 exist in current Gold records?", customer_1_exists)
new_dim_customer_list = []
changed_dim_customer_list = []
unchanged_dim_customer_list = []

for new_customer in incoming_dim_customer:
    current_dim = None

    for gold_dim in gold_dim_customer:
        if new_customer.get("customer_id") == gold_dim.get("customer_id"):
            current_dim = gold_dim
            break

    if current_dim is None:
        new_dim_customer_list.append(new_customer)
        continue

    has_changes = False

    for att in tracked_attributes:
        if new_customer.get(att) != current_dim.get(att):
            has_changes = True
            print(
                f"Customer {new_customer['customer_id']} changed: "
                f"{att} | "
                f"incoming={new_customer.get(att)} | "
                f"gold={current_dim.get(att)}"
            )
            break

    if has_changes:
        changed_dim_customer_list.append(new_customer)
    else:
        unchanged_dim_customer_list.append(current_dim)

print("Unchanged customers:", len(unchanged_dim_customer_list))
print("Changed customers:", len(changed_dim_customer_list))
print("New customers:", len(new_dim_customer_list))


def process_changed_customers(changed_dim_customer):
    update_query = text("""
        UPDATE gold.dim_customer
            SET valid_to = sysdatetime(), is_current = 0
           where customer_id = :customer_id and is_current = :is_current
        
     """)
    columns = ", ".join(gold_customer_column_order)
    parameters = ", ".join(
        f":{column}" for column in gold_customer_column_order
    )

    insert_query = text(f"""
        INSERT INTO gold.dim_customer
        (
            {columns},
            valid_from,
            valid_to,
            is_current
        )
        VALUES
        (
            {parameters},
            SYSDATETIME(),
            NULL,
            1
        )
    """)

    with engine.begin() as conn:
        for changed_dim in changed_dim_customer:
            print(changed_dim.get("customer_id"))
            
            update_row_count = conn.execute(update_query, {"customer_id":changed_dim.get('customer_id'),"is_current":1}).rowcount
            if update_row_count == 1:
                insert_row_count = conn.execute(insert_query,changed_dim)
            else:
                raise ValueError(
                    f"error caused by {changed_dim.get('customer_id')} from row {update_row_count}")

            
def gold_customer_batch_loader():
    loader = generic_batch_loader(table_name=table_name,
                                   column_order= gold_customer_column_order,
                                   transformed_data= new_dim_customer_list,
                                   domain="customer",
                                   schema='gold.'
                                   )
    return loader
