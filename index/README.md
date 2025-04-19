# How to download indeces?


Goto these pages,  goto Index Constituents, search/click for "Get the data", download to index/<date> 

[CoinDesk Large Cap Select Index (DLCS)](https://www.coindesk.com/indices/dlcs)

[CoinDesk Stablecoin Index (CSC)](https://www.coindesk.com/indices/csc)

1Q2025 CoinDesk changes its indices. Use historic-data instead.

Downloads:
https://www.coingecko.com/en/coins/bitcoin/historical_data
https://www.coingecko.com/en/coins/ethereum/historical_data
https://www.coingecko.com/en/coins/solana/historical_data

Run `market_cap_weights.py` from project root to compute weights:


For 2025 Q1 report:
```sh
python market_cap_weights.py btc eth sol --date 2025-04-03 
python market_cap_weights.py usdt usdc dai --date 2025-04-03
```

