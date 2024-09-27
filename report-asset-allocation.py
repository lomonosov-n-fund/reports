# Report on Asset Allocation and how it compares with the targets
# Use Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

pd.set_option('display.float_format', '{:.2f}'.format)
load_dotenv()

# URL for the request
url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultPortfolio"

# Request headers
ENZYME_API_KEY=os.getenv('ENZYME_API_KEY')
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ENZYME_API_KEY}",
    "Connect-Protocol-Version": "1"
}

# Request data to be sent in JSON format
address = os.getenv('ENZYME_VAULT_ADDRESS')
data = {
  "deployment": "DEPLOYMENT_UNSPECIFIED",
  "address": address,
  "currency": "CURRENCY_UNSPECIFIED"
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(data))

# convert json to pandas dataframe
assets = pd.DataFrame(response.json()["assets"])



with open('coin_data.json', 'r') as f:
    coin_data = json.load(f)

# Coin Name - specific coin name 
# Asset Name - few coins can contribute to the same asset (e.g. WBTC and renBTC both contribute to BTC)
# Use coin data to modify the table 
assets["Coin Name"] = assets["address"].map(lambda x: coin_data[x]["Coin Name"])
assets["Asset Name"] = assets["address"].map(lambda x: coin_data[x]["Asset Name"])
assets["Asset Class"] = assets["address"].map(lambda x: coin_data[x]["Asset Class"])
del assets["address"]

total_value = assets["value"].sum()
print(f"\nTotal Value: {total_value:.2f}")

# calculate the total value of the assets by asset class
# assets_copy = assets.copy(deep=True)
assets_by_class = assets.groupby('Asset Class').sum() 
# keep only these columns
assets_by_class.drop(assets_by_class.columns.difference(['value', 'Asset Class']), axis=1, inplace=True)
assets_by_class["Percentage"] = assets_by_class["value"] / total_value * 100
assets_by_class["Reference"] = 0
assets_by_class.loc["Native Coins", "Reference"] = 70
assets_by_class.loc["Stable Coins", "Reference"] = 30

total_by_class = {}
total_by_class["Native Coins"] = assets_by_class["value"]["Native Coins"]
total_by_class["Stable Coins"] = assets_by_class["value"]["Stable Coins"]

print(f'\nAssets by class:')



def table_to_pdf(df, filename):
    with PdfPages(filename) as pdf:
        fig, ax =plt.subplots(figsize=(8, 3))  # Adjust as necessary
        ax.axis('tight')
        ax.axis('off')  # Hide the axes
        the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
        # Optional: Configure table properties
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(12)
        the_table.scale(1.2, 1.2)  # Adjust table size
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

from utils.latex import pandas_to_latex
# def table_to_latex(df, filename, caption, label):
#     latex_table = df.to_latex(
#         index=False,
#         float_format="%.2f")
#     latex_table = f""" 
# \\begin{{table}}[h] 
# \\centering 
# {latex_table} 
# \\caption{{{caption}}} 
# \\label{{tab:{label}}} 
# \\end{{table}} 
# """
#     with open(filename, 'w') as f:
#         f.write(latex_table)


assets_by_class = assets_by_class.round(2) 
# sort the values by the 'Percentage' column
assets_by_class = assets_by_class.sort_values(by='Reference', ascending=False)

c = assets_by_class.copy(deep=True)
c = c.reset_index()
print(c)
table_to_pdf(c, 'report/assets_by_class.pdf')
pandas_to_latex(c, 'report/assets-by-class.tex',caption='Распределение активов по классам', label='assets-by-class')

# function to replace blanks with '-'
def replace_blanks(s):
    return s.replace(' ', '-')

def report_inclass_allocations(index_csv, assets, class_name, total):
    print(f'\nInclass allocations for {class_name}:')
    # keep rows with Asset Class = class_name
    coins = assets[assets["Asset Class"] == class_name]
    # aggregate the values by Asset Name
    inclass_assets = coins.groupby('Asset Name').sum()
    # add a new column to the dataframe with the percentage of the total value
    inclass_assets["Percentage"] = inclass_assets["value"] / total * 100
    # keep only these columns
    inclass_assets.drop(inclass_assets.columns.difference(['Asset Name', 'value', 'Percentage']), axis=1, inplace=True)
    # manual download https://www.coindesk.com/indices
    index = pd.read_csv(index_csv, usecols=['Symbol', 'Weight'], dtype={'Weight': float})
    # uppercase the Symbol column
    index['Asset Name'] = index['Symbol'].str.upper()
    # Add Reference column
    inclass_assets = inclass_assets.merge(index[['Asset Name', 'Weight']], on='Asset Name', how='left')
    inclass_assets.rename(columns={'Weight': 'Reference'}, inplace=True)
    inclass_assets.sort_values(by='Percentage', ascending=False, inplace=True)
    print(inclass_assets.to_string(index=False))
    classname = replace_blanks(class_name)
    pandas_to_latex(inclass_assets, f'report/inclass-{classname}.tex',caption=f'Распределение активов в классе {class_name}', label=f'inclass-allocation-{classname}')

index_date='2024-09-08'
print(f'using index data for {index_date}')
report_inclass_allocations(f'index/{index_date}/Constituents - CoinDesk Large Cap Select Index.csv', assets, 'Native Coins', assets_by_class["value"]["Native Coins"])
report_inclass_allocations(f'index/{index_date}/Constituents - CoinDesk Stablecoin Index.csv', assets, 'Stable Coins', assets_by_class["value"]["Stable Coins"])
