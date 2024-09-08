# Reports for Lomonosov Funds

## Setup project

I tested the code only on Ubuntu 22.04.

### Start Python virtual environment

```sh
python3 -m venv env
source env/bin/activate
```

### Install dependencies

```sh
pip install -r requirements.txt
```

To save the list of dependencies

```sh
pip freeze > requirements.txt
```

### Add API keys to your `.env` file

```txt
MORALIS_API_KEY=...
COINGECKO_API_KEY=...
ENZYME_API_KEY=...
ENZYME_VAULT_ADDRESS=...
```

You can get free API keys from corresponding API providers

## Query Enzyme API to download transactions as JSON

```sh
python query-enzyme.py > vault-activity.json
```

## Run Python scripts to generate LaTeX table for the report

### Transaction expenses

```sh
python ./report-expenses.py vault-activity.json
```

### Asset allocation

```sh
python ./report-asset-allocation.py
```

### Fund performance

```sh
python ./report-performance.py
```
