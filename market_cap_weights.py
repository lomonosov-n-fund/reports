import click
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz

@click.command(help="""
Calculate market capitalization weights for specified cryptocurrencies.

The script reads historical data from CSV files in the ./historical-data directory
and calculates relative weights based on market capitalization.

Examples:
    # Calculate weights using most recent data
    python market_cap_weights.py btc eth sol

    # Calculate weights for a specific date
    python market_cap_weights.py btc eth --date 2024-03-31

    # Show this help message
    python market_cap_weights.py --help
""")
@click.argument('coins', nargs=-1, required=True, metavar='COIN...')
@click.option('--date', '-d', 
              help="Target date in YYYY-MM-DD format. If not specified, uses most recent available data. "
                   "The script will use data from the last available date on or before the specified date.")
def market_cap_weights(coins, date):
    """Calculate market capitalization weights for specified cryptocurrencies.
    
    COIN... List of coin symbols to include in calculation (e.g., btc eth sol)
    """
    # Convert coins to lowercase for consistency
    coins = [coin.lower() for coin in coins]
    
    # Initialize dictionary to store data
    market_caps = {}
    
    # Process each specified coin
    for coin in coins:
        file_path = Path('historical-data') / f'{coin}.csv'
        if not file_path.exists():
            click.echo(f"Error: No data file found for {coin}", err=True)
            return
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        df['snapped_at'] = pd.to_datetime(df['snapped_at'])
        
        # Get the most recent date if not specified
        if date:
            target_date = pd.Timestamp(date).tz_localize(None)  # Make timezone-naive for comparison
            df['snapped_at'] = df['snapped_at'].dt.tz_localize(None)  # Make timezone-naive for comparison
            # Find the closest date to the target date
            df = df[df['snapped_at'] <= target_date]
            if df.empty:
                click.echo(f"Error: No data available for {coin} on or before {date}", err=True)
                return
            latest_data = df.iloc[-1]
        else:
            latest_data = df.iloc[-1]
        
        market_caps[coin] = latest_data['market_cap']
    
    # Calculate total market cap
    total_market_cap = sum(market_caps.values())
    
    # Calculate and display weights
    click.echo(f"\nMarket Capitalization Weights (as of {date or latest_data['snapped_at'].strftime('%Y-%m-%d')}):")
    click.echo("-" * 50)
    click.echo(f"{'Coin':<8} {'Market Cap ($)':<20} {'Weight (%)':<10}")
    click.echo("-" * 50)
    
    for coin, market_cap in market_caps.items():
        weight = (market_cap / total_market_cap) * 100
        click.echo(f"{coin.upper():<8} {market_cap:,.2f} {'':<5} {weight:.2f}%")

if __name__ == "__main__":
    market_cap_weights() 