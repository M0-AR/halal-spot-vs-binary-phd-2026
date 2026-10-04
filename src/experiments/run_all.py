"""Run all experiments in order, aggregate into results/summary.json + figures."""
import os, json, subprocess, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

EXPS = ["01_binary_payoff_math.py", "02_spot_vs_binary_backtest.py", "03_ai_speed_gharar.py", "04_sharia_screen.py", "05_live_verification.py"]

def run():
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)
    for e in EXPS:
        print(f"\n===== {e} =====")
        r = subprocess.run([sys.executable, f"src/experiments/{e}"], capture_output=False)
        if r.returncode != 0:
            print(f"FAILED {e}")
            sys.exit(1)
    # figure: binary EV vs win-rate
    import json as J
    d = J.load(open("results/exp01_payoff.json"))
    sims80 = [s for s in d["simulations"] if s["payout"]==0.80]
    wr = [s["win_rate"] for s in sims80]
    ev = [s["ev_per_trade"] for s in sims80]
    plt.figure()
    plt.plot(wr, ev, marker="o")
    plt.axhline(0, linestyle="--")
    plt.xlabel("Win rate")
    plt.ylabel("EV per $1 trade (payout 80%)")
    plt.title("Binary options EV: breakeven 55.56%")
    plt.savefig("figures/fig01_ev.png", dpi=150)
    # figure: horizon vs realized win-rate
    d3 = J.load(open("results/exp03_speed_vs_gharar.json"))
    hs = [x["horizon_sec"] for x in d3["sweep_horizon"]]
    w60 = [x["realized_wr_p60"] for x in d3["sweep_horizon"]]
    plt.figure()
    plt.semilogx(hs, w60, marker="o")
    plt.axhline(0.5, linestyle="--")
    plt.xlabel("Horizon (sec, log)")
    plt.ylabel("Realized win-rate (AI edge 60%)")
    plt.title("Speed cannot rescue 60s gharar: noise dominates")
    plt.savefig("figures/fig03_horizon.png", dpi=150)
    print("\nSaved figures/fig01_ev.png figures/fig03_horizon.png")
    summary = {"status": "all-passed", "exps": EXPS}
    J.dump(summary, open("results/summary.json","w"), indent=2)

if __name__ == "__main__":
    run()
