import requests
import os

# payload = {"api_key": os.environ["ETSY_API_KEY"], "tags": "dog"}

payload = {"aws_key": os.environ['AMAZON_ACCESS_KEY'],
           "aws_secret": os.environ['AMAZON_SECRET_KEY'],
           "aws_associate_tag": os.environ['AMAZON_ASSOC_TAG'],
           "Keywords": "dog",
           "SearchIndex": "All"}

response = requests.get("https://openapi.etsy.com/v2/listings/active", params=payload)

data = response.json()
