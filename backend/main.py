import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI
from production_database.queries import get_records

app = FastAPI(
    title="NovaPay API",
    description="Development API for the NovaPay Data Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to NovaPay API"
    }


@app.get("/api/v1/customers")
def get_customers():
    customer_records = get_records(table_name='customers')
    return customer_records


@app.get("/api/v1/transactions")
def get_transactions():
    transaction_records = get_records(table_name='transactions')
    return transaction_records

@app.get("/api/v1/merchants")
def get_merchants():
    merchant_records = get_records(table_name='merchants')
    return merchant_records
