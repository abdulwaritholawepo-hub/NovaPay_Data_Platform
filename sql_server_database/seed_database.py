import logging
import random
from datetime import datetime

from sqlalchemy import text

from config import logging_config
from sql_server_database.production_DB_connection import (
    production_database_engine_connection
)


logger = logging.getLogger(__name__)


CUSTOMER_DATA = [
    (
        "Abdulwarith",
        "Olawepo",
        "abdulwarith@novapay.com",
        "08031234560",
        "1999-04-12",
        "Male",
        "1000000001",
        125000.50,
        "Active",
        "2026-01-10 09:15:00"
    ),
    (
        "Amina",
        "Bello",
        "amina.bello@novapay.com",
        "08032345670",
        "1998-07-19",
        "Female",
        "1000000002",
        8540.00,
        "Active",
        "2026-01-11 10:20:00"
    ),
    (
        "Chinedu",
        "Okafor",
        "chinedu.okafor@novapay.com",
        "08033456780",
        "1997-11-25",
        "Male",
        "1000000003",
        15200.25,
        "Active",
        "2026-01-12 11:25:00"
    ),
    (
        "Fatima",
        "Abubakar",
        "fatima.abubakar@novapay.com",
        "08034567810",
        "1996-03-30",
        "Female",
        "1000000004",
        22100.50,
        "Active",
        "2026-01-13 12:30:00"
    ),
    (
        "Emeka",
        "Nwosu",
        "emeka.nwosu@novapay.com",
        "08035678101",
        "1995-08-15",
        "Male",
        "1000000005",
        35600.75,
        "Active",
        "2026-01-14 13:35:00"
    ),
    (
        "Zainab",
        "Yusuf",
        "zainab.yusuf@novapay.com",
        "08036789012",
        "1994-12-20",
        "Female",
        "1000000006",
        45200.00,
        "Active",
        "2026-01-15 14:40:00"
    ),
    (
        "Ibrahim",
        "Sani",
        "ibrahim.sani@novapay.com",
        "08037890123",
        "1993-06-10",
        "Male",
        "1000000007",
        55800.25,
        "Active",
        "2026-01-16 15:45:00"
    ),
    (
        "Aisha",
        "Mohammed",
        "aisha.mohammed@novapay.com",
        "08038901234",
        "1992-09-25",
        "Female",
        "1000000008",
        65400.50,
        "Active",
        "2026-01-17 16:50:00"
    ),
    (
        "Oluwaseun",
        "Adebayo",
        "oluwaseun.adebayo@novapay.com",
        "08039012345",
        "1991-02-10",
        "Male",
        "1000000009",
        75200.75,
        "Active",
        "2026-01-18 17:55:00"
    ),
    (
        "Maryam",
        "Abdullahi",
        "maryam.abdullahi@novapay.com",
        "08030123456",
        "1990-05-15",
        "Female",
        "1000000010",
        85400.00,
        "Active",
        "2026-01-19 18:01:00"
    ),
    (
        "Tunde",
        "Ogunleye",
        "tunde.ogunleye@novapay.com",
        "08031234567",
        "1989-11-20",
        "Male",
        "1000000011",
        95200.75,
        "Active",
        "2026-01-20 19:06:00"
    ),
    (
        "Halima",
        "Abubakar",
        "halima.abubakar@novapay.com",
        "08032345678",
        "1988-04-25",
        "Female",
        "1000000012",
        105400.00,
        "Active",
        "2026-01-21 20:30:00"
    ),
    (
        "Chukwuemeka",
        "Okeke",
        "chukwuemeka.okeke@novapay.com",
        "08033456089",
        "1987-07-30",
        "Male",
        "1000000013",
        115200.75,
        "Active",
        "2026-01-22 21:45:00"
    ),
    (
        "Aminat",
        "Adamu",
        "aminat.adamu@novapay.com",
        "08034567890",
        "1986-10-05",
        "Female",
        "1000000014",
        125400.00,
        "Active",
        "2026-01-23 22:10:00"
    ),
    (
        "Oluwafemi",
        "Akinyemi",
        "oluwafemi.akinyemi@novapay.com",
        "08035672901",
        "1985-01-10",
        "Male",
        "1000000015",
        135200.75,
        "Active",
        "2026-01-24 23:06:00"
    )
]


MERCHANT_DATA = [
    (
        "Shoprite Ikeja",
        "Supermarket",
        "shoprite@novapay.com",
        "07030000001",
        "Lagos",
        "Lagos",
        "2000000001",
        "Active",
        "2026-01-01 09:00:00"
    ),
    (
        "Jumia Online Store",
        "E-commerce",
        "jumia@novapay.com",
        "07030000002",
        "Lagos",
        "Lagos",
        "2000000002",
        "Active",
        "2026-01-02 10:00:00"
    ),
    (
        "Konga Online Store",
        "E-commerce",
        "konga@novapay.com",
        "07030000003",
        "Lagos",
        "Lagos",
        "2000000003",
        "Active",
        "2026-01-03 11:00:00"
    ),
    (
        "Shoprite Victoria Island",
        "Supermarket",
        "shoprite.victoria@novapay.com",
        "07030000004",
        "Lagos",
        "Lagos",
        "2000000004",
        "Active",
        "2026-01-04 12:00:00"
    ),
    (
        "Ebeano Supermarket",
        "Supermarket",
        "ebeano@novapay.com",
        "07030000005",
        "Lagos",
        "Lagos",
        "2000000005",
        "Active",
        "2026-01-05 13:00:00"
    ),
    (
        "MTN Nigeria",
        "Telecom",
        "mtn@novapay.com",
        "07030000006",
        "Lagos",
        "Lagos",
        "2000000006",
        "Active",
        "2026-01-06 14:00:00"
    ),
    (
        "Airtel Nigeria",
        "Telecom",
        "airtel@novapay.com",
        "07030000007",
        "Lagos",
        "Lagos",
        "2000000007",
        "Active",
        "2026-01-07 15:00:00"
    ),
    (
        "Glo Nigeria",
        "Telecom",
        "glo@novapay.com",
        "07030000009",
        "Lagos",
        "Lagos",
        "2000000009",
        "Active",
        "2026-01-08 16:00:00"
    ),
    (
        "Uber Nigeria",
        "Transport",
        "uber@novapay.com",
        "07030000008",
        "Lagos",
        "Lagos",
        "2000000026",
        "Active",
        "2026-01-09 17:00:00"
    ),
    (
        "Bolt Nigeria",
        "Transport",
        "bolt@novapay.com",
        "08030000010",
        "Lagos",
        "Lagos",
        "2000000037",
        "Active",
        "2026-01-02 18:00:00"
    )
]


def generate_customers():
    """Convert customer source data into database-ready dictionaries."""

    customers = []

    for customer in CUSTOMER_DATA:
        (
            first_name,
            last_name,
            email,
            phone_number,
            date_of_birth,
            gender,
            account_number,
            wallet_balance,
            account_status,
            created_at
        ) = customer

        customers.append({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "account_number": account_number,
            "wallet_balance": wallet_balance,
            "account_status": account_status,
            "created_at": created_at
        })

    return customers


def generate_merchants():
    """Convert merchant source data into database-ready dictionaries."""

    merchants = []

    for merchant in MERCHANT_DATA:
        (
            merchant_name,
            category,
            email,
            phone_number,
            city,
            state,
            account_number,
            merchant_status,
            created_at
        ) = merchant

        merchants.append({
            "merchant_name": merchant_name,
            "category": category,
            "email": email,
            "phone_number": phone_number,
            "city": city,
            "state": state,
            "account_number": account_number,
            "merchant_status": merchant_status,
            "created_at": created_at
        })

    return merchants


def generate_transactions(number_of_transactions=50):
    """Generate synthetic transaction records."""

    transactions = []

    transaction_amounts = [
        500.00,
        1200.00,
        2500.00,
        5000.00,
        12000.00,
        25500.00,
        80000.00
    ]

    payment_methods = [
        "wallet",
        "bank_transfer",
        "debit_card",
        "QR_code"
    ]

    transaction_categories = [
        "merchant_payment",
        "airtime_purchase",
        "data_purchase",
        "electricity_bill",
        "wallet_transfer"
    ]

    statuses = [
        "successful",
        "pending",
        "failed"
    ]

    narrations = [
        "grocery_shopping",
        "lunch_payment",
        "airtime_purchase",
        "electricity_bill",
        "wallet_transfer",
        "netflix_subscription",
        "uber_ride",
        "online_shopping"
    ]

    start_dt = datetime.strptime(
        "2026-01-01 00:00:00",
        "%Y-%m-%d %H:%M:%S"
    )

    end_dt = datetime.strptime(
        "2026-12-31 23:59:59",
        "%Y-%m-%d %H:%M:%S"
    )

    start_ts = start_dt.timestamp()
    end_ts = end_dt.timestamp()

    used_reference_numbers = set()

    for _ in range(number_of_transactions):

        random_ts = random.uniform(start_ts, end_ts)
        transaction_datetime = datetime.fromtimestamp(random_ts)

        while True:
            reference_number = (
                f"NVP{random.randint(200000, 999999)}"
            )

            if reference_number not in used_reference_numbers:
                used_reference_numbers.add(reference_number)
                break

        transaction = {
            "sender_id": random.randint(1, len(CUSTOMER_DATA)),
            "receiver_id": random.randint(1, len(MERCHANT_DATA)),
            "amount": random.choice(transaction_amounts),
            "receiver_type": "merchant",
            "currency": "NGN",
            "payment_method": random.choice(payment_methods),
            "transaction_category": random.choice(
                transaction_categories
            ),
            "transaction_direction": "debit",
            "status": random.choices(
                statuses,
                weights=[97, 2, 1],
                k=1
            )[0],
            "reference_number": reference_number,
            "narration": random.choice(narrations),
            "created_at": transaction_datetime
        }

        transactions.append(transaction)

    return transactions


def seed_database():
    """Seed the NovaPay production database."""

    logger.info("Starting NovaPay database seeding")

    customers = generate_customers()
    merchants = generate_merchants()
    transactions = generate_transactions()

    logger.info(
        "Generated %d customers, %d merchants and %d transactions",
        len(customers),
        len(merchants),
        len(transactions)
    )

    insert_customers = text("""
        INSERT INTO Customers (
            first_name,
            last_name,
            email,
            phone_number,
            date_of_birth,
            gender,
            account_number,
            wallet_balance,
            account_status,
            created_at
        )
        VALUES (
            :first_name,
            :last_name,
            :email,
            :phone_number,
            :date_of_birth,
            :gender,
            :account_number,
            :wallet_balance,
            :account_status,
            :created_at
        )
    """)

    insert_merchants = text("""
        INSERT INTO Merchants (
            merchant_name,
            category,
            email,
            phone_number,
            city,
            state,
            account_number,
            merchant_status,
            created_at
        )
        VALUES (
            :merchant_name,
            :category,
            :email,
            :phone_number,
            :city,
            :state,
            :account_number,
            :merchant_status,
            :created_at
        )
    """)

    insert_transactions = text("""
        INSERT INTO Transactions (
            sender_id,
            receiver_id,
            amount,
            receiver_type,
            currency,
            payment_method,
            transaction_category,
            transaction_direction,
            status,
            reference_number,
            narration,
            created_at
        )
        VALUES (
            :sender_id,
            :receiver_id,
            :amount,
            :receiver_type,
            :currency,
            :payment_method,
            :transaction_category,
            :transaction_direction,
            :status,
            :reference_number,
            :narration,
            :created_at
        )
    """)

    engine = production_database_engine_connection()

    logger.info("Production database engine created successfully")

    with engine.begin() as conn:

        logger.info("Inserting %d customers", len(customers))
        conn.execute(insert_customers, customers)

        logger.info("Inserting %d merchants", len(merchants))
        conn.execute(insert_merchants, merchants)

        logger.info("Inserting %d transactions", len(transactions))
        conn.execute(insert_transactions, transactions)

    logger.info("NovaPay database seeded successfully")


if __name__ == "__main__":
    seed_database()
