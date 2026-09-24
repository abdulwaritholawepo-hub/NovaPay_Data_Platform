import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer_helper import COLUMN_ORDER
from silver_batch_loader.batch_loader import generic_batch_loader
from transform.customer_transformer import transform_customers
from silver_incremental_loader.incremental_loader import DOMAIN_CONFIG
config = DOMAIN_CONFIG["customer"]
table_name = config["table"]
def batch_loader_customer():
    loader = generic_batch_loader(table_name=table_name,
                                   column_order=COLUMN_ORDER,
                                   transformed_data= transform_customers(),
                                   domain="customer"
                                   )
    return loader