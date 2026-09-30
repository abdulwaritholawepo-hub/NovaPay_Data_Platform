import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection

engine = analytics_database_engine_connection()
with engine.begin() as conn:
        conn.execute(text("""
             IF NOT EXISTS(SELECT * FROM sys.schemas WHERE name='gold')
             BEGIN
             EXEC('CREATE SCHEMA gold')
             END
             """))





with engine.begin() as conn:
    conn.execute(text(
        """
        IF OBJECT_ID('gold.dim_customer', 'U') IS NULL
        BEGIN
        CREATE TABLE gold.dim_customer(
    customer_key INT IDENTITY (1,1) PRIMARY KEY NOT NULL,
    customer_id INT NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(101) NOT NULL,
    customer_initials VARCHAR(2) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    date_of_birth DATE NOT NULL,
    age INT NOT NULL,
    is_adult BIT NOT NULL,
    eligibility VARCHAR(30) NULL,
    customer_segment VARCHAR(30) NULL,
    phone_number VARCHAR(20) NULL,
    email_domain VARCHAR(100) NULL,
    duplicate_email VARCHAR(20) NOT NULL,
    account_status VARCHAR(20) NULL,
    wallet_balance DECIMAL(18, 2) NOT NULL,
    wallet_segment VARCHAR(30) NULL,
    risk_level VARCHAR(20) NULL,
    risk_flag VARCHAR(20) NOT NULL,
    created_at DATETIME2 NULL,
    account_tenure_days INT NULL,
    customer_lifetime_stage VARCHAR(30) NULL,
    valid_from DATETIME2 NOT NULL,
    valid_to DATETIME2 NULL,
    is_current BIT NOT NULL

)
END

        """
        ))

    
with engine.begin() as conn:
    conn.execute(
        text("""
        IF OBJECT_ID('gold.dim_merchant','U') IS NULL
BEGIN
    CREATE TABLE gold.dim_merchant(
	    merchant_key INT IDENTITY (1,1) PRIMARY KEY NOT NULL,
	    merchant_id INT NOT NULL,
        account_number VARCHAR(20) NOT NULL,
	    merchant_code VARCHAR(20) NOT NULL,
	    merchant_name VARCHAR (150) NOT NULL,
	    category VARCHAR(100) NULL,
	    segment VARCHAR(100) NULL,
	    email VARCHAR(255) NULL,
        email_domain VARCHAR(100) NULL,
	    duplicate_email VARCHAR(20) NOT NULL,
        phone_number VARCHAR(20) NULL,
        city VARCHAR(100) NULL,
        state VARCHAR(100) NULL,
        location VARCHAR(200) NULL,
        merchant_status VARCHAR(30) NULL,
        is_active BIT NOT NULL,
        created_at DATETIME2 NOT NULL,
        merchant_tenure_days INT NOT NULL,
        tenure_category VARCHAR(50) NOT NULL,
        valid_from DATETIME2 NOT NULL,
        valid_to DATETIME2 NULL,
        is_current BIT NOT NULL
    )
END
        """))

with engine.begin() as conn:
    conn.execute(
        text("""
        IF OBJECT_ID('gold.dim_date', 'U') IS NULL
BEGIN
	CREATE TABLE gold.dim_date(
		date_key INT IDENTITY (1,1) PRIMARY KEY NOT NULL,
		full_date DATE UNIQUE NOT NULL,
		day INT NOT NULL,
		day_name VARCHAR(10) NOT NULL,
		day_of_week INT not null,
		week_of_year int not null,
		month int not null,
		month_name varchar(10) not null,
		quarter int not null,
		quarter_name varchar(2) not null,
		year int not null
	)
END
        """))

with engine.begin() as conn:
    conn.execute(
        text("""
        
        IF OBJECT_ID ('gold.fact_transaction', 'U') IS NULL
BEGIN
    CREATE TABLE gold.fact_transaction(
    transaction_key INT IDENTITY (1,1) PRIMARY KEY NOT NULL,
    transaction_id INT NOT NULL,
    sender_customer_key INT NOT NULL,
    receiver_customer_key INT NULL,
    receiver_merchant_key INT NULL,
    date_key INT NOT NULL,
    amount DECIMAL (18,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    receiver_type VARCHAR(20) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    transaction_category VARCHAR(30) NOT NULL,
    transaction_direction VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    reference_number VARCHAR(100) UNIQUE NOT NULL,
    narration VARCHAR(255) null,
    created_at DATETIME2 NOT NULL,

    CONSTRAINT FK_fact_transaction_sender_customer FOREIGN KEY (sender_customer_key)
    REFERENCES gold.dim_customer(customer_key),
    
    CONSTRAINT FK_fact_transaction_receiver_customer FOREIGN KEY (receiver_customer_key)
    REFERENCES gold.dim_customer(customer_key),

    CONSTRAINT FK_fact_transaction_receiver_merchant FOREIGN KEY (receiver_merchant_key)
    REFERENCES gold.dim_merchant(merchant_key),


    CONSTRAINT FK_fact_transaction_date FOREIGN KEY (date_key)
    REFERENCES gold.dim_date(date_key)
)
END
        """))
