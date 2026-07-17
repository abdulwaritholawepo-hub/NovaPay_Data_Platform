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
        
        except requests.exceptions.HTTPError as errh:
            last_exception = errh
            print(f"HHTTP Error occurred: {errh}")
           
        except requests.exceptions.ConnectionError as errc:
            last_exception = errc
            print(f"connecting Error occurred: {errc}")
           
        except requests.exceptions.Timeout as errt:
            last_exception = errt
            print(f"Timeout Error occurred: {errt}")
            
        except requests.exceptions.JSONDecodeError as errjde:
            last_exception = errjde
            print(f"Response payload was not valid JSON: {errjde}")
            
        except requests.exceptions.RequestException as err:
            last_exception = err
            print(f"An unexpected error occurred: {err}")
        if attempts == maximum_retries:
            print("maximum retries reached")

        wait_time = attempts**2
        print(f"retrying in {wait_time} seconds")
        time.sleep(wait_time)
    if last_exception:
        raise last_exception


get_customer_data()