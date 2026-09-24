import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_incremental_loader.gold_generic_incremental import gold_generic_incremental_loader
from silver_query.silver_generic_query import generic_silver_query
customers = generic_silver_query('customers')
def gold_customer_incremental_load():
    return gold_generic_incremental_loader(transformed_data=customers,
                               domain="customer",
                               schema='gold.')
