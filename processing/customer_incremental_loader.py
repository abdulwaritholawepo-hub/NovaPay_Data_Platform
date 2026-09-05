import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.incremental_loader import generic_incremental_loader
from transform.customer_transformer import transform_customers

def customer_incremental_loader():
    return generic_incremental_loader(transformed_data=transform_customers(),
                                                domain="customer" )
  
