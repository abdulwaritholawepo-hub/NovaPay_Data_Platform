from sqlalchemy import text
from analytics_DB_connection import analytics_database_engine_connection

engine = analytics_database_engine_connection()

with engine.begin() as conn:
    conn.execute(
        text("""
            IF OBJECT_ID('dbo.customers', 'U') IS NULL
            BEGIN
            CREATE TABLE customers(
                customer_id INT PRIMARY KEY,
                account_number VARCHAR(10) UNIQUE NOT NULL,
                first_name VARCHAR(50) NULL,
                last_name VARCHAR(50) NULL,
                full_name VARCHAR(100) NULL,
                customer_initials VARCHAR(2) NULL,
                gender VARCHAR(20) NULL,
                date_of_birth DATE NULL,
                age INT NULL,
                is_adult BIT NULL,
                eligibility VARCHAR(50) NULL,
                customer_segment VARCHAR(50) NULL,
                phone_number VARCHAR(20) NULL,
                email VARCHAR(255) NULL,
                email_domain VARCHAR(100) NULL,
                duplicate_email BIT NULL,
                account_status VARCHAR(30) NULL,
                wallet_balance DECIMAL(18,2) NULL,
                wallet_segment VARCHAR(50) NULL,
                risk_level VARCHAR(30) NULL,
                risk_flag BIT NULL,
                created_at DATETIME2 NULL,
                account_tenure_days INT NULL,
                customer_lifetime_stage VARCHAR(50) NULL

            )
            END
            """)
            )
print("table created succesfully")