import requests
import os

payload = {"api_key": os.environ["ETSY_API_KEY"], "tags": "dog"}

response = requests.get("https://openapi.etsy.com/v2/listings/active", params=payload)

data = response.json()
