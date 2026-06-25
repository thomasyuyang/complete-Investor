from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

POSITIONS_PATH = DATA_DIR / "positions.csv"
KELLY_PATH = DATA_DIR / "kelly.csv"
WATCHLIST_PATH = DATA_DIR / "watchlist.csv"
JOURNAL_PATH = DATA_DIR / "trade_journal.csv"

DEFAULT_POSITIONS = pd.DataFrame([
    {"Ticker":"SMH","Shares":0,"Avg Cost":0.0},
    {"Ticker":"NVDA","Shares":0,"Avg Cost":0.0},
    {"Ticker":"MSFT","Shares":0,"Avg Cost":0.0},
])

DEFAULT_KELLY = pd.DataFrame([
    {"Ticker":"SMH","Win Rate %":58,"Avg Win %":12,"Avg Loss %":7,"Kelly Fraction":0.25},
    {"Ticker":"NVDA","Win Rate %":55,"Avg Win %":15,"Avg Loss %":8,"Kelly Fraction":0.25},
    {"Ticker":"MSFT","Win Rate %":57,"Avg Win %":10,"Avg Loss %":6,"Kelly Fraction":0.25},
    {"Ticker":"GOOGL","Win Rate %":56,"Avg Win %":11,"Avg Loss %":7,"Kelly Fraction":0.25},
    {"Ticker":"MO","Win Rate %":54,"Avg Win %":7,"Avg Loss %":5,"Kelly Fraction":0.25},
    {"Ticker":"VGT","Win Rate %":58,"Avg Win %":11,"Avg Loss %":6.5,"Kelly Fraction":0.25},
    {"Ticker":"QQQ","Win Rate %":57,"Avg Win %":10,"Avg Loss %":6,"Kelly Fraction":0.25},
    {"Ticker":"VOO","Win Rate %":57,"Avg Win %":8,"Avg Loss %":5,"Kelly Fraction":0.25},
    {"Ticker":"SCHD","Win Rate %":55,"Avg Win %":6,"Avg Loss %":4,"Kelly Fraction":0.25},
    {"Ticker":"TSM","Win Rate %":56,"Avg Win %":13,"Avg Loss %":8,"Kelly Fraction":0.25},
    {"Ticker":"AVGO","Win Rate %":56,"Avg Win %":14,"Avg Loss %":8,"Kelly Fraction":0.25},
])

def clean_positions(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["Ticker","Shares","Avg Cost"]:
        if c not in df.columns:
            df[c] = "" if c == "Ticker" else 0
    out = df[["Ticker","Shares","Avg Cost"]].copy()
    out["Ticker"] = out["Ticker"].astype(str).str.upper().str.strip()
    out["Shares"] = pd.to_numeric(out["Shares"], errors="coerce").fillna(0).astype(int)
    out["Avg Cost"] = pd.to_numeric(out["Avg Cost"], errors="coerce").fillna(0.0)
    return out[out["Ticker"]!=""].drop_duplicates("Ticker", keep="last").reset_index(drop=True)

def clean_kelly(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["Ticker","Win Rate %","Avg Win %","Avg Loss %","Kelly Fraction"]:
        if c not in df.columns:
            df[c] = 0
    out = df[["Ticker","Win Rate %","Avg Win %","Avg Loss %","Kelly Fraction"]].copy()
    out["Ticker"] = out["Ticker"].astype(str).str.upper().str.strip()
    for c in ["Win Rate %","Avg Win %","Avg Loss %","Kelly Fraction"]:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)
    return out[out["Ticker"]!=""].drop_duplicates("Ticker", keep="last").reset_index(drop=True)

def load_positions() -> pd.DataFrame:
    if POSITIONS_PATH.exists():
        return clean_positions(pd.read_csv(POSITIONS_PATH))
    save_positions(DEFAULT_POSITIONS)
    return DEFAULT_POSITIONS.copy()

def save_positions(df: pd.DataFrame) -> None:
    clean_positions(df).to_csv(POSITIONS_PATH, index=False)

def load_kelly() -> pd.DataFrame:
    if KELLY_PATH.exists():
        return clean_kelly(pd.read_csv(KELLY_PATH))
    save_kelly(DEFAULT_KELLY)
    return DEFAULT_KELLY.copy()

def save_kelly(df: pd.DataFrame) -> None:
    clean_kelly(df).to_csv(KELLY_PATH, index=False)

def load_watchlist() -> list[str]:
    if WATCHLIST_PATH.exists():
        df = pd.read_csv(WATCHLIST_PATH)
        if "Ticker" in df.columns:
            return [x for x in df["Ticker"].astype(str).str.upper().str.strip().tolist() if x]
    return ["SMH","NVDA","MSFT","GOOGL","MO","VGT","QQQ"]

def save_watchlist(tickers: list[str]) -> None:
    pd.DataFrame({"Ticker": sorted(set([t.upper().strip() for t in tickers if t.strip()]))}).to_csv(WATCHLIST_PATH, index=False)

def load_journal() -> pd.DataFrame:
    cols = ["Date","Ticker","Action","Shares","Price","Reason","Lesson"]
    if JOURNAL_PATH.exists():
        df = pd.read_csv(JOURNAL_PATH)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    pd.DataFrame(columns=cols).to_csv(JOURNAL_PATH, index=False)
    return pd.DataFrame(columns=cols)

def append_journal(row: dict) -> None:
    df = load_journal()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(JOURNAL_PATH, index=False)
