# Investor Principles Patch Guide

This patch adds a new daily section to your Streamlit app:

## Today's Investor Principle

It selects a Graham, Fisher, or Munger style principle based on:

- Market regime: Bullish / Neutral / Defensive
- Best recommendation action: BUY / ADD / WATCH / DO NOT CHASE
- Selected ticker
- Price level: Near high / Good pullback / Weak trend

---

## File included

```text
modules/investor_principles.py
```

Copy this file into your GitHub repository inside the existing `modules` folder.

---

## Step 1: Add the import to app.py

Open `app.py`.

Add this line near the other imports:

```python
from modules.investor_principles import daily_investor_principle, render_principle_html
```

---

## Step 2: Add the principle card after Best Entry Candidate

In `app.py`, find the section inside `with tab1:` where the app shows:

```python
Best Entry Candidate
```

Immediately after the `st.markdown(...)` that displays the best candidate card, add this:

```python
principle = daily_investor_principle(
    market_regime=reg["name"],
    action=tb["Action"],
    ticker=tb["Ticker"],
    level=tb["Level"],
)
st.markdown(render_principle_html(principle), unsafe_allow_html=True)
```

---

## Step 3: Optional principle for “No strong buy today”

If you also want to show a Munger-style patience reminder when there is no buy candidate, replace your `else` block with this:

```python
else:
    st.markdown('<div class="card yellow"><div class="title">No strong new buy today</div><div class="line">Hold cash, review current positions, and avoid chasing extended prices.</div></div>', unsafe_allow_html=True)

    principle = daily_investor_principle(
        market_regime=reg["name"],
        action="WATCH",
        ticker="CASH",
        level="No strong buy",
    )
    st.markdown(render_principle_html(principle), unsafe_allow_html=True)
```

---

## No change needed to requirements.txt

This patch does not require new packages.
