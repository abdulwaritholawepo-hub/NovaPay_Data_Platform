from sqlalchemy import text
from analytics_DB_connection import analytics_database_engine_connection
import logging
from config import logging_config
logger = logging.getLogger(__name__)
engine = analytics_database_engine_connection()
logger.info("Analytics database engine created successfully")

with engine.begin() as conn:
    logger.info("Checking whether customers table exists")
    conn.execute(
        text("""
            IF OBJECT_ID('dbo.customers', 'U') IS NULL
            BEGIN
            CREATE TABLE customers(
                customer_id INT PRIMARY KEY NOT NULL,
                account_number VARCHAR(10) UNIQUE NOT NULL,
                first_name VARCHAR(50) NULL,
                last_name VARCHAR(50) NULL,
                full_name VARCHAR(100) NULL,
                customer_initials VARCHAR(2) NULL,
                gender VARCHAR(20) NULL,
                date_of_birth DATE NULL,
                age INT NULL,
                is_adult VARCHAR(50) NULL,
                eligibility VARCHAR(50) NULL,
                customer_segment VARCHAR(50) NULL,
                phone_number VARCHAR(20) NULL,
                email VARCHAR(255) NULL,
                email_domain VARCHAR(100) NULL,
                duplicate_email VARCHAR(50) NULL,
                account_status VARCHAR(30) NULL,
                wallet_balance DECIMAL(18,2) NULL,
                wallet_segment VARCHAR(50) NULL,
                risk_level VARCHAR(30) NULL,
                risk_flag VARCHAR(30) NULL,
                created_at DATETIME2 NULL,
                account_tenure_days INT NULL,
                customer_lifetime_stage VARCHAR(50) NULL

            )
            END
            """)
            )
logger.info("Customers table checked/created successfully")
