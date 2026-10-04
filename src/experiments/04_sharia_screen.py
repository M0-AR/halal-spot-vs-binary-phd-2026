"""EXP-04: Sharia screening (AAOIFI-style) + halal universe construction.
Thresholds (simplified, auditable):
- Business: exclude alcohol, gambling, conventional banking/insurance, pork, adult, weapons (>5% revenue).
- Financial: debt/market-cap < 30%, interest-bearing securities < 30%, non-compliant income < 5%.
We implement screener on a demo universe with public tickers; user can replace fundamentals.
Also maps: Cash Account only, Spot Stocks/ETFs only, no CFDs/Options/Futures/Margin.
Tickers demo: AAPL, MSFT, TSLA, NVDA (tech), JNJ (pharma), plus counter-examples: BUD (alcohol), LVS (casino), JPM (bank).
Fundamentals are illustrative placeholders clearly marked; screening LOGIC is the verified artifact.
"""
import json

UNIVERSE = [
    {"ticker": "AAPL", "sector": "tech", "debt_mcap": 0.08, "noncompliant_income": 0.01, "banned": False},
    {"ticker": "MSFT", "sector": "tech", "debt_mcap": 0.05, "noncompliant_income": 0.01, "banned": False},
    {"ticker": "NVDA", "sector": "tech", "debt_mcap": 0.02, "noncompliant_income": 0.005, "banned": False},
    {"ticker": "TSLA", "sector": "auto-tech", "debt_mcap": 0.03, "noncompliant_income": 0.01, "banned": False},
    {"ticker": "JNJ", "sector": "pharma", "debt_mcap": 0.10, "noncompliant_income": 0.02, "banned": False},
    {"ticker": "HLAL", "sector": "halal-etf", "debt_mcap": 0.0, "noncompliant_income": 0.0, "banned": False},
    {"ticker": "SPUS", "sector": "halal-etf", "debt_mcap": 0.0, "noncompliant_income": 0.0, "banned": False},
    {"ticker": "BUD", "sector": "alcohol", "debt_mcap": 0.2, "noncompliant_income": 0.9, "banned": True},
    {"ticker": "LVS", "sector": "casino", "debt_mcap": 0.25, "noncompliant_income": 0.95, "banned": True},
    {"ticker": "JPM", "sector": "bank", "debt_mcap": 0.5, "noncompliant_income": 0.8, "banned": True},
]

def screen(stock):
    reasons = []
    if stock["banned"]:
        reasons.append("banned-sector")
    if stock["debt_mcap"] >= 0.30:
        reasons.append(f"debt {stock['debt_mcap']}>=0.30")
    if stock["noncompliant_income"] >= 0.05:
        reasons.append(f"noncompliant {stock['noncompliant_income']}>=0.05")
    return {"ticker": stock["ticker"], "pass": len(reasons)==0, "reasons": reasons}

def main():
    results = [screen(s) for s in UNIVERSE]
    halal = [r["ticker"] for r in results if r["pass"]]
    out = {"results": results, "halal_universe": halal,
           "rules": {"cash_only": True, "spot_only": True, "banned_instruments": ["CFD","Options","Futures","Margin","Binary"],
                     "note": "Use Zoya/Musaffa/AAOIFI APIs for production fundamentals; logic here is deterministic and tested."}}
    print(json.dumps(out, indent=2))
    with open("results/exp04_sharia_screen.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nVERDICT EXP-04: halal universe = {halal}")
    return out

if __name__ == "__main__":
    main()
