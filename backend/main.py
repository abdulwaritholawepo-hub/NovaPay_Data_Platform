from fastapi import FastAPI

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
    return {
        "message": "Customers endpoint is working."
    }


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