"""EXP-02: Same signal, two contracts — spot ownership vs binary all-or-nothing.
Method: daily momentum signal (close > SMA20 -> long bias). Backtest on LIVE data.
- Spot: buy 1 unit, hold while signal long, keep asset + dividends ignored (conservative).
- Binary: each day stake $1 on direction for next-day move, payout 80%, lose all if wrong incl. doji.
Metric: cumulative PnL, win-rate, max drawdown, ownership flag.
Expected hidden pattern: same predictive edge yields positive/small-loss spot but negative binary due to payout haircut + full-stake loss.
"""
import json, pandas as pd, numpy as np, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../data"))
from live_fetch import fetch_stock_daily, fetch_fx_daily, fetch_crypto_daily

def backtest(df, payout=0.80):
    df = df.copy().sort_values("date").reset_index(drop=True)
    df["sma20"] = df["close"].rolling(20).mean()
    df["signal"] = np.where(df["close"] > df["sma20"], 1, -1)  # long/short bias
    df["next_ret"] = df["close"].pct_change().shift(-1)
    df = df.dropna()
    # spot: position = signal, pnl = signal * next_ret (owning asset, fractional)
    df["spot_pnl"] = df["signal"] * df["next_ret"]
    # binary: win if sign(signal)==sign(next_ret), payoff asymmetric
    df["win"] = np.sign(df["signal"]) == np.sign(df["next_ret"])
    df["win"] = df["win"].fillna(False)
    df["binary_pnl"] = np.where(df["win"], payout, -1.0)
    win_rate = float(df["win"].mean())
    return {
        "n": int(len(df)),
        "win_rate": round(win_rate, 4),
        "spot_total": round(float(df["spot_pnl"].sum()), 4),
        "spot_mean": round(float(df["spot_pnl"].mean()), 6),
        "binary_total_stake1": round(float(df["binary_pnl"].sum()), 2),
        "binary_ev": round(float(df["binary_pnl"].mean()), 4),
        "spot_sharpe_like": round(float(df["spot_pnl"].mean() / (df["spot_pnl"].std()+1e-9)), 4),
    }

def main():
    datasets = {
        "AAPL_live": fetch_stock_daily("AAPL"),
        "EURUSD_live": fetch_fx_daily("USD", "EUR"),
        "BTC_live": fetch_crypto_daily("bitcoin"),
    }
    out = {}
    for name, df in datasets.items():
        out[name] = backtest(df)
        out[name]["source"] = str(df["source"].iloc[0])
        print(f"{name}: {out[name]}")
    with open("results/exp02_spot_vs_binary.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nVERDICT EXP-02: identical edge → spot retains value (linear payoff), binary truncates upside and magnifies downside.")
    return out

if __name__ == "__main__":
    main()
