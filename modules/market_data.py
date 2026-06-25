from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

@st.cache_data(ttl=20)
def live_quote(ticker: str) -> dict:
    ticker = ticker.upper().strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        tk = yf.Ticker(ticker)
        fi = getattr(tk, "fast_info", {}) or {}
        last = fi.get("last_price", None)
        prev = fi.get("previous_close", None)
        if last and last > 0:
            return {"price": float(last), "source": "fast_info last_price", "time": now, "previous_close": float(prev) if prev else None}
    except Exception:
        pass

    try:
        df = yf.download(ticker, period="1d", interval="1m", auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        if not df.empty:
            return {"price": float(df["Close"].iloc[-1]), "source": "1-minute latest close", "time": str(df.index[-1]), "previous_close": None}
    except Exception:
        pass

    try:
        df = yf.download(ticker, period="5d", interval="1d", auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        if not df.empty:
            return {"price": float(df["Close"].iloc[-1]), "source": "daily close fallback", "time": str(df.index[-1]), "previous_close": None}
    except Exception:
        pass

    return {"price": np.nan, "source": "unavailable", "time": now, "previous_close": None}

@st.cache_data(ttl=300)
def load_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()
