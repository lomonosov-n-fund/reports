# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import click
import requests
import json
from dotenv import load_dotenv
import os
from datetime import timedelta, date
from pathlib import Path

@click.command(help="""
Fetches historical vault activity data from the Enzyme API and stores it for use by other scripts.
""")
@click.option('--filename', default='vault-activity.json', show_default=True, help='Output filename for vault activity data (JSON).')
@click.option('--output-dir', default='.', show_default=True, type=click.Path(file_okay=False, dir_okay=True, writable=True), help='Directory to save the output file.')
@click.option('--verbose', is_flag=True, help='Enable verbose output.')
def main(filename, output_dir, verbose):
    load_dotenv()

    output_path = Path(output_dir) / filename
    if verbose:
        click.echo(f"Output file: {output_path}")

    # URL for the request
    url = "https://api.enzyme.finance/enzyme.enzyme.v1.EnzymeService/GetVaultActivities"

    # Headers to be sent with the request
    ENZYME_API_KEY = os.getenv('ENZYME_API_KEY')
    if not ENZYME_API_KEY:
        raise click.ClickException("ENZYME_API_KEY not set in environment.")
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {ENZYME_API_KEY}",
        "connect-protocol-version": "1"
    }

    # Data to be sent in JSON format
    address = os.getenv('ENZYME_VAULT_ADDRESS')
    if not address:
        raise click.ClickException("ENZYME_VAULT_ADDRESS not set in environment.")
    start_date = os.getenv('FUND_INCEPTION_DATE', '2024-01-01T00:00:00Z')
    if verbose:
        click.echo(f"Start date: {start_date}")

    yesterday_date = date.today() - timedelta(days=1)
    end_date = f"{yesterday_date.isoformat()}T00:00:00Z"
    if verbose:
        click.echo(f"End date: {end_date}")

    data = {
        "deployment": "ethereum",
        "address": address,
        "currency": "usd",
        "range": {"from": start_date, "to": end_date}
    }

    if verbose:
        click.echo("Making the request...")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if verbose:
        click.echo(f"Response status code: {response.status_code}")

    # check if the request was successful
    if response.status_code != 200:
        raise click.ClickException(f"Request failed with status code {response.status_code}")

    # pretty print the response into a file
    with open(output_path, 'w') as file:
        file.write(json.dumps(response.json(), indent=2))
    if verbose:
        click.echo(f"Vault activity data saved to {output_path}")

if __name__ == '__main__':
    main()
