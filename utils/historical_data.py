"""
Historical data utilities for accessing price data from CSV files.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class HistoricalDataManager:
    """
    Manages access to historical price data from CSV files in the historical-data directory.
    
    This class provides methods to:
    - Load and cache historical price data
    - Get prices for specific dates
    - Validate data availability
    - Get available symbols and date ranges
    """
    
    def __init__(self, data_dir: str = "./historical-data"):
        """
        Initialize the HistoricalDataManager.
        
        Args:
            data_dir: Directory containing historical data CSV files
        """
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, pd.DataFrame] = {}
        self._available_symbols: Optional[List[str]] = None
        
    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols (coins) in the historical data.
        
        Returns:
            List of available symbol names (e.g., ['btc', 'eth', 'sol'])
        """
        if self._available_symbols is None:
            if not self.data_dir.exists():
                self._available_symbols = []
            else:
                csv_files = list(self.data_dir.glob("*.csv"))
                self._available_symbols = [f.stem.lower() for f in csv_files]
        return self._available_symbols.copy()
    
    def is_symbol_available(self, symbol: str) -> bool:
        """
        Check if historical data is available for a given symbol.
        
        Args:
            symbol: Symbol to check (e.g., 'btc', 'eth')
            
        Returns:
            True if data is available, False otherwise
        """
        return symbol.lower() in self.get_available_symbols()
    
    def _load_symbol_data(self, symbol: str) -> pd.DataFrame:
        """
        Load and cache historical data for a symbol.
        
        Args:
            symbol: Symbol to load (e.g., 'btc', 'eth')
            
        Returns:
            DataFrame with historical price data
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        symbol_lower = symbol.lower()
        
        if symbol_lower not in self._cache:
            csv_path = self.data_dir / f"{symbol_lower}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"No price data file found for {symbol}: {csv_path}")
            
            df = pd.read_csv(csv_path)
            df['snapped_at'] = pd.to_datetime(df['snapped_at'])
            
            # Make timezone-naive for consistent comparison
            df['snapped_at'] = df['snapped_at'].dt.tz_localize(None)
            
            self._cache[symbol_lower] = df
        
        return self._cache[symbol_lower]
    
    def get_price(self, symbol: str, date: str) -> float:
        """
        Get historical price for a symbol on a specific date.
        
        Args:
            symbol: Symbol to get price for (e.g., 'btc', 'eth')
            date: Date in YYYY-MM-DD format
            
        Returns:
            Price for the symbol on the specified date
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If no data is available for the date
        """
        df = self._load_symbol_data(symbol)
        
        target_date = pd.to_datetime(date).tz_localize(None)
        df_filtered = df[df['snapped_at'] <= target_date]
        
        if df_filtered.empty:
            raise ValueError(f"No price data for {symbol} on or before {date}")
        
        return df_filtered.iloc[-1]['price']
    
    def get_price_safe(self, symbol: str, date: str, default: Optional[float] = None) -> Optional[float]:
        """
        Get historical price safely, returning None if not available.
        
        Args:
            symbol: Symbol to get price for
            date: Date in YYYY-MM-DD format
            default: Default value to return if price not available
            
        Returns:
            Price if available, default value otherwise
        """
        try:
            return self.get_price(symbol, date)
        except (FileNotFoundError, ValueError):
            return default
    
    def get_date_range(self, symbol: str) -> tuple[datetime, datetime]:
        """
        Get the date range available for a symbol.
        
        Args:
            symbol: Symbol to get date range for
            
        Returns:
            Tuple of (earliest_date, latest_date)
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        df = self._load_symbol_data(symbol)
        min_date = df['snapped_at'].min().to_pydatetime()
        max_date = df['snapped_at'].max().to_pydatetime()
        return min_date, max_date
    
    def get_latest_price(self, symbol: str) -> float:
        """
        Get the most recent price for a symbol.
        
        Args:
            symbol: Symbol to get latest price for
            
        Returns:
            Most recent price
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        df = self._load_symbol_data(symbol)
        return df.iloc[-1]['price']
    
    def get_latest_date(self, symbol: str) -> datetime:
        """
        Get the most recent date available for a symbol.
        
        Args:
            symbol: Symbol to get latest date for
            
        Returns:
            Most recent date
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        df = self._load_symbol_data(symbol)
        return df.iloc[-1]['snapped_at']
    
    def clear_cache(self):
        """Clear the internal cache of loaded data."""
        self._cache.clear()
        self._available_symbols = None
    
    def get_cache_info(self) -> Dict[str, any]:
        """
        Get information about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_symbols': list(self._cache.keys()),
            'cache_size': len(self._cache),
            'available_symbols': len(self.get_available_symbols())
        } 