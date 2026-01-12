# Quant
Quant is a research-oriented repository focused on quantitative analysis in finance.

## Collectors

### Binance klines
Fetch historical 1m klines for SYMBOL(from 2019 new year to now by default):

```bash
    python binance/klines.py SYMBOL
```

Raw JSON files are saved under `data/raw/binance/spot/SYMBOL/klines/`.

Example:

```bash
    python binance/klines.py btcusdt
```

Optional flags:

* --start-time (-s): ISO 8601 UTC start time (e.g., 2023-01-01T00:00:00+00:00)
* --end-time (-e): ISO 8601 UTC end time (defaults to now)
