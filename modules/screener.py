from .market_data import live_quote, load_history
from .technical import state_from_history
from .portfolio import analyze

def market_regime():
    total, rows = 0, []
    for t in ["SPY", "QQQ", "SMH"]:
        try:
            q = live_quote(t)
            hist = load_history(t, "1y")
            s, _ = state_from_history(hist, t, q["price"])
            score = int(s["Price"] > s["EMA50"]) + int(s["Price"] > s["EMA200"]) + int(s["EMA50"] > s["EMA200"]) + int(s["RSI"] >= 45)
            total += score
            rows.append({"Ticker": t, "Price": s["Price"], "Score": score, "RSI": round(s["RSI"], 1), "Quote Source": q["source"], "Quote Time": q["time"]})
        except Exception:
            rows.append({"Ticker": t, "Price": None, "Score": 0, "RSI": "N/A", "Quote Source": "error", "Quote Time": ""})
    if total >= 10:
        return {"name": "Bullish", "score": total, "modifier": 1.0, "css": "green", "rows": rows}
    if total >= 7:
        return {"name": "Neutral", "score": total, "modifier": 0.6, "css": "yellow", "rows": rows}
    return {"name": "Defensive", "score": total, "modifier": 0.25, "css": "red", "rows": rows}

def screen_tickers(tickers, positions_map, account, cash, reg, max_holdings, holding_count, kelly_map, period):
    results, details = [], {}
    for t in tickers:
        try:
            q = live_quote(t)
            hist = load_history(t, period)
            s, ind_df = state_from_history(hist, t, q["price"])
            krow = kelly_map.get(t, {"Ticker": t, "Win Rate %": 55, "Avg Win %": 10, "Avg Loss %": 6, "Kelly Fraction": 0.25})
            res = analyze(s, positions_map.get(t, {}), account, cash, reg, max_holdings, holding_count, krow)
            res["Quote Source"] = q["source"]
            res["Quote Time"] = q["time"]
            details[t] = (ind_df, s, res)
            results.append(res)
        except Exception as e:
            results.append({"Ticker": t, "Action": f"ERROR: {e}", "Entry Score": 0})
    return results, details
