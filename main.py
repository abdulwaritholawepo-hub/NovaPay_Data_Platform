import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.customer_batch_loader import batch_loader_customer
from processing.merchants_batch_loader import batch_loader_merchants
def execution():
    batch_loader_customer()
    batch_loader_merchants()

if __name__ == "__main__":
    execution()
