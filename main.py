import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.customer_batch_loader import batch_loader_customer
from processing.merchants_batch_loader import batch_loader_merchants
from processing.transaction_batch_loader import batch_loader_transactions
def execution():
    batch_loader_customer()
    batch_loader_merchants()
    batch_loader_transactions()

if __name__ == "__main__":
    execution()
