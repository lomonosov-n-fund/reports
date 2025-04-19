# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import sys
import requests
import json
from dotenv import load_dotenv
import os
from datetime import timedelta, date

# use first argument as filename, if not provided, use default
filename = sys.argv[1] if len(sys.argv) > 1 else 'vault-activity.json'
print(f"Filename: {filename}")

load_dotenv()

# URL for the request
url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultActivities"

# Headers to be sent with the request
ENZYME_API_KEY=os.getenv('ENZYME_API_KEY')
headers = {
    "content-type": "application/json",
    "authorization": f"Bearer {ENZYME_API_KEY}",
    "connect-protocol-version": "1"
}

# Data to be sent in JSON format
address = os.getenv('ENZYME_VAULT_ADDRESS')
start_date = "2024-01-01T00:00:00Z"
print(f"start date {start_date}")


yesterday_date = date.today() - timedelta(days=1)
end_date = f"{yesterday_date.isoformat()}T00:00:00Z"

print(f"end date {end_date}")

data = {
  "deployment": "ethereum",
  "address": address,
  "currency": "usd",
  "range": {"from": start_date, "to": end_date}
}

print("Making the request")
response = requests.post(url, headers=headers, data=json.dumps(data))
print(f"Response status code: {response.status_code}")

# check if the request was successful
if response.status_code != 200:
    print(f"Request failed with status code {response.status_code}")
    exit()

# pretty print the response into a file
with open(filename, 'w') as file:
    file.write(json.dumps(response.json(), indent=2))
