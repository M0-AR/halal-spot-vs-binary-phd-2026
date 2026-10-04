"""Live public-data fetcher: Yahoo Finance (stocks), Frankfurter/ECB (FX), CoinGecko (crypto).
No API keys. All calls have offline synthetic fallback so benchmarks are reproducible.
"""
import json, time, datetime as dt
import requests
import pandas as pd
import numpy as np

def fetch_stock_daily(symbol="AAPL", period="1y"):
    """Yahoo chart API (no key). Returns DataFrame with close."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 research"}, timeout=20)
        r.raise_for_status()
        j = r.json()["chart"]["result"][0]
        ts = j["timestamp"]
        closes = j["indicators"]["quote"][0]["close"]
        df = pd.DataFrame({"date": pd.to_datetime(ts, unit="s"), "close": closes}).dropna()
        df["symbol"] = symbol
        df["source"] = "yahoo"
        return df
    except Exception as e:
        print(f"[live_fetch] stock fallback for {symbol}: {e}")
        return synthetic_gbm(symbol=symbol, n=250, s0=150.0)

def fetch_fx_daily(base="USD", target="EUR", days=365):
    """Frankfurter (ECB). No key."""
    try:
        end = dt.date.today()
        start = end - dt.timedelta(days=days)
        url = f"https://api.frankfurter.app/{start}..{end}?from={base}&to={target}"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        rates = r.json()["rates"]
        rows = [{"date": pd.to_datetime(k), "close": v[target], "symbol": f"{base}{target}=X", "source": "frankfurter"} for k, v in sorted(rates.items())]
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"[live_fetch] fx fallback: {e}")
        return synthetic_gbm(symbol=f"{base}{target}=X", n=250, s0=0.9)

def fetch_crypto_daily(coin="bitcoin", vs="usd", days=365):
    """CoinGecko free market_chart. No key (rate-limited)."""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency={vs}&days={days}"
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        prices = r.json()["prices"]
        df = pd.DataFrame(prices, columns=["ms", "close"])
        df["date"] = pd.to_datetime(df["ms"], unit="ms")
        df = df[["date", "close"]]
        df["symbol"] = coin
        df["source"] = "coingecko"
        return df
    except Exception as e:
        print(f"[live_fetch] crypto fallback: {e}")
        return synthetic_gbm(symbol=coin, n=365, s0=60000.0)

def synthetic_gbm(symbol="SYNTH", n=500, s0=100.0, mu=0.0003, sigma=0.015, seed=2026):
    rng = np.random.default_rng(seed + abs(hash(symbol)) % 10000)
    rets = rng.normal(mu, sigma, n)
    closes = s0 * np.exp(np.cumsum(rets))
    dates = pd.date_range(end=dt.date.today(), periods=n)
    return pd.DataFrame({"date": dates, "close": closes, "symbol": symbol, "source": "synthetic-gbm"})

if __name__ == "__main__":
    for fn in [lambda: fetch_stock_daily("AAPL"),
               lambda: fetch_fx_daily("USD", "EUR"),
               lambda: fetch_crypto_daily("bitcoin")]:
        df = fn()
        print(df.tail(2).to_string(), f"\nrows={len(df)} source={df['source'].iloc[0]}")
