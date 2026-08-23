import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.api_client import get_data_from_api
from config import api_config

def get_customer_data():
    return get_data_from_api(url=api_config.customer_url,
                                        timeout=api_config.timeout,
                                        maximum_retries=api_config.maximum_retries
                                        )
