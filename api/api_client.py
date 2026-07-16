import requests
import json

url = "http://localhost:8000/api/v1/customers"
resposnse = requests.get(url)
print(resposnse)