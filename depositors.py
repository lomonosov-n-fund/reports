# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview
# https://sdk.enzyme.finance/api/endpoints/vault
import click
from cli.params import common_options
from utils.report_dates import get_last_complete_quarter, get_quarter_dates
from utils.files import ensure_writable_dir
import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
import datetime
from pathlib import Path

def filter_depositors_by_date_range(data, start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ")
    filtered = [
        depositor
        for depositor in data
        if start_date <= datetime.datetime.strptime(depositor["depositorSince"], "%Y-%m-%dT%H:%M:%SZ") <= end_date
    ]
    return filtered


@click.command()
@common_options
def depositors(dry_run, quarter, year, output_dir, verbose, operator, latex):
    # Resolve quarter/year
    q, y = (quarter, year) if quarter and year else get_last_complete_quarter()
    if verbose:
        click.echo(f"Reporting for Q{q} {y}")

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
    if verbose:
        click.echo("Making POST request to Enzyme")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    dict = response.json()

    
    # all depositors as of the last day of the previous quarter
    start_date = "2024-01-01T00:00:00Z"
    # end_date = "2025-03-31T23:59:59Z"
    quarter_start_day, quarter_end_day = get_quarter_dates(y, q)
    print(f"Quarter starts at: {quarter_start_day}")
    print(f"Quarter ends at: {quarter_end_day}")
    end_date = quarter_end_day
    filtered_depositors = filter_depositors_by_date_range(dict['depositors'], start_date, end_date)


    # Create a DataFrame with aggregated data
    number_of_depositors = len(filtered_depositors)
    total_number_of_shares = sum(d["numberOfShares"] for d in filtered_depositors)

    summary_df = pd.DataFrame({
        "Показатель": ["количество вкладчиков", "количество акций"],
        "Значение": [int(number_of_depositors), int(total_number_of_shares)]
    })

    if verbose:
        print(summary_df)

    from utils.latex import pandas_to_latex
    filepath = Path(output_dir) / f"depositors_{y}_Q{q}.tex"
    if verbose:
        print( filepath )
    if not dry_run:
        ensure_writable_dir(output_dir, dry_run)
        pandas_to_latex(summary_df, filepath, caption = 'Основная информация о фонде', label = 'depositors')


if __name__ == "__main__":
    depositors()