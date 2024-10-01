# Report on Performance 

# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd


pd.set_option('display.float_format', '{:.2f}'.format)
load_dotenv()

# URL for the request
url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultTimeSeries" 

# Headers to be sent with the request
ENZYME_API_KEY=os.getenv('ENZYME_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ENZYME_API_KEY}",
    "Connect-Protocol-Version": "1"
}

# Data to be sent in JSON format
address = os.getenv('ENZYME_VAULT_ADDRESS')

# use ISO 8601 format for dates
start_date = "2024-05-01T00:00:00Z"
print(f"start date {start_date}")
end_date = "2024-09-26T00:00:00Z"
print(f"end date {end_date}")
data = {
    "deployment": "DEPLOYMENT_UNSPECIFIED", 
    "address": address,  
    "currency": "CURRENCY_UNSPECIFIED",  # Currency in which to receive the data
    "range": {
        "from": start_date,  # Start date in ISO 8601 format
        "to": end_date  # End date in ISO 8601 format
    },
    "resolution": "RESOLUTION_ONE_DAY"  #
}


# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# pretty print the response's json
# print(json.dumps(response.json(), indent=2))

# convert json to pandas dataframe



# data = pd.read_json(response.json())
# data = response.json()

# Normalize the data to unpack the nested 'items'
df = pd.json_normalize(response.json()['items'])

# Convert 'timestamp' to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# print(df)

import matplotlib.pyplot as plt

# Directory where the plot will be saved
output_dir = './report'
print(f"Output directory {output_dir}")

# Create the directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Plotting

plt.figure(figsize=(10, 5))  # Set the figure size (optional)
plt.plot(df['timestamp'], df['netShareValue'], marker='o')  # Line plot with markers
plt.title('Net Share Value Over Time')  # Title of the plot
plt.xlabel('Timestamp')  # X-axis label
plt.ylabel('Net Share Value')  # Y-axis label
plt.grid(True)  # Turn on the grid
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()  # Automatically adjust subplot parameters to give specified padding
# plt.show()
output_path = os.path.join(output_dir, 'performance_plot.png')
plt.savefig(output_path)

# add plot for grossAssetValue
plt.figure(figsize=(10, 5))  # Set the figure size (optional)
plt.plot(df['timestamp'], df['grossAssetValue'], marker='o')  # Line plot with markers
plt.title('Gross Asset Value Over Time')  # Title of the plot
plt.xlabel('Timestamp')  # X-axis label
plt.ylabel('Gross Asset Value')  # Y-axis label
plt.grid(True)  # Turn on the grid
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()  # Automatically adjust subplot parameters to give specified padding
# plt.show()

output_path = os.path.join(output_dir, 'gross_asset_value_plot.png')
plt.savefig(output_path)


# plt.savefig('./report/gross_asset_value_plot.png')

