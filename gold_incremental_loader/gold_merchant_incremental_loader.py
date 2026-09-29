import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_incremental_loader.gold_generic_incremental import gold_generic_incremental_loader
from silver_query.silver_generic_query import generic_silver_query
merchants = generic_silver_query('merchants')
def gold_merchant_incremental_load():
    return gold_generic_incremental_loader(transformed_data=merchants,
                               domain="merchant",
                               schema='gold.')
