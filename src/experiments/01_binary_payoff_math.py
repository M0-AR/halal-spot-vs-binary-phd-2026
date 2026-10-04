"""EXP-01: Binary payoff math — why payout < 100% creates structural negative expectancy.
Pocket Option typical payout 70-95% (we test 80% and 92% upper bound).
Breakeven win-rate = 1 / (1+payout). For 80%: 55.56%. For 92%: 52.08%.
Even a 50%-accurate AI loses money; retail Nadex study: -9.9% avg return.
"""
import json, numpy as np

def breakeven(payout):
    return 1.0 / (1.0 + payout)

def simulate(win_rate, payout=0.80, n=10000, stake=1.0, seed=1):
    rng = np.random.default_rng(seed)
    wins = rng.random(n) < win_rate
    pnl = np.where(wins, stake*payout, -stake)
    return float(pnl.mean()), float(pnl.sum())

def main():
    out = {"payouts": {}, "simulations": []}
    for p in [0.70, 0.80, 0.92]:
        out["payouts"][str(p)] = {"breakeven_win_rate": breakeven(p)}
    # key claim: AI at 50%, 55%, 60% accuracy
    for wr in [0.50, 0.53, 0.55, 0.60, 0.70]:
        mean, total = simulate(wr, payout=0.80, n=20000, seed=2026)
        out["simulations"].append({"win_rate": wr, "payout": 0.80, "ev_per_trade": round(mean, 4), "total_20k": round(total, 1)})
    # upper-bound payout 92%
    for wr in [0.50, 0.52, 0.55]:
        mean, _ = simulate(wr, payout=0.92, n=20000, seed=7)
        out["simulations"].append({"win_rate": wr, "payout": 0.92, "ev_per_trade": round(mean, 4), "total_20k": round(mean*20000, 1)})
    # hidden pattern: variance kills — prob of ruin with Kelly-less fixed staking
    print(json.dumps(out, indent=2))
    with open("results/exp01_payoff.json", "w") as f:
        json.dump(out, f, indent=2)
    # verdict
    print("\nVERDICT EXP-01: at payout 80%, need >55.56% wins just to break even. Coin-flip AI (50%) EV=-0.10/trade.")
    return out

if __name__ == "__main__":
    main()
