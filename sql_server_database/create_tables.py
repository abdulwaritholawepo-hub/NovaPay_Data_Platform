from sqlalchemy import text
from urllib.parse import quote_plus
from production_DB_connection import production_database_engine_connection
import logging
from config import logging_config
logger = logging.getLogger(__name__)
engine = production_database_engine_connection()
logger.info("Production database engine created successfully")

with engine.begin() as conn: 
    logger.info("Checking whether customers table exists")
    conn.execute(
        text("""
             IF OBJECT_ID('dbo.customers', 'U') IS NULL
             BEGIN
             CREATE TABLE Customers(
             customer_id INTEGER IDENTITY(1,1) PRIMARY KEY,
             first_name  VARCHAR(50) NOT NULL,
             last_name   VARCHAR(50) NOT NULL,
             email       VARCHAR(100) UNIQUE NOT NULL,
             phone_number VARCHAR(20) UNIQUE NOT NULL,
             date_of_birth DATE NOT NULL,
             gender      VARCHAR(10) NOT NULL,
             account_number VARCHAR(20) UNIQUE NOT NULL,
             wallet_balance DECIMAL(18,2) DEFAULT 0.00 NOT NULL,
             account_status VARCHAR(20) NULL,
             created_at     DATETIME2 NOT NULL
             ) 
             END
             """)
    
    )
    logger.info("Customers table checked/created successfully")
    
    logger.info("Checking whether merchants table exists")
    conn.execute(
        text("""
             IF OBJECT_ID('dbo.merchants', 'u') IS NULL
             BEGIN
             CREATE TABLE Merchants(
             merchant_id INTEGER IDENTITY(1,1) PRIMARY KEY,
             merchant_name VARCHAR(100) UNIQUE NOT NULL,
             category VARCHAR(50) NULL,
             email VARCHAR(100) UNIQUE NOT NULL,
             phone_number VARCHAR(20) UNIQUE NOT NULL,
             city VARCHAR(50) NULL,
             state VARCHAR(50) NULL,
             account_number VARCHAR(20) UNIQUE NOT NULL,
             merchant_status VARCHAR(20) NULL,
             created_at DATETIME2 NOT NULL
             )
             END
             """)
    )
    logger.info("Merchants table checked/created successfully")

    logger.info("Checking whether transactions table exists")
    conn.execute(
        text("""
             IF OBJECT_ID('dbo.transactions','U') IS NULL
             BEGIN
             CREATE TABLE Transactions(
             transaction_id INTEGER IDENTITY(1,1) PRIMARY KEY,
             sender_id INTEGER NOT NULL,
             receiver_id INTEGER NOT NULL,
             receiver_type VARCHAR(30) NULL,
             amount DECIMAL(18,2) NOT NULL,
             currency VARCHAR(10) NOT NULL,
             payment_method VARCHAR(30) NULL,
             transaction_category VARCHAR(30) NULL,
             transaction_direction VARCHAR(10) NULL,
             status VARCHAR(20) NULL,
             reference_number VARCHAR(100) UNIQUE NOT NULL,
             narration VARCHAR(255) NULL,
             created_at DATETIME2 NOT NULL
             )
             END
             """)
    )
    logger.info("Transactions table checked/created successfully")

logger.info(
    "Production database table setup completed successfully. "
    "Customers, merchants, and transactions tables checked/created."
)
