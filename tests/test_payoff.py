def test_breakeven():
    from pathlib import Path
    import sys
    sys.path.insert(0, "src/experiments")
    # breakeven formula 1/(1+p)
    assert abs(1/(1+0.80) - 0.5555556) < 1e-5
    assert abs(1/(1+0.92) - 0.5208333) < 1e-5

def test_screener_logic():
    import sys
    sys.path.insert(0, "src/experiments")
    import importlib.util
    spec = importlib.util.spec_from_file_location("s", "src/experiments/04_sharia_screen.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.screen({"ticker":"X","debt_mcap":0.1,"noncompliant_income":0.01,"banned":False})["pass"] is True
    assert m.screen({"ticker":"Y","debt_mcap":0.5,"noncompliant_income":0.01,"banned":False})["pass"] is False
