import yfinance as yf
from datetime import datetime, timedelta

# AI & entrepreneurship relevant tickers
# Grouped by category for context
TICKERS = {
    "AI Infrastructure": ["NVDA", "AMD", "INTC", "AVGO"],
    "AI Platforms": ["MSFT", "GOOGL", "META", "AMZN"],
    "AI Pure Plays": ["PLTR", "AI", "SOUN", "BBAI"],
    "Venture & Finance": ["COIN", "HOOD"],
}

MOVE_THRESHOLD = 3.0  # flag moves above 3%

def fetch_stocks():
    signals = []

    for category, tickers in TICKERS.items():
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")

                if len(hist) < 2:
                    continue

                prev_close = hist["Close"].iloc[-2]
                curr_close = hist["Close"].iloc[-1]
                pct_change = ((curr_close - prev_close) / prev_close) * 100

                signals.append({
                    "ticker": ticker,
                    "category": category,
                    "price": round(curr_close, 2),
                    "change_pct": round(pct_change, 2),
                    "is_signal": abs(pct_change) >= MOVE_THRESHOLD,
                    "direction": "up" if pct_change > 0 else "down",
                })

            except Exception as e:
                print(f"Stock fetch failed for {ticker}: {e}")
                continue

    # Sort: biggest movers first
    signals.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
    return signals


def summarize_stock_signals(signals):
    if not signals:
        return "No stock data available today."

    lines = ["Stock Market Signals (AI & entrepreneurship relevant tickers):\n"]

    big_movers = [s for s in signals if s["is_signal"]]
    if big_movers:
        lines.append("Significant moves (3%+):")
        for s in big_movers:
            arrow = "↑" if s["direction"] == "up" else "↓"
            lines.append(f"  {s['ticker']} ({s['category']}): {arrow}{abs(s['change_pct'])}% — ${s['price']}")
        lines.append("")

    lines.append("Full snapshot:")
    for s in signals:
        arrow = "↑" if s["direction"] == "up" else "↓"
        lines.append(f"  {s['ticker']}: {arrow}{abs(s['change_pct'])}% (${s['price']})")

    return "\n".join(lines)