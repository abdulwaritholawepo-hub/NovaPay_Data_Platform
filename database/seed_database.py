from sqlalchemy import create_engine, text
import pyodbc
from urllib.parse import quote_plus
import random
from datetime import datetime
connection_string = quote_plus(
    r"DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=DESKTOP-HIGKAHM\SQLEXPRESS;"
    r"DATABASE=NovaPayDB;"
    r"Trusted_Connection=yes;"
    r"TrustServerCertificate=yes;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")

customers = [{
    "first_name": "Abdulwarith",
    "last_name": "Olawepo",
    "email": "abdulwarith@novapay.com",
    "phone_number": "08031234560",
    "date_of_birth": "1999-04-12",
    "gender": "Male",
    "account_number": "1000000001",
    "wallet_balance": 125000.50,
    "account_status": "Active",
    "created_at": "2026-01-10 09:15:00"
},
{
    "first_name": "Amina",
    "last_name": "Bello",
    "email": "amina.bello@novapay.com",
    "phone_number": "08032345670",
    "date_of_birth": "1998-07-19",
    "gender": "Female",
    "account_number": "1000000002",
    "wallet_balance": 8540.00,
    "account_status": "Active",
    "created_at": "2026-01-11 10:20:00"
},
{
    "first_name": "Chinedu",
    "last_name": "Okafor",
    "email": "chinedu.okafor@novapay.com",
    "phone_number": "08033456780",
    "date_of_birth": "1997-11-25",
    "gender": "Male",
    "account_number": "1000000003",
    "wallet_balance": 15200.25,
    "account_status": "Active",
    "created_at": "2026-01-12 11:25:00"
},
{
    "first_name": "Fatima",
    "last_name": "Abubakar",
    "email": "fatima.abubakar@novapay.com",
    "phone_number": "08034567810",
    "date_of_birth": "1996-03-30",
    "gender": "Female",
    "account_number": "1000000004",
    "wallet_balance": 22100.50,
    "account_status": "Active",
    "created_at": "2026-01-13 12:30:00"
},
{
    "first_name": "Emeka",
    "last_name": "Nwosu",
    "email": "emeka.nwosu@novapay.com",
    "phone_number": "08035678101",
    "date_of_birth": "1995-08-15",
    "gender": "Male",
    "account_number": "1000000005",
    "wallet_balance": 35600.75,
    "account_status": "Active",
    "created_at": "2026-01-14 13:35:00"
},
{
    "first_name": "Zainab",
    "last_name": "Yusuf",
    "email": "zainab.yusuf@novapay.com",
    "phone_number": "08036789012",
    "date_of_birth": "1994-12-20",
    "gender": "Female",
    "account_number": "1000000006",
    "wallet_balance": 45200.00,
    "account_status": "Active",
    "created_at": "2026-01-15 14:40:00"
},
{
    "first_name": "Ibrahim",
    "last_name": "Sani",
    "email": "ibrahim.sani@novapay.com",
    "phone_number": "08037890123",
    "date_of_birth": "1993-06-10",
    "gender": "Male",
    "account_number": "1000000007",
    "wallet_balance": 55800.25,
    "account_status": "Active",
    "created_at": "2026-01-16 15:45:00"
},
{
    "first_name": "Aisha",
    "last_name": "Mohammed",
    "email": "aisha.mohammed@novapay.com",
    "phone_number": "08038901234",
    "date_of_birth": "1992-09-25",
    "gender": "Female",
    "account_number": "1000000008",
    "wallet_balance": 65400.50,
    "account_status": "Active",
    "created_at": "2026-01-17 16:50:00"
},
{
    "first_name": "Oluwaseun",
    "last_name": "Adebayo",
    "email": "oluwaseun.adebayo@novapay.com",
    "phone_number": "08039012345",
    "date_of_birth": "1991-02-10",
    "gender": "Male",
    "account_number": "1000000009",
    "wallet_balance": 75200.75,
    "account_status": "Active",
    "created_at": "2026-01-18 17:55:00"
},
{
    "first_name": "Maryam",
    "last_name": "Abdullahi",
    "email": "maryam.abdullahi@novapay.com",
    "phone_number": "08030123456",
    "date_of_birth": "1990-05-15",
    "gender": "Female",
    "account_number": "1000000010",
    "wallet_balance": 85400.00,
    "account_status": "Active",
    "created_at": "2026-01-19 18:01:00"
},
{
    "first_name": "Tunde",
    "last_name": "Ogunleye",
    "email": "tunde.ogunleye@novapay.com",
    "phone_number": "08031234567",
    "date_of_birth": "1989-11-20",
    "gender": "Male",
    "account_number": "1000000011",
    "wallet_balance": 95200.75,
    "account_status": "Active",
    "created_at": "2026-01-20 19:06:00"
},
{
    "first_name": "Halima",
    "last_name": "Abubakar",
    "email": "halima.abubakar@novapay.com",
    "phone_number": "08032345678",
    "date_of_birth": "1988-04-25",
    "gender": "Female",
    "account_number": "1000000012",
    "wallet_balance": 105400.00,
    "account_status": "Active",
    "created_at": "2026-01-21 20:30:00"
},
{
    "first_name": "Chukwuemeka",
    "last_name": "Okeke",
    "email": "chukwuemeka.okeke@novapay.com",
    "phone_number": "08033456089",
    "date_of_birth": "1987-07-30",
    "gender": "Male",
    "account_number": "1000000013",
    "wallet_balance": 115200.75,
    "account_status": "Active",
    "created_at": "2026-01-22 21:45:00"
},
{
    "first_name": "Aminat",
    "last_name": "Adamu",
    "email": "aminat.adamu@novapay.com",
    "phone_number": "08034567890",
    "date_of_birth": "1986-10-05",
    "gender": "Female",
    "account_number": "1000000014",
    "wallet_balance": 125400.00,
    "account_status": "Active",
    "created_at": "2026-01-23 22:10:00"
},
{
    "first_name": "Oluwafemi",
    "last_name": "Akinyemi",
    "email": "oluwafemi.akinyemi@novapay.com",
    "phone_number": "08035672901",
    "date_of_birth": "1985-01-10",
    "gender": "Male",
    "account_number": "1000000015",
    "wallet_balance": 135200.75,
    "account_status": "Active",
    "created_at": "2026-01-24 23:06:00"
}
]

merchants = [
    {
        "merchant_name": "Shoprite Ikeja",
        "category": "Supermarket",
        "email": "shoprite@novapay.com",
        "phone_number": "07030000001",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000001",
        "merchant_status": "Active",
        "created_at": "2026-01-01 09:00:00"
    },
    {
        "merchant_name": "Jumia Online Store",
        "category": "E-commerce",
        "email": "jumia@novapay.com",
        "phone_number": "07030000002",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000002",
        "merchant_status": "Active",
        "created_at": "2026-01-02 10:00:00"
    },
    {
        "merchant_name": "Konga Online Store",
        "category": "E-commerce",
        "email": "konga@novapay.com",
        "phone_number": "07030000003",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000003",
        "merchant_status": "Active",
        "created_at": "2026-01-03 11:00:00"
    },
    {
        "merchant_name": "Shoprite Victoria Island",
        "category": "Supermarket",
        "email": "shoprite.victoria@novapay.com",
        "phone_number": "07030000004",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000004",
        "merchant_status": "Active",
        "created_at": "2026-01-04 12:00:00"
    },
    {
        "merchant_name": "Ebeano Supermarket",
        "category": "Supermarket", 
        "email": "ebeano@novapay.com",
        "phone_number": "07030000005",
        "city": "Lagos",  
        "state": "Lagos",
        "account_number": "2000000005",
        "merchant_status": "Active",
        "created_at": "2026-01-05 13:00:00"
    },
    {
        "merchant_name": "MTN Nigeria",
        "category": "Telecom",
        "email": "mtn@novapay.com",
        "phone_number": "07030000006",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000006",
        "merchant_status": "Active",
        "created_at": "2026-01-06 14:00:00"
    },
    {
        "merchant_name": "Airtel Nigeria",
        "category": "Telecom",
        "email": "airtel@novapay.com",
        "phone_number": "07030000007",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000007",
        "merchant_status": "Active",
        "created_at": "2026-01-07 15:00:00"
    },
    {
        "merchant_name": "Glo Nigeria",
        "category": "Telecom",
        "email": "glo@novapay.com",
        "phone_number": "07030000009",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000009",
        "merchant_status": "Active",
        "created_at": "2026-01-08 16:00:00"
    },
    {
        "merchant_name": "Uber Nigeria",
        "category": "Transport",
        "email": "uber@novapay.com",
        "phone_number": "07030000008",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000026",
        "merchant_status": "Active",
        "created_at": "2026-01-09 17:00:00"
    },
    {
        "merchant_name": "Bolt Nigeria",
        "category": "Transport",
        "email": "bolt@novapay.com",
        "phone_number": "08030000010",
        "city": "Lagos",
        "state": "Lagos",
        "account_number": "2000000037",
        "merchant_status": "Active",
        "created_at": "2026-01-02 18:00:00"
    }
]
transactions = []
print(len(customers))
print(len(merchants))


transaction_amount = [500.00, 1200.00, 2500.00, 5000.00, 12000.00, 25500.00, 80000.00]
payment_method = ["wallet", "bank_transfer", "debit_card","QR_code"]
transaction_category =["merchant_payment", "airtime_purchase","data_purchase","electricity_bill", "wallet_transfer"]
status = ["successful", "pending", "failed"]
narration = ['grocery_shopping', 'lunch_payment', 'airtime_purchase', 'electricity_bill','wallet_transfer', 'netflix_subscription','uber_ride', 'online_shopping']
receiver_type = "merchant"
currency = "NGN"
transaction_direction = "debit"

start_dt = datetime.strptime("2026-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
end_dt = datetime.strptime("2026-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
start_ts = start_dt.timestamp()
end_ts = end_dt.timestamp()

used_reference_numbers = set()


number_of_transactions = 50
for _ in range(number_of_transactions):
    
    random_ts = random.uniform(start_ts, end_ts)

    datetime_random = datetime.fromtimestamp(random_ts)
    while True:
        ref = f"NVP{random.randint(200000, 999999)}"
        if ref not in used_reference_numbers:
            used_reference_numbers.add(ref)
            
            break
    
    transaction = {
        "sender_id": random.randint(1, len(customers)),
        "receiver_id": random.randint(1, len(merchants)),
        "amount": random.choice(transaction_amount),
        "receiver_type": receiver_type,
        "currency": currency,
        "payment_method": random.choice(payment_method),
        "transaction_category": random.choice(transaction_category),
        "transaction_direction": transaction_direction,
        "status": random.choices(status,weights=[97, 2, 1], k=1)[0],
        "reference_number": ref,
        "narration": random.choice(narration),
        "created_at": datetime_random
        
    }
    transactions.append(transaction)

print(len(transactions))
print(len(used_reference_numbers))

insert_customers = text("""
INSERT INTO Customers (first_name, last_name, email, phone_number, date_of_birth, gender, account_number, wallet_balance, account_status, created_at)
VALUES (:first_name, :last_name, :email, :phone_number, :date_of_birth, :gender, :account_number, :wallet_balance, :account_status, :created_at)
""")
insert_merchants = text("""
INSERT INTO Merchants (merchant_name, category, email, phone_number, city, state, account_number, merchant_status, created_at)
VALUES (:merchant_name, :category, :email, :phone_number, :city, :state, :account_number, :merchant_status, :created_at)
""")
insert_transactions = text("""
INSERT INTO Transactions (sender_id, receiver_id, amount, receiver_type, currency, payment_method, transaction_category, transaction_direction, status, reference_number, narration, created_at)
VALUES (:sender_id, :receiver_id, :amount, :receiver_type, :currency, :payment_method, :transaction_category, :transaction_direction, :status, :reference_number, :narration, :created_at)
""")
with engine.begin() as conn:
    conn.execute(insert_customers, customers)
    conn.execute(insert_merchants, merchants)
    conn.execute(insert_transactions, transactions)
    print("Database seeded successfully.")
