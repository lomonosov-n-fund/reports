# How to download indeces?


Goto these pages,  goto Index Constituents, search/click for "Get the data", download to index/<date> 

[CoinDesk Large Cap Select Index (DLCS)](https://www.coindesk.com/indices/dlcs)

[CoinDesk Stablecoin Index (CSC)](https://www.coindesk.com/indices/csc)

1Q2025 CoinDesk changes its indices. Use historic-data instead.

Download native:
https://www.coingecko.com/en/coins/bitcoin/historical_data
https://www.coingecko.com/en/coins/ethereum/historical_data
https://www.coingecko.com/en/coins/solana/historical_data

Download stablecoins:
https://www.coingecko.com/en/coins/tether/historical_data
https://www.coingecko.com/en/coins/usdc/historical_data
https://www.coingecko.com/en/coins/dai/historical_data



- Run `market_cap_weights.py` from project root to compute weights
- Add manually the computed weights into CSV files ./index/YYYY-MM-DD


For 2026 Q1 report:
```sh
python market_cap_weights.py btc eth sol --date 2026-04-09 
python market_cap_weights.py usdt usdc dai --date 2026-04-09 
```


For 2025 Q4 report:
```sh
python market_cap_weights.py btc eth sol --date 2026-01-15 
python market_cap_weights.py usdt usdc dai --date 2026-01-15 
```

For 2025 Q3 report:
```sh
python market_cap_weights.py btc eth sol --date 2025-10-25 
python market_cap_weights.py usdt usdc dai --date 2025-10-25
```


For 2025 Q1 report:
```sh
python market_cap_weights.py btc eth sol --date 2025-04-03 
python market_cap_weights.py usdt usdc dai --date 2025-04-03
```

