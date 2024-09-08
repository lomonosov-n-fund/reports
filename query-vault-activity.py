# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()


# URL for the request
url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultActivities"

# Headers to be sent with the request
ENZYME_API_KEY=os.getenv('ENZYME_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ENZYME_API_KEY}",
    "Connect-Protocol-Version": "1"
}

# Data to be sent in JSON format
address = os.getenv('ENZYME_VAULT_ADDRESS')
data = {
  "deployment": "DEPLOYMENT_UNSPECIFIED",
  "address": address,
  "currency": "CURRENCY_UNSPECIFIED"
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# pretty print the response
print(json.dumps(response.json(), indent=2))
