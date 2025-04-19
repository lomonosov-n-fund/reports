# Report on Asset Allocation and how it compares with the targets
# Use Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import click
from cli.params import common_options
from utils.report_dates import get_last_complete_quarter
import requests
import json
from dotenv import load_dotenv
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from utils.files import ensure_writable_dir
from utils.latex import pandas_to_latex

# Column names for LaTeX tables
ASSET_CLASS_COLUMNS = {
    'Asset Class': 'Класс актива',
    'value': 'Стоимость',
    'Percentage': 'Процент',
    'Reference': 'Целевой процент'
}

INCLASS_COLUMNS = {
    'Asset Name': 'Актив',
    'value': 'Стоимость',
    'Percentage': 'Процент',
    'Reference': 'Целевой процент'
}

pd.set_option('display.float_format', '{:.2f}'.format)

# function to replace blanks with '-'
def replace_blanks(s):
    return s.replace(' ', '-')

def report_inclass_allocations(index_csv, assets, class_name, total, output_dir, dry_run, verbose, year, quarter):
    if not os.path.exists(index_csv):
        print(f"Error: The file '{index_csv}' does not exist.")
        sys.exit(1)
    if verbose:
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
    if verbose:
        print(inclass_assets.to_string(index=False))
    classname = replace_blanks(class_name)
    if verbose:
        print(f'\nExporting to LaTEX')
    if not dry_run:
        ensure_writable_dir(output_dir, dry_run)
        # Rename columns for LaTeX output
        inclass_assets_latex = inclass_assets.rename(columns=INCLASS_COLUMNS)
        pandas_to_latex(inclass_assets_latex, Path(output_dir) / f'inclass-{classname}_{year}_Q{quarter}.tex',
                       caption=f'Распределение активов в классе {class_name}',
                       label=f'inclass-allocation-{classname}')

@click.command()
@common_options
def asset_allocation(dry_run, quarter, year, output_dir, verbose, operator, latex):
    # Resolve quarter/year
    q, y = (quarter, year) if quarter and year else get_last_complete_quarter()
    if verbose:
        click.echo(f"Reporting for Q{q} {y}")

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
        "deployment": "ethereum",
        "address": address,
        "currency": "usd"
    }

    if verbose:
        print("Making the request")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if verbose:
        print(f"Response status code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        exit()

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
    if verbose:
        print(f"\nTotal Value: {total_value:.2f}")

    # calculate the total value of the assets by asset class
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

    if verbose:
        print(f'\nAssets by class:')

    assets_by_class = assets_by_class.round(2) 
    # sort the values by the 'Percentage' column
    assets_by_class = assets_by_class.sort_values(by='Reference', ascending=False)

    c = assets_by_class.copy(deep=True)
    c = c.reset_index()
    # Rename columns for LaTeX output
    c_latex = c.rename(columns=ASSET_CLASS_COLUMNS)
    if verbose:
        print(c)
    
    if not dry_run:
        ensure_writable_dir(output_dir, dry_run)
        if latex:
            pandas_to_latex(c_latex, Path(output_dir) / f'assets-by-class_{y}_Q{q}.tex',
                          caption='Распределение активов по классам',
                          label='assets-by-class')

    index_date='2025-04-03'
    if verbose:
        print(f'\nusing index data for {index_date}')
    
    report_inclass_allocations(f'index/{index_date}/Large Cap Select Index.csv',
                             assets, 'Native Coins',
                             assets_by_class["value"]["Native Coins"],
                             output_dir, dry_run, verbose, y, q)
    report_inclass_allocations(f'index/{index_date}/Stablecoin Index.csv',
                             assets, 'Stable Coins',
                             assets_by_class["value"]["Stable Coins"],
                             output_dir, dry_run, verbose, y, q)

if __name__ == "__main__":
    asset_allocation()
