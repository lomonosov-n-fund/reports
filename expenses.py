import shelve
import sys
from moralis import evm_api
import json
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import requests
import pandas as pd
from utils.latex import pandas_to_latex
import click
from cli.params import common_options
from utils.report_dates import get_last_complete_quarter, get_quarter_dates
from utils.files import ensure_writable_dir
from pathlib import Path

def normalize_date(datetime_str):
    # Handle both ISO format and the original format
    try:
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        try:
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            # If it's already a datetime object, use it directly
            if isinstance(datetime_str, datetime):
                datetime_obj = datetime_str
            else:
                raise ValueError(f"Unsupported date format: {datetime_str}")
    
    formatted_date = datetime_obj.strftime('%d-%m-%Y')
    return formatted_date

class EthereumHistoricPrice:
    def __init__(self, currency="usd"):
        self.db = shelve.open("prices", writeback=True) 
        self.currency = currency
        self.api_key = os.getenv('COINGECKO_API_KEY')

    def __del__(self):
        self.db.close()

    def quote(self, date):
        if date in self.db:
            pass
        else:
            url = f"https://api.coingecko.com/api/v3/coins/ethereum/history?date={date}&localization=false"
            headers = {"accept": "application/json","x-cg-api-key": self.api_key}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.db[date] = response.json()
                self.db.sync()
                print(f"Retrieved {date} from API")
            else:
                print(f"Failed to retrieve {date} from API")
                return None
        return self.db[date]["market_data"]["current_price"][self.currency]
    
class TradesData:
    def __init__(self):
        self.db = shelve.open("trades") 
        self.api_key = os.getenv('MORALIS_API_KEY')

    def __del__(self):
        self.db.close()

    def qet(self, transaction_hash):
        if transaction_hash in self.db:
            pass
        else:
            params = {"chain": "eth", "transaction_hash": transaction_hash}
            result = evm_api.transaction.get_transaction(api_key=self.api_key,params=params)
            self.db[transaction_hash] = result
            self.db.sync()
            time.sleep(1)
        return self.db[transaction_hash]

def get_part_before_slash(s):
    return s.split('/')[0]

def trade_fee(transaction_hash, trades_data, eth_price, verbose=False):
    t = trades_data.qet(transaction_hash)
    fee_eth = float(t["transaction_fee"])
    block_date = normalize_date(t["block_timestamp"])
    eth_price_usd = eth_price.quote(block_date)
    fee_usd = fee_eth * eth_price_usd
    if verbose:
        print(f'Date  {block_date} Fee (USD): {fee_usd}')
    return fee_usd
    
def mgmt_fee(transaction_hash, trades_data, eth_price, verbose=False):
    t = trades_data.qet(transaction_hash)
    fee_eth = float(t["transaction_fee"])
    block_date = normalize_date(t["block_timestamp"])
    eth_price_usd = eth_price.quote(block_date)
    fee_usd = fee_eth * eth_price_usd
    if verbose:
        print(f'Date  {block_date} Fee (USD): {fee_usd}')
    return fee_usd

def AggregatByMonth(df):
    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    # Extract year and month from the Date column
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Group by the new YearMonth column and sum the Fee column
    monthly_fees = df.groupby('YearMonth')['Fee'].sum().reset_index()
    # Round the Fee column to 2 decimal places
    monthly_fees['Fee'] = monthly_fees['Fee'].round(2)
    return monthly_fees

@click.command()
@common_options
def expenses(dry_run, quarter, year, output_dir, verbose, operator, latex):
    # Resolve quarter/year
    q, y = (quarter, year) if quarter and year else get_last_complete_quarter()
    
    # Ensure output directory exists
    if not dry_run:
        ensure_writable_dir(output_dir)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize price and trades data
    eth_price = EthereumHistoricPrice()
    trades_data = TradesData()
    
    # Process vault activity
    with open('vault-activity.json', 'r') as f:
        data = json.load(f)
    
    # Initialize data structures
    tx_fees = {
        "Date": [],
        "Fee": []
    }
    
    mgmt_fees = {
        "Date": [],
        "Fee": []
    }
    
    # Process activities
    for activity in data['vaultActivities']:
        # Get the activity type and its data
        activity_type = list(activity.keys())[0]
        activity_data = activity[activity_type]
        
        # Get timestamp from the appropriate location
        timestamp = activity_data.get('timestamp')
        if not timestamp:
            continue
            
        # Convert Unix timestamp to ISO format
        timestamp_iso = datetime.fromtimestamp(timestamp).isoformat()
        
        if 'trade' in activity_type:
            transaction_hash = get_part_before_slash(activity_data['id'])
            fee = trade_fee(transaction_hash, trades_data, eth_price, verbose)
            tx_fees["Date"].append(normalize_date(timestamp_iso))
            tx_fees["Fee"].append(fee)
        elif "feeSharesReceivedEvent" in activity_type:
            transaction_hash = get_part_before_slash(activity_data['id'])
            fee = mgmt_fee(transaction_hash, trades_data, eth_price, verbose)
            shares = float(activity_data["shares"])
            if verbose:
                print(f'Date {normalize_date(timestamp_iso)} Fee (USD): {fee} Shares: {shares} Tx Hash: {transaction_hash}')
            mgmt_fees["Date"].append(normalize_date(timestamp_iso))
            mgmt_fees["Fee"].append(shares)
    
    # Create DataFrames and aggregate by month
    df_tx = pd.DataFrame(tx_fees)
    monthly_tx_fees = AggregatByMonth(df_tx)
    
    df_mgmt = pd.DataFrame(mgmt_fees)
    monthly_mgmt_fees = AggregatByMonth(df_mgmt)
    
    # Generate LaTeX output if requested
    if latex and not dry_run:
        # Create filenames with year and quarter
        tx_expense_file = output_dir / f'monthly-tx-expense_{y}_Q{q}.tex'
        mgmt_fee_file = output_dir / f'monthly-mgmt-fee_{y}_Q{q}.tex'
        
        pandas_to_latex(
            monthly_tx_fees, 
            tx_expense_file, 
            caption='Транзакционные расходы (USD)', 
            label='monthly-tx-expense'
        )
        
        pandas_to_latex(
            monthly_mgmt_fees, 
            mgmt_fee_file, 
            caption='Комиссия за управление (акции фонда)', 
            label='monthly-mgmt-fee'
        )
    
    # Print output if operator mode is enabled
    if operator:
        print("\nMonthly Transaction Fees (USD):")
        print(monthly_tx_fees)
        print("\nIndividual Management Fees:")
        print(df_mgmt)
        print("\nMonthly Management Fees (Shares):")
        print(monthly_mgmt_fees)

if __name__ == '__main__':
    expenses()
