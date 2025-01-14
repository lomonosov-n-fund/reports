# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview
# https://sdk.enzyme.finance/api/endpoints/vault

import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
import datetime

load_dotenv()

# URL for the request
url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultDepositors"

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
  "deployment": "ethereum",
  "address": address,
  "currency": "usd"
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# pretty print the response
# print(json.dumps(response.json(), indent=2))

dict = response.json()

# print(dict['numberOfDepositors'])
# print(dict['numberOfShares'])
# print(dict['depositors'])

def filter_depositors_by_date_range(data, start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
    filtered = [
        depositor
        for depositor in data
        if start_date <= datetime.datetime.strptime(depositor["depositorSince"], "%Y-%m-%dT%H:%M:%SZ") <= end_date
    ]
    return filtered

# all depositors in 2024 year 
start_date = "2024-01-01T00:00:00Z"
end_date = "2024-12-31T23:59:59Z"
filtered_depositors = filter_depositors_by_date_range(dict['depositors'], start_date, end_date)
# print(filtered_depositors)
# print(len(filtered_depositors))


# Create a DataFrame with aggregated data
number_of_depositors = len(filtered_depositors)
total_number_of_shares = sum(d["numberOfShares"] for d in filtered_depositors)

summary_df = pd.DataFrame({
    "Metric": ["количество вкладчиков", "количество акций"],
    "Value": [int(number_of_depositors), int(total_number_of_shares)]
})

print(summary_df)
# report depositors info as a table

# keys_to_keep = ['numberOfDepositors', 'numberOfShares']

# filtered_dict = {k: dict[k] for k in keys_to_keep if k in dict}
# print(filtered_dict)

# df = pd.DataFrame(filtered_dict.items(), columns=['Metric', 'Value'])

# mapping_dict = {
#     'numberOfDepositors': 'количество вкладчиков',
#     'numberOfShares': 'количество акций'
# }

# df['Metric'] = df['Metric'].replace(mapping_dict)
# df['Value'] = df['Value'].astype(int)

# print(df)

from utils.latex import pandas_to_latex

pandas_to_latex(summary_df, 'report/depositors.tex', caption = 'Основная информация о фонде', label = 'depositors')


