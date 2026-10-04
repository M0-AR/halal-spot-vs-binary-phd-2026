"""Generate assets/demo.gif (+mp4 if ffmpeg) from REAL results. No mocks."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

os.makedirs("assets", exist_ok=True)
d1 = json.load(open("results/exp01_payoff.json"))
sims80 = [s for s in d1["simulations"] if s["payout"] == 0.80]
wr = [s["win_rate"] for s in sims80]
ev = [s["ev_per_trade"] for s in sims80]
d3 = json.load(open("results/exp03_speed_vs_gharar.json"))
hs = [x["horizon_sec"] for x in d3["sweep_horizon"]]
w60 = [x["realized_wr_p60"] for x in d3["sweep_horizon"]]

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
fig.suptitle("LIVE PROOF: same edge wins on spot, loses on binary", fontsize=12, fontweight="bold")

def frame(i):
    for a in ax:
        a.clear()
    k = max(2, i + 1)
    ax[0].plot(wr[:k], ev[:k], marker="o", color="#0ea5a4", linewidth=3)
    ax[0].axhline(0, color="red", linestyle="--")
    ax[0].set_xlabel("Win rate")
    ax[0].set_ylabel("EV per $1 (payout 80%)")
    ax[0].set_title("Binary bleeds below 55.56%")
    ax[0].set_xlim(0.49, 0.71)
    ax[0].set_ylim(-0.15, 0.3)
    ax[1].semilogx(hs[:k] if k <= 5 else hs, (w60[:k] if k <= 5 else w60), marker="o", color="#7c3aed", linewidth=3)
    ax[1].axhline(0.5, color="red", linestyle="--")
    ax[1].set_xlabel("Horizon (sec)")
    ax[1].set_ylabel("Realized WR (60% AI edge)")
    ax[1].set_title("5s→50.8% · 60s→55.5% · 1d→79%")
    ax[1].set_ylim(0.48, 0.85)
    fig.tight_layout()

anim = FuncAnimation(fig, frame, frames=8, interval=600)
anim.save("assets/demo.gif", writer="pillow", dpi=90)
print("saved assets/demo.gif")
try:
    anim.save("assets/demo.mp4", writer="ffmpeg", dpi=110)
    print("saved assets/demo.mp4")
except Exception as e:
    print(f"mp4 skipped (ffmpeg missing): {e}")
    # fallback: copy gif path note
    open("assets/demo.mp4.note.txt", "w").write("Install ffmpeg to regenerate mp4; demo.gif is the canonical demo.")
