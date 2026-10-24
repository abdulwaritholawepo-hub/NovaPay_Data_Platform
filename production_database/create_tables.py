import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from urllib.parse import quote_plus
from production_database.production_DB_connection import production_database_engine_connection
import logging
from config import logging_config
logger = logging.getLogger(__name__)
engine = production_database_engine_connection()
logger.info("Production database engine created successfully")

with engine.begin() as conn: 
    logger.info("Checking whether customers table exists")
    conn.execute(
        text("""
             IF OBJECT_ID('dbo.Customers', 'U') IS NULL
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
             IF OBJECT_ID('dbo.Merchants', 'u') IS NULL
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
             IF OBJECT_ID('dbo.Transactions','U') IS NULL
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
    conn.execute(text("""
        IF OBJECT_ID('dbo.CustomerChangeEvents', 'U') IS NULL
        BEGIN
        CREATE TABLE CustomerChangeEvents(
        event_id bigint primary key identity(1,1) not null,
        customer_id int not null,
        event_type varchar(30) not null,
        effective_at datetime2(7) not null,
        event_sequence bigint not null check(event_sequence > 0),
        first_name varchar(50) not null,
        last_name varchar(50) not null,
        gender varchar(10) not null,
        date_of_birth date not null,
        phone_number varchar(20) not null,
        email varchar(100) not null,
        account_number varchar(20) null,
        wallet_balance decimal(18,2) not null check(wallet_balance >= 0),
        account_status varchar(20) null,
        created_at datetime2 not null,
        recorded_at datetime2(7) not null default sysdatetime(),
        processed_at datetime2(7) null,
        CONSTRAINT UQ_CustomerChangeEvents_Customer_Sequence
                UNIQUE (customer_id, event_sequence),

        constraint fk_customer_id foreign key (customer_id)
        references dbo.Customers(customer_id)
        )
        END
    """))
    logger.info("CustomerChangeEvents table checked/created successfully")

logger.info(
    "Production database table setup completed successfully. "
    "Customers, merchants, transactions tables and CustomerChangeEvents checked/created."
)


