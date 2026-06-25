# Thomas AI Complete Investor V7 — Phase 1

Phase 1 implements a clean modular Streamlit app based on the prior Kelly entry screener.

## Included Phase 1 features

- Modular architecture
- Real-time quote engine using `yfinance.fast_info` with fallback to 1-minute price
- Persistent CSV portfolio records
- Persistent Kelly assumptions
- Persistent trade journal
- Market regime dashboard
- Technical indicators: EMA20/50/200, RSI, ATR%, 6-month high distance
- Kelly formula breakdown
- Position sizing with cash reserve, maximum holdings, and max-position caps
- Entry ranking and chart view
- Trade journal entry form
- Manual CSV backup/download

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub / Streamlit Cloud

Upload all files to a new GitHub repository. In Streamlit Cloud, set the main file path to:

```text
app.py
```

## Educational use only

This app is for investment decision support and learning. It is not financial advice. Real-time quotes are best-effort from Yahoo Finance/yfinance and should be verified with your broker before trading.
