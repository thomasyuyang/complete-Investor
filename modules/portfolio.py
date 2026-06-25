import math
import numpy as np
from .kelly import kelly

def money(x):
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return "$0"

def price(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return "N/A"

def shares_for(dollars, px):
    return max(0, math.floor(dollars / px)) if px and px > 0 else 0

def max_pct(ticker):
    ticker = ticker.upper()
    if ticker == "SMH":
        return 0.80
    if ticker in ["VGT","QQQ","QQQM","VOO","SCHD"]:
        return 0.50
    if ticker in ["NVDA","MSFT","GOOGL","AVGO","TSM","AAPL","COST","V"]:
        return 0.25
    if ticker in ["MO","O","JNJ"]:
        return 0.20
    return 0.20

def price_level(s):
    if s["Price"] < s["EMA50"] or s["EMA20"] < s["EMA50"] * 0.985:
        return "Weak / below trend", "red"
    if s["DIST_HIGH"] > -3 and s["RSI"] >= 68:
        return "High price level", "red"
    if s["DIST_HIGH"] > -3:
        return "Near high", "yellow"
    if s["DIST_HIGH"] > -6:
        return "Slightly extended", "yellow"
    if -10 <= s["DIST_HIGH"] <= -6:
        return "Normal pullback", "green"
    if -16 <= s["DIST_HIGH"] < -10:
        return "Good pullback", "green"
    if s["DIST_HIGH"] < -16:
        return "Deep pullback", "blue"
    return "Neutral", "blue"

def dynamic_stop(s, avg_cost, has_position):
    if s["Ticker"] in ["NVDA","AVGO","TSM","AMD"]:
        stop = max(s["EMA50"] * 0.97, s["Price"] - 2.0 * s["ATR"])
    else:
        stop = max(s["EMA50"] * 0.98, s["Price"] - 1.8 * s["ATR"])
    if has_position and avg_cost > 0 and s["Price"] > avg_cost * 1.08:
        stop = max(stop, s["EMA20"] * 0.98, s["Price"] - 1.8 * s["ATR"])
    return stop

def entry_score(s, regime_name):
    score, reasons = 0, []
    for cond, pts, txt in [
        (s["Price"] > s["EMA200"], 8, "above EMA200"),
        (s["Price"] > s["EMA50"], 8, "above EMA50"),
        (s["EMA20"] > s["EMA50"], 7, "EMA20>EMA50"),
        (s["EMA50"] > s["EMA200"], 7, "EMA50>EMA200"),
    ]:
        if cond:
            score += pts
            reasons.append(txt)
    if -16 <= s["DIST_HIGH"] <= -6:
        score += 30
        reasons.append("good pullback")
    elif -6 < s["DIST_HIGH"] <= -3:
        score += 14
        reasons.append("slight pullback")
    elif s["DIST_HIGH"] > -3:
        score -= 10
        reasons.append("near high")
    elif s["DIST_HIGH"] < -16:
        score += 8
        reasons.append("deep pullback")
    if 42 <= s["RSI"] <= 60:
        score += 20
        reasons.append("healthy RSI")
    elif 60 < s["RSI"] <= 68:
        score += 10
    elif s["RSI"] > 70:
        score -= 15
    elif s["RSI"] < 35:
        score -= 8
    if s["ATR_PCT"] <= 3:
        score += 20
    elif s["ATR_PCT"] <= 5:
        score += 12
    else:
        score += 3
    if regime_name == "Defensive":
        score -= 20
    elif regime_name == "Neutral":
        score -= 8
    return max(0, min(100, score)), "; ".join(reasons)

def analyze(s, pos, account, cash, reg, max_holdings, holding_count, krow):
    shares = pos.get("shares", 0)
    avg = pos.get("avg_cost", 0.0)
    current_value = shares * s["Price"]
    has_pos = current_value > 0

    level, tone = price_level(s)
    score, reason = entry_score(s, reg["name"])
    stop = dynamic_stop(s, avg, has_pos)
    b, raw_k, cons_k = kelly(krow["Win Rate %"], krow["Avg Win %"], krow["Avg Loss %"], krow["Kelly Fraction"])
    kelly_cap = account * cons_k

    action, base_pct = "WATCH", 0
    if level in ["Normal pullback", "Good pullback"] and score >= 65:
        action = "BUY / ADD"
        base_pct = 0.18 if s["Ticker"] in ["SMH","VGT","QQQ","QQQM","VOO","SCHD"] else 0.12
    elif level in ["Slightly extended","Near high"] and not has_pos and score >= 55:
        action = "SMALL STARTER ONLY"
        base_pct = 0.08 if s["Ticker"] in ["SMH","VGT","QQQ","QQQM","VOO","SCHD"] else 0.04
    elif level == "High price level":
        action = "DO NOT CHASE"
    elif level == "Weak / below trend":
        action = "WAIT / REDUCE IF HELD"
    elif level == "Deep pullback":
        action = "WAIT FOR REVERSAL"

    if not has_pos and holding_count >= max_holdings and base_pct > 0:
        action = "MAX HOLDINGS REACHED"
        base_pct = 0

    rule_buy = account * base_pct * reg["modifier"]
    pos_room = max(0, account * max_pct(s["Ticker"]) - current_value)
    kelly_room = max(0, kelly_cap - current_value)
    buy = min(rule_buy, cash, pos_room, kelly_room)
    buy_shares = shares_for(buy, s["Price"])
    buy = buy_shares * s["Price"]

    return {
        "Ticker": s["Ticker"], "Price": s["Price"], "Level": level, "Tone": tone, "Action": action,
        "Entry Score": score, "Buy $": buy, "Buy Shares": buy_shares, "Current Value": current_value,
        "Reference Stop": stop, "Risk %": (s["Price"] / stop - 1) * 100 if stop > 0 else np.nan,
        "Win Rate %": krow["Win Rate %"], "Avg Win %": krow["Avg Win %"], "Avg Loss %": krow["Avg Loss %"],
        "Reward/Risk": b, "Raw Kelly %": raw_k * 100, "Kelly Fraction": krow["Kelly Fraction"],
        "Conservative Kelly %": cons_k * 100, "Kelly Cap $": kelly_cap, "Rule Buy $": rule_buy,
        "Position Room $": pos_room, "Kelly Room $": kelly_room, "Reason": reason
    }
