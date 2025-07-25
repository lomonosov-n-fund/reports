# Report on Performance 
# Enzyme API documentation: https://enzymefinance.github.io/sdk/api/overview

import click
from cli.params import common_options
from utils.report_dates import get_last_complete_quarter, get_quarter_dates
from utils.files import ensure_writable_dir
import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

pd.set_option('display.float_format', '{:.2f}'.format)

def calculate_performance(df, start_date=None):
    """Calculate performance metrics for a given date range"""
    if start_date:
        df = df[df['timestamp'] >= pd.to_datetime(start_date)]
    
    start_value = df['netShareValue'].iloc[0]
    end_value = df['netShareValue'].iloc[-1]
    performance = ((end_value - start_value) / start_value) * 100
    
    return {
        'start_date': df['timestamp'].iloc[0],
        'end_date': df['timestamp'].iloc[-1],
        'start_value': start_value,
        'end_value': end_value,
        'performance': performance,
        'start_gav': df['grossAssetValue'].iloc[0],
        'end_gav': df['grossAssetValue'].iloc[-1]
    }

@click.command()
@common_options
def performance(dry_run, quarter, year, output_dir, verbose, operator, latex):
    # Resolve quarter/year
    q, y = (quarter, year) if quarter and year else get_last_complete_quarter()
    if verbose:
        click.echo(f"Reporting for Q{q} {y}")

    load_dotenv()

    # Fund inception date - can be overridden via FUND_INCEPTION_DATE environment variable
    FUND_INCEPTION_DATE = os.getenv('FUND_INCEPTION_DATE', "2024-01-01T00:00:00Z")

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

    # Get quarter dates
    quarter_start_day, quarter_end_day = get_quarter_dates(y, q)
    if verbose:
        click.echo(f"Quarter starts at: {quarter_start_day}")
        click.echo(f"Quarter ends at: {quarter_end_day}")

    data = {
        "deployment": "ethereum", 
        "address": address,  
        "currency": "usd",  # Currency in which to receive the data
        "range": {
            "from": FUND_INCEPTION_DATE,  # Start from inception
            "to": quarter_end_day  # End at quarter end
        },
        "resolution": "RESOLUTION_ONE_DAY"  #
    }

    if verbose:
        click.echo("Making POST request to Enzyme")

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        click.echo(f"Error: {response.text}", err=True)
        return

    # convert json to pandas dataframe
    df = pd.json_normalize(response.json()['items'])

    # Convert 'timestamp' to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    if operator:
        # Calculate quarter performance
        quarter_df = df[df['timestamp'].between(pd.to_datetime(quarter_start_day), pd.to_datetime(quarter_end_day))]
        quarter_perf = calculate_performance(quarter_df)
        
        # Calculate since inception performance
        inception_perf = calculate_performance(df, FUND_INCEPTION_DATE)

        # Format the output
        click.echo("\nQuarter Performance Summary:")
        click.echo(f"Quarter: Q{q} {y}")
        click.echo(f"Start Date: {quarter_perf['start_date'].strftime('%Y-%m-%d')}")
        click.echo(f"End Date: {quarter_perf['end_date'].strftime('%Y-%m-%d')}")
        click.echo(f"Starting Net Share Value: ${quarter_perf['start_value']:,.2f}")
        click.echo(f"Ending Net Share Value: ${quarter_perf['end_value']:,.2f}")
        click.echo(f"Quarter Performance: {quarter_perf['performance']:+.2f}%")
        click.echo(f"Starting Gross Asset Value: ${quarter_perf['start_gav']:,.2f}")
        click.echo(f"Ending Gross Asset Value: ${quarter_perf['end_gav']:,.2f}")

        click.echo("\nSince Inception Performance Summary:")
        click.echo(f"Start Date: {inception_perf['start_date'].strftime('%Y-%m-%d')}")
        click.echo(f"End Date: {inception_perf['end_date'].strftime('%Y-%m-%d')}")
        click.echo(f"Starting Net Share Value: ${inception_perf['start_value']:,.2f}")
        click.echo(f"Ending Net Share Value: ${inception_perf['end_value']:,.2f}")
        click.echo(f"Total Performance: {inception_perf['performance']:+.2f}%")
        click.echo(f"Starting Gross Asset Value: ${inception_perf['start_gav']:,.2f}")
        click.echo(f"Ending Gross Asset Value: ${inception_perf['end_gav']:,.2f}")

    if verbose:
        click.echo("Generating performance plots")

    # Create output directory if needed
    if not dry_run and not operator:
        ensure_writable_dir(output_dir, dry_run)

    # Filter data for quarter-specific plots
    quarter_df = df[df['timestamp'].between(pd.to_datetime(quarter_start_day), pd.to_datetime(quarter_end_day))]

    # Plot quarter-specific net share value
    plt.figure(figsize=(10, 5))
    plt.plot(quarter_df['timestamp'], quarter_df['netShareValue'], marker='o', color='blue')
    if operator:
        plt.title(f'Quarter {q} {y} Net Share Value')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if operator:
        plt.show()
    elif latex and not dry_run:
        output_path = Path(output_dir) / f'performance_quarter_{y}_Q{q}.png'
        plt.savefig(output_path)
        if verbose:
            click.echo(f"Saved quarter net share value plot to {output_path}")

    # Plot quarter-specific gross asset value
    plt.figure(figsize=(10, 5))
    plt.plot(quarter_df['timestamp'], quarter_df['grossAssetValue'], marker='o', color='green')
    if operator:
        plt.title(f'Quarter {q} {y} Gross Asset Value')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if operator:
        plt.show()
    elif latex and not dry_run:
        output_path = Path(output_dir) / f'gross_asset_value_quarter_{y}_Q{q}.png'
        plt.savefig(output_path)
        if verbose:
            click.echo(f"Saved quarter gross asset value plot to {output_path}")

    # Plot since inception net share value
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['netShareValue'], marker='o', color='blue')
    if operator:
        plt.title('Net Share Value Since Inception')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if operator:
        plt.show()
    elif latex and not dry_run:
        output_path = Path(output_dir) / f'performance_since_inception_{y}_Q{q}.png'
        plt.savefig(output_path)
        if verbose:
            click.echo(f"Saved since inception net share value plot to {output_path}")

    # Plot since inception gross asset value
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['grossAssetValue'], marker='o', color='green')
    if operator:
        plt.title('Gross Asset Value Since Inception')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if operator:
        plt.show()
    elif latex and not dry_run:
        output_path = Path(output_dir) / f'gross_asset_value_since_inception_{y}_Q{q}.png'
        plt.savefig(output_path)
        if verbose:
            click.echo(f"Saved since inception gross asset value plot to {output_path}")

if __name__ == "__main__":
    performance()



