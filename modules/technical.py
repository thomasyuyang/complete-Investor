import numpy as np
import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - 100/(1+rs)

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"] - df["Close"].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

def indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["EMA20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["EMA50"] = out["Close"].ewm(span=50, adjust=False).mean()
    out["EMA200"] = out["Close"].ewm(span=200, adjust=False).mean()
    out["RSI14"] = rsi(out["Close"])
    out["ATR14"] = atr(out)
    out["ATR_PCT"] = out["ATR14"] / out["Close"] * 100
    out["HIGH_6M"] = out["Close"].rolling(126, min_periods=30).max()
    out["DIST_HIGH"] = (out["Close"] / out["HIGH_6M"] - 1) * 100
    return out

def state_from_history(df: pd.DataFrame, ticker: str, live_price: float | None = None) -> dict:
    out = indicators(df)
    l = out.iloc[-1]
    px = float(live_price) if live_price and live_price > 0 else float(l["Close"])
    dist_high = (px / float(l["HIGH_6M"]) - 1) * 100 if float(l["HIGH_6M"]) > 0 else float(l["DIST_HIGH"])
    return {
        "Ticker": ticker,
        "Price": px,
        "EMA20": float(l["EMA20"]),
        "EMA50": float(l["EMA50"]),
        "EMA200": float(l["EMA200"]),
        "RSI": float(l["RSI14"]),
        "ATR": float(l["ATR14"]),
        "ATR_PCT": float(l["ATR_PCT"]),
        "DIST_HIGH": float(dist_high),
    }, out
