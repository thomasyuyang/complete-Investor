from datetime import date
import pandas as pd
import streamlit as st

from modules.storage import (
    load_positions, save_positions, clean_positions,
    load_kelly, save_kelly, clean_kelly,
    load_watchlist, save_watchlist,
    load_journal, append_journal
)
from modules.screener import market_regime, screen_tickers
from modules.portfolio import money, price
from modules.charts import price_chart

st.set_page_config(page_title="Thomas AI Complete Investor V7", page_icon="📈", layout="wide")

st.markdown("""
<style>
.card{background:white;border:1px solid #e5edf5;border-radius:18px;padding:16px 18px;box-shadow:0 2px 12px rgba(0,0,0,0.05);margin:10px 0 16px 0;}
.green{background:#eaf7ef;border-left:7px solid #29a35a}.yellow{background:#fff8e6;border-left:7px solid #d6a300}
.red{background:#fdecec;border-left:7px solid #d94848}.blue{background:#edf2ff;border-left:7px solid #4b6fff}
.title{font-size:1.25rem;font-weight:800;margin-bottom:8px}.line{font-size:1.02rem;line-height:1.55}
.small{font-size:0.88rem;color:#666}
</style>
""", unsafe_allow_html=True)

st.title("📈 Thomas AI Complete Investor V7 — Phase 1")
st.caption("Modular Kelly Entry Screener with live quote refresh, persistent records, market regime, and trade journal.")

with st.sidebar:
    st.header("Account")
    account = st.number_input("Total short-term account value ($)", min_value=1000.0, value=10000.0, step=500.0)
    cash = st.number_input("Current cash available ($)", min_value=0.0, value=10000.0, step=100.0)
    max_holdings = st.slider("Maximum holdings allowed", 1, 8, 3)
    min_cash_pct = st.slider("Minimum cash reserve %", 0, 50, 20) / 100
    period = st.selectbox("Chart period", ["3mo", "6mo", "1y"], index=2)
    if st.button("Refresh market data / live quotes"):
        st.cache_data.clear()
        st.rerun()

if "positions_df" not in st.session_state:
    st.session_state.positions_df = load_positions()
if "kelly_df" not in st.session_state:
    st.session_state.kelly_df = load_kelly()
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Positions & Kelly", "Watchlist", "Trade Journal"])

with tab2:
    st.markdown('<div class="card blue"><div class="title">Persistent Positions Manager</div><div class="line">Changes are saved to data/positions.csv.</div></div>', unsafe_allow_html=True)
    positions_edit = st.data_editor(st.session_state.positions_df, num_rows="dynamic", use_container_width=True, key="positions_editor")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save positions"):
            st.session_state.positions_df = clean_positions(positions_edit)
            save_positions(st.session_state.positions_df)
            st.success("Positions saved.")
    with c2:
        st.download_button("Download positions CSV", clean_positions(positions_edit).to_csv(index=False), "positions.csv", "text/csv")

    st.markdown('<div class="card blue"><div class="title">Persistent Kelly Inputs</div><div class="line">Formula: f* = (b × p - q) / b. Use conservative fraction such as 0.25.</div></div>', unsafe_allow_html=True)
    kelly_edit = st.data_editor(st.session_state.kelly_df, num_rows="dynamic", use_container_width=True, key="kelly_editor")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save Kelly inputs"):
            st.session_state.kelly_df = clean_kelly(kelly_edit)
            save_kelly(st.session_state.kelly_df)
            st.success("Kelly inputs saved.")
    with c2:
        st.download_button("Download Kelly CSV", clean_kelly(kelly_edit).to_csv(index=False), "kelly.csv", "text/csv")

with tab3:
    st.markdown('<div class="card blue"><div class="title">Watchlist Manager</div><div class="line">Keep ETFs and a small number of trusted companies here.</div></div>', unsafe_allow_html=True)
    current_text = ",".join(st.session_state.watchlist)
    watch_text = st.text_area("Tickers to screen", current_text, height=130)
    if st.button("Save watchlist"):
        tickers = [x.strip().upper() for x in watch_text.replace(";", ",").split(",") if x.strip()]
        st.session_state.watchlist = tickers
        save_watchlist(tickers)
        st.success("Watchlist saved.")
    st.download_button("Download watchlist CSV", pd.DataFrame({"Ticker": st.session_state.watchlist}).to_csv(index=False), "watchlist.csv", "text/csv")

with tab1:
    positions = clean_positions(st.session_state.positions_df)
    kelly_df = clean_kelly(st.session_state.kelly_df)

    active = positions[positions["Shares"] > 0]
    pos_map = {r["Ticker"]: {"shares": int(r["Shares"]), "avg_cost": float(r["Avg Cost"])} for _, r in active.iterrows()}
    holding_count = len(pos_map)
    kelly_map = {r["Ticker"]: r for _, r in kelly_df.iterrows()}

    reg = market_regime()
    st.markdown(
        f'<div class="card {reg["css"]}"><div class="title">Market Regime: {reg["name"]} ({reg["score"]}/12)</div>'
        f'<div class="line">Buy size modifier: {reg["modifier"]:.0%}</div></div>',
        unsafe_allow_html=True
    )
    with st.expander("Market regime quote details"):
        df_reg = pd.DataFrame(reg["rows"])
        if "Price" in df_reg.columns:
            df_reg["Price"] = df_reg["Price"].map(lambda x: price(x) if pd.notna(x) else "N/A")
        st.dataframe(df_reg, use_container_width=True, hide_index=True)

    all_tickers = sorted(set(st.session_state.watchlist) | set(pos_map.keys()))
    results, details = screen_tickers(all_tickers, pos_map, account, cash, reg, max_holdings, holding_count, kelly_map, period)

    if results:
        dfres = pd.DataFrame(results)
        if cash - account * min_cash_pct <= 0:
            dfres["Buy $"] = 0
            dfres["Buy Shares"] = 0
            dfres["Action"] = "CASH RESERVE LIMIT"

        valid = dfres[dfres["Buy Shares"].fillna(0) > 0] if "Buy Shares" in dfres.columns else pd.DataFrame()
        if not valid.empty:
            top = valid[~valid["Action"].astype(str).str.contains("MAX|RESERVE|CHASE|WAIT", regex=True, na=False)].sort_values("Entry Score", ascending=False)
        else:
            top = pd.DataFrame()

        if not top.empty:
            tb = top.iloc[0]
            css = {"green":"green", "yellow":"yellow", "red":"red", "blue":"blue"}.get(tb.get("Tone", "blue"), "blue")
            st.markdown(
                f'<div class="card {css}"><div class="title">Best Entry Candidate: {tb["Ticker"]}</div>'
                f'<div class="line">Action: {tb["Action"]}<br>'
                f'Buy: {money(tb["Buy $"])} / {int(tb["Buy Shares"])} shares<br>'
                f'Current Price: {price(tb["Price"])}<br>'
                f'Conservative Kelly: {tb["Conservative Kelly %"]:.1f}% | Kelly Cap: {money(tb["Kelly Cap $"])}<br>'
                f'Reference Stop: {price(tb["Reference Stop"])}<br>'
                f'<span class="small">Quote: {tb.get("Quote Source","")} | {tb.get("Quote Time","")}</span></div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div class="card yellow"><div class="title">No strong new buy today</div><div class="line">Hold cash, review current positions, and avoid chasing extended prices.</div></div>', unsafe_allow_html=True)

        disp = dfres.copy()
        for c in ["Price", "Reference Stop"]:
            if c in disp.columns:
                disp[c] = disp[c].map(lambda x: price(x) if pd.notna(x) else "N/A")
        for c in ["Buy $", "Current Value", "Kelly Cap $", "Rule Buy $", "Position Room $", "Kelly Room $"]:
            if c in disp.columns:
                disp[c] = disp[c].map(lambda x: money(x) if pd.notna(x) else "$0")
        for c in ["Risk %", "Raw Kelly %", "Conservative Kelly %"]:
            if c in disp.columns:
                disp[c] = disp[c].map(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")

        st.subheader("Candidate Ranking with Kelly and Live Quote Source")
        cols = [c for c in ["Ticker","Level","Action","Entry Score","Price","Buy $","Buy Shares","Current Value","Reference Stop","Risk %","Raw Kelly %","Conservative Kelly %","Kelly Cap $","Quote Source","Quote Time","Reason"] if c in disp.columns]
        st.dataframe(disp.sort_values("Entry Score", ascending=False)[cols], hide_index=True, use_container_width=True)

        selected = st.selectbox("View Kelly Formula Breakdown and Chart", all_tickers)
        if selected in details:
            ind_df, s, res = details[selected]
            st.markdown(f"## {selected} Kelly Formula Breakdown")
            st.markdown(f"""
**Formula:** `f* = (b × p - q) / b`

`p = win rate = {res['Win Rate %']:.1f}%`  
`q = 1 - p = {100-res['Win Rate %']:.1f}%`  
`b = Avg Win / Avg Loss = {res['Avg Win %']:.1f}% / {res['Avg Loss %']:.1f}% = {res['Reward/Risk']:.2f}`  

**Raw Kelly:** `{res['Raw Kelly %']:.1f}%`  
**Kelly Fraction:** `{res['Kelly Fraction']:.2f}`  
**Conservative Kelly:** `{res['Conservative Kelly %']:.1f}%`  
**Kelly Capital Cap:** `{money(res['Kelly Cap $'])}`  

Final buy amount is the minimum of:

1. Rule-based buy amount: `{money(res['Rule Buy $'])}`
2. Cash available: `{money(cash)}`
3. Max position room: `{money(res['Position Room $'])}`
4. Kelly room after current position: `{money(res['Kelly Room $'])}`
5. Cash reserve rule

**Final recommended buy:** `{money(res['Buy $'])}` / `{res['Buy Shares']}` shares.

**Live quote source:** `{res.get('Quote Source','')}`  
**Quote time:** `{res.get('Quote Time','')}`
""")
            st.plotly_chart(price_chart(ind_df.tail(130), selected), use_container_width=True)

with tab4:
    st.markdown('<div class="card blue"><div class="title">Trade Journal</div><div class="line">Record why you bought or sold. This builds discipline and learning.</div></div>', unsafe_allow_html=True)
    with st.form("journal_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            j_date = st.date_input("Date", date.today())
        with c2:
            j_ticker = st.text_input("Ticker", "NVDA").upper()
        with c3:
            j_action = st.selectbox("Action", ["BUY", "ADD", "TRIM", "SELL", "WATCH", "REVIEW"])
        with c4:
            j_shares = st.number_input("Shares", min_value=0.0, value=0.0, step=1.0)
        j_price = st.number_input("Price", min_value=0.0, value=0.0, step=0.01)
        j_reason = st.text_area("Reason")
        j_lesson = st.text_area("Lesson")
        submitted = st.form_submit_button("Save journal entry")
        if submitted:
            append_journal({
                "Date": str(j_date),
                "Ticker": j_ticker,
                "Action": j_action,
                "Shares": j_shares,
                "Price": j_price,
                "Reason": j_reason,
                "Lesson": j_lesson
            })
            st.success("Journal entry saved.")

    journal = load_journal()
    st.dataframe(journal.tail(100).iloc[::-1], use_container_width=True, hide_index=True)
    st.download_button("Download trade journal CSV", journal.to_csv(index=False), "trade_journal.csv", "text/csv")

st.caption("Educational decision support only. Current prices are best-effort from yfinance and may be delayed or unavailable. Confirm bid/ask with your broker before trading.")
