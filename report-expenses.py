import shelve
import sys
from moralis import evm_api
import json
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import requests
# from prettytable import PrettyTable
import pandas as pd
from utils.latex import pandas_to_latex

def normalize_date(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_date = datetime_obj.strftime('%d-%m-%Y')
    return formatted_date

class EthereumHistoricPrice:
    def __init__(self, currency="usd"):
        self.db = shelve.open("prices", writeback=True) 
        self.currency = currency
        self.api_key = os.getenv('COINGECKO_API_KEY')

    def __del__(self):
        # print("Closing Prices database")
        self.db.close()

    def quote(self, date):
        if date in self.db:
            # print(f"Retrieving {date} from cache")
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
        # print("Closing Trades database")
        self.db.close()

    def qet(self, transaction_hash):
        if transaction_hash in self.db:
            # print('Transaction already exists')
            pass
        else:
            # print('Transaction does not exist, adding it to the shelve')
            params = {"chain": "eth", "transaction_hash": transaction_hash}
            result = evm_api.transaction.get_transaction(api_key=self.api_key,params=params)
            self.db[transaction_hash] = result
            self.db.sync()
            # I use free API, so I need to wait in case throughput limits are reached
            time.sleep(1)
        return self.db[transaction_hash]
        
load_dotenv()

# Initialize locally cached obbjects
price_usd = EthereumHistoricPrice("usd")
trade = TradesData()

# get filename from command line argument, if not provided, use default
filename = sys.argv[1] if len(sys.argv) > 1 else 'vault-activity.json'

with open(filename, 'r') as file:
    data = json.load(file)

def get_part_before_slash(s):
    return s.split('/')[0]

def trade_fee(transaction_hash):
    t = trade.qet(transaction_hash)
    fee_eth = float(t["transaction_fee"])
    block_date = normalize_date(t["block_timestamp"])
    eth_price = price_usd.quote(block_date)
    fee_usd = fee_eth * eth_price
    print(f'Date  {block_date} Fee (USD): {fee_usd}' )
    return block_date, fee_usd
    
def mgmt_fee(transaction_hash):
    t = trade.qet(transaction_hash)
    fee_eth = float(t["transaction_fee"])
    block_date = normalize_date(t["block_timestamp"])
    eth_price = price_usd.quote(block_date)
    fee_usd = fee_eth * eth_price
    print(f'Date  {block_date} Fee (USD): {fee_usd}' )
    return block_date, fee_usd


dict = {
    "Date": [],
    "Fee": []
}   

fee_mgmt = {
    "Date": [],
    "Fee": []
}


for activity in data['vaultActivities']:
    if 'trade' in activity:
        transaction_hash = get_part_before_slash(activity['trade']['id'])
        # print(f'Trade {transaction_hash}')
        d, f = trade_fee(transaction_hash)
        # print(d, f)
        dict["Date"].append(d) 
        dict["Fee"].append(f)
    elif "feeSharesReceivedEvent" in activity:
        # print(f'FeeShares {activity["feeSharesReceivedEvent"]}')
        transaction_hash = get_part_before_slash(activity['feeSharesReceivedEvent']['id'])
        d, f = mgmt_fee(transaction_hash)
        shares = float(activity["feeSharesReceivedEvent"]["shares"])
        print(f'Date {d} Fee (USD): {f} Shares: {shares}')
        fee_mgmt["Date"].append(d)
        fee_mgmt["Fee"].append(shares)
    else:
        # do nothing
        pass
        
    
def AggregatByMonth(df):
    # Convert the Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    # Extract year and month from the Date column
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Group by the new YearMonth column and sum the Fee column
    monthly_fees = df.groupby('YearMonth')['Fee'].sum().reset_index()
    # Round the Fee column to 2 decimal places
    monthly_fees['Fee'] = monthly_fees['Fee'].round(2)
    # Display the aggregated DataFrame
    print(monthly_fees)
    return monthly_fees



df = pd.DataFrame(dict)
monthly_fees = AggregatByMonth(df)


# Export to LaTeX

pandas_to_latex(
    monthly_fees, 
    './report/monthly-tx-expense.tex', 
    caption = 'Транзакционные расходы (USD)', 
    label = 'monthly-tx-expense')

df_mgmt = pd.DataFrame(fee_mgmt)
print(df_mgmt)
monthly_fees_mgmt = AggregatByMonth(df_mgmt)

pandas_to_latex(
    monthly_fees_mgmt, 
    './report/monthly-mgmt-fee.tex', 
    caption = 'Комиссия за управление (акции фонда)', 
    label = 'monthly-mgmt-fee')
