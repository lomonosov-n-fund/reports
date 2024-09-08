# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv()

url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultDepositors"




# URL for the request
# url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultActivities"

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

dict = response.json()

print(dict['numberOfDepositors'])
print(dict['numberOfShares'])


# report depositors info as a table

keys_to_keep = ['numberOfDepositors', 'numberOfShares']

filtered_dict = {k: dict[k] for k in keys_to_keep if k in dict}
print(filtered_dict)

df = pd.DataFrame(filtered_dict.items(), columns=['Metric', 'Value'])

mapping_dict = {
    'numberOfDepositors': 'количество вкладчиков',
    'numberOfShares': 'количество акций'
}

df['Metric'] = df['Metric'].replace(mapping_dict)
df['Value'] = df['Value'].astype(int)

print(df)

from utils.latex import pandas_to_latex

pandas_to_latex(df, 'report/depositors.tex', caption = 'Основная информация о фонде', label = 'depositors')


