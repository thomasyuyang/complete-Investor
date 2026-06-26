"""
Investor Principles Module

Adds a daily context-aware investing principle inspired by:
- Benjamin Graham: margin of safety and value discipline
- Philip Fisher: quality growth and long-term business excellence
- Charlie Munger: patience, rationality, and avoiding obvious mistakes

This module uses short principles and paraphrased teaching messages, not long book quotations.
"""

from datetime import date


def daily_investor_principle(market_regime: str, action: str, ticker: str, level: str) -> dict:
    """Choose the most relevant daily investor principle."""
    market_regime = str(market_regime or "").title()
    action = str(action or "").upper()
    ticker = str(ticker or "the selected equity").upper()
    level = str(level or "")

    if "DO NOT CHASE" in action or level in ["Near high", "High price level"]:
        return {
            "source": "Charlie Munger",
            "title": "Avoid the obvious mistake",
            "principle": "The easiest way to improve investment results is to avoid emotional, unnecessary mistakes.",
            "application": (
                f"{ticker} may be a good asset, but today's price level looks extended. "
                "The practical decision is to wait for a better entry instead of chasing."
            ),
            "tone": "yellow",
        }

    if market_regime == "Defensive":
        return {
            "source": "Benjamin Graham",
            "title": "Margin of safety first",
            "principle": "A good investment should leave room for error between price and value.",
            "application": (
                "The current market regime is defensive. Keep position size small, protect cash, "
                "and only buy when the discount is large enough to justify the risk."
            ),
            "tone": "red",
        }

    growth_names = {"MSFT", "NVDA", "GOOGL", "AVGO", "TSM", "VGT", "SMH", "QQQ", "QQQM"}
    if ("BUY" in action or "STARTER" in action) and ticker in growth_names:
        return {
            "source": "Philip Fisher",
            "title": "Quality growth deserves patience",
            "principle": "The best opportunities often come from excellent businesses bought selectively, not from merely cheap stocks.",
            "application": (
                f"{ticker} is being considered because quality, growth potential, and entry timing appear to align. "
                "Use gradual buying and Kelly sizing instead of making one emotional purchase."
            ),
            "tone": "green",
        }

    dividend_names = {"SCHD", "MO", "O", "JNJ", "VYM", "VIG", "BRK-B", "BRK.B"}
    if ("BUY" in action or "STARTER" in action) and ticker in dividend_names:
        return {
            "source": "Benjamin Graham",
            "title": "Income must be supported by safety",
            "principle": "Dividend income is attractive only when earnings, cash flow, and balance sheet strength support it.",
            "application": (
                f"{ticker} may be suitable only if the dividend is sustainable and the valuation is reasonable. "
                "Do not buy a high yield without checking business strength."
            ),
            "tone": "green",
        }

    if "WATCH" in action or "WAIT" in action or "HOLD" in action:
        return {
            "source": "Charlie Munger",
            "title": "Waiting is a decision",
            "principle": "Patience is not inactivity; it is disciplined selectivity.",
            "application": (
                "The app is not forcing a trade today. Holding cash and waiting for a clearer advantage "
                "may be the highest-quality decision."
            ),
            "tone": "blue",
        }

    day = date.today().toordinal() % 3
    defaults = [
        {
            "source": "Benjamin Graham",
            "title": "Price versus value",
            "principle": "Investment discipline begins with separating market price from business value.",
            "application": "Before buying, ask whether the current price gives you enough margin of safety.",
            "tone": "blue",
        },
        {
            "source": "Philip Fisher",
            "title": "Own better businesses",
            "principle": "A truly superior company can compound value for many years.",
            "application": "Focus on a short list of businesses and ETFs you understand and trust.",
            "tone": "blue",
        },
        {
            "source": "Charlie Munger",
            "title": "Rationality wins",
            "principle": "Good investing requires calm judgment, patience, and avoiding unnecessary mistakes.",
            "application": "Let the system protect you from overtrading, chasing, and oversizing.",
            "tone": "blue",
        },
    ]
    return defaults[day]


def render_principle_html(principle: dict) -> str:
    """Returns Streamlit-compatible HTML card."""
    tone = principle.get("tone", "blue")
    return f"""
<div class="card {tone}">
  <div class="title">📖 Today's Investor Principle — {principle.get("source", "")}</div>
  <div class="line">
    <b>{principle.get("title", "")}</b><br>
    <i>{principle.get("principle", "")}</i><br><br>
    <b>Today's application:</b><br>
    {principle.get("application", "")}
  </div>
</div>
"""
