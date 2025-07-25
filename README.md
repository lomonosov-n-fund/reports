# Reports Documentation

## Scripts Overview

### 1. Vault Activity Query (`query-vault-activity.py`)

Fetches historical vault activity data from the Enzyme API and stores it for use by other scripts.

**Features:**
- Retrieves vault activities from fund inception to current date
- Stores data in JSON format for other scripts to use
- Output filename and directory are configurable via CLI options

**Usage:**
```bash
# Basic usage (outputs to vault-activity.json in current directory)
python query-vault-activity.py

# Save to a custom output directory (e.g., ./tmp)
python query-vault-activity.py --output-dir ./tmp

# Specify a custom output filename
python query-vault-activity.py --filename my-activity.json

# Specify both custom filename and directory
python query-vault-activity.py --filename my-activity.json --output-dir ./tmp

# Enable verbose output
python query-vault-activity.py --output-dir ./tmp --verbose
```

**CLI Options:**
- `--filename`: Output filename for vault activity data (default: vault-activity.json)
- `--output-dir`: Directory to save the output file (default: current directory)
- `--verbose`: Enable verbose output

**Output Files:**
- The output file will be saved as `<output-dir>/<filename>`, e.g., `./tmp/vault-activity.json`

### 2. Depositors Report (`depositors.py`)

Analyzes depositor activity and share distribution in the fund.

**Features:**
- Calculates total number of depositors and shares
- Filters depositors by date range
- Generates LaTeX tables with Russian headers
- Supports quarter-specific reporting

**Usage:**
```bash
# test report for the last quarter, the output goes to ./tmp
python depositors.py --verbose --latex

# silent production run with the output to ./report/depositors_2025_Q2.tex
python depositors.py --latex --quarter 2 --year 2025 --output-dir ./report
```

**Output Files:**
- `depositors_{year}_Q{quarter}.tex`: Depositor statistics with share counts

### 3. Performance Report (`performance.py`)

Generates comprehensive performance analysis of the fund.

**Features:**
- Calculates quarterly and inception-to-date performance
- Tracks net share value and gross asset value
- Generates performance visualization plots
- Supports both operator view and LaTeX output

**Usage:**
```bash
# Interactive test mode with plots
python performance.py --verbose --operator

# Silent production run Generate LaTeX tables and plots
python performance.py --latex --quarter 2 --year 2025 --output-dir ./report
```

**Output Files:**
- Performance plots:
  - `performance_quarter_{year}_Q{quarter}.png`: Quarterly net share value
  - `gross_asset_value_quarter_{year}_Q{quarter}.png`: Quarterly gross asset value
  - `performance_since_inception_{year}_Q{quarter}.png`: Net share value since inception
  - `gross_asset_value_since_inception_{year}_Q{quarter}.png`: Gross asset value since inception

### 4. Expenses Report (`expenses.py`)

Analyzes fund expenses including transaction fees and management fees.

**Features:**
- Calculates transaction fees in USD
- Tracks management fee distributions
- Uses CoinGecko API for historical ETH prices
- Caches price data for efficiency
- Aggregates expenses by month

**Usage:**
```bash
# test report for the last quarter, the output goes to ./tmp
python expenses.py --verbose --latex
```

**Output Files:**
- `monthly-tx-expense_{year}_Q{quarter}.tex`: Monthly transaction fees in USD
- `monthly-mgmt-fee_{year}_Q{quarter}.tex`: Monthly management fees in fund shares

### 5. Asset Allocation Report (`asset-allocation.py`)

Analyzes current portfolio composition and compares with target allocations.

**Features:**
- Fetches current portfolio from Enzyme API
- Calculates allocation across asset classes using historical prices
- Compares with target allocations from index data
- Generates in-class allocation analysis
- Supports configurable report and index dates

**Usage:**
```bash
# Basic usage with defaults (report-date: 2025-07-08, index-date: 2025-07-07)
python asset-allocation.py --verbose --latex

# Specify custom report date for asset values
python asset-allocation.py --verbose --report-date 2025-07-08 --latex

# Specify both report and index dates
python asset-allocation.py --verbose --report-date 2025-07-08 --index-date 2025-07-07 --latex

# Use different index date for comparison
python asset-allocation.py --verbose --index-date 2025-04-03 --latex

# Production run with custom dates
python asset-allocation.py --latex --quarter 2 --year 2025 --output-dir ./report --report-date 2025-06-30 --index-date 2025-06-29
```

**CLI Options:**
- `--report-date`: Date for computing asset values using historical prices (YYYY-MM-DD format, default: 2025-07-08)
- `--index-date`: Date for index comparison data (YYYY-MM-DD format, default: 2025-07-07)

**Output Files:**
- `assets-by-class_{year}_Q{quarter}.tex`: Overall asset allocation
- `inclass-Native-Coins_{year}_Q{quarter}.tex`: Native coins allocation
- `inclass-Stable-Coins_{year}_Q{quarter}.tex`: Stablecoins allocation

## Recommended Execution Order

For generating a complete quarterly report, execute scripts in this order:
1. `query-vault-activity.py` - Fetch latest vault activity data (required for expenses and depositors analysis)
2. `depositors.py` - Generate depositor statistics
3. `performance.py` - Calculate performance metrics
4. `expenses.py` - Analyze expenses (requires vault activity data)
5. `asset-allocation.py` - Generate current allocation report

## Environment Setup

1. Use Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Required environment variables in `.env`:
```
ENZYME_API_KEY=your_api_key
ENZYME_VAULT_ADDRESS=your_vault_address
COINGECKO_API_KEY=your_coingecko_api_key  # Required for expenses.py
MORALIS_API_KEY=your_moralis_api_key      # Required for expenses.py
```

## Common Command Line Options

All reporting scripts support these options:
- `--dry-run`: Preview without saving files
- `--quarter`: Quarter number (1-4)
- `--year`: Reporting year
- `--output-dir`: Output directory (default: "./outputs")
- `--verbose`: Show detailed output
- `--operator`: Show interactive plots (performance.py) or console output
- `--latex`: Generate LaTeX files

## Dependencies

Key dependencies:
- `click`: Command-line interface
- `pandas`: Data processing
- `requests`: API communication
- `python-dotenv`: Environment variable management
- `matplotlib`: Plot generation (performance.py)
- `moralis`: Transaction data retrieval (expenses.py) 