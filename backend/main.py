from fastapi import FastAPI
from sql_server_database.queries import get_customers_records

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
    customers = get_customers_records()
    return customers


@app.get("/api/v1/transactions")
def get_transactions():
    return {
        "message": "Transactions endpoint is working."
    }


@app.get("/api/v1/merchants")
def get_merchants():
    return {
        "message": "Merchants endpoint is working."
    }