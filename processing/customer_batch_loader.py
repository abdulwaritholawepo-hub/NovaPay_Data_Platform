import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.customer_transformer_helper import COLUMN_ORDER
from processing.batch_loader import generic_batch_loader
from transform.customer_transformer import transform_customers
from processing.incremental_loader import DOMAIN_CONFIG
config = DOMAIN_CONFIG["customer"]
table_name = config["table"]
def customer_batch_loader():
    loader = generic_batch_loader(batch_domain=table_name,
                                   domain_column_order=COLUMN_ORDER,
                                   transformed_data= transform_customers(),
                                   domain="customer"
                                   )
    return loader