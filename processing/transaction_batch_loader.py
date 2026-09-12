import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.transaction_transformer_helper import TRANSACTION_COLUMN_ORDER
from processing.batch_loader import generic_batch_loader
from transform.transaction_transformer import transform_transactions
from processing.incremental_loader import DOMAIN_CONFIG
config = DOMAIN_CONFIG["transaction"]
table_name = config["table"]
def batch_loader_transactions():
    return generic_batch_loader(batch_domain=table_name,
                                domain_column_order=TRANSACTION_COLUMN_ORDER,
                                transformed_data=transform_transactions(),
                                domain="transaction")
