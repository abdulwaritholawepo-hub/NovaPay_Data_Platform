import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from config import api_config

from config import api_config

def get_customer_data(url=None, timeout=None, maximum_retries=None):
    if url is None:
        url = api_config.customer_url
    if timeout is None:
        timeout = api_config.timeout
    if maximum_retries is None:
        maximum_retries = api_config.maximum_retries
    last_exception =None
    for attempts in range(1, maximum_retries + 1):
        try:
            response = requests.get(url, timeout=timeout )
        
            response.raise_for_status()
            print("request succesful")
            data = response.json()
            return data
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.JSONDecodeError,
            requests.exceptions.RequestException,)as err: 
            last_exception = err
            error_type = type(last_exception).__name__
            print(f"{error_type} occurred: {last_exception}")
            if attempts == maximum_retries:
                print("maximum retries reached")
            else:
                wait_time = attempts**2
                print(f"retrying in {wait_time} seconds")
                time.sleep(wait_time)
    if last_exception:
        raise last_exception