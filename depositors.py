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
@click.option("--report-date", type=str, help="ISO date to override quarter (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)")
@common_options
def depositors(dry_run, quarter, year, output_dir, verbose, operator, latex, report_date):
    # Resolve quarter/year
    q, y = (quarter, year) if quarter and year else get_last_complete_quarter()
    if verbose and not report_date:
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

    
    # all depositors as of the target report date
    start_date = "2024-01-01T00:00:00Z"
    if report_date:
        # Normalize provided report date to ISO end-of-day when only YYYY-MM-DD is given
        report_date_str = report_date
        if "T" in report_date_str:
            end_date = report_date_str if report_date_str.endswith("Z") else report_date_str + "Z"
        else:
            end_date = f"{report_date_str}T23:59:59Z"
        if verbose:
            click.echo(f"Overriding quarter with report date: {end_date}")
    else:
        quarter_start_day, quarter_end_day = get_quarter_dates(y, q)
        if verbose:
            click.echo(f"Quarter starts at: {quarter_start_day}")
            click.echo(f"Quarter ends at: {quarter_end_day}")
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
        click.echo(summary_df)

    from utils.latex import pandas_to_latex
    if report_date:
        # Use date-only portion for filename
        date_only = report_date.split("T")[0]
        filepath = Path(output_dir) / f"depositors_{date_only}.tex"
    else:
        filepath = Path(output_dir) / f"depositors_{y}_Q{q}.tex"
    if verbose:
        click.echo( filepath )
    if not dry_run:
        ensure_writable_dir(output_dir, dry_run)
        pandas_to_latex(summary_df, filepath, caption = 'Основная информация о фонде', label = 'depositors')


if __name__ == "__main__":
    depositors()