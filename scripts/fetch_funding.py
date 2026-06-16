import feedparser

FUNDING_FEEDS = [
    {
        "name": "TechCrunch Startups",
        "url": "https://techcrunch.com/category/startups/feed/"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/"
    },
    {
        "name": "TechCrunch Venture",
        "url": "https://techcrunch.com/tag/venture-capital/feed/"
    },
]

FUNDING_KEYWORDS = [
    "raises", "raised", "funding", "series a", "series b", "series c",
    "seed round", "million", "billion", "investment", "venture", "backed",
    "valuation", "ipo", "acquisition", "acquired", "acquires"
]

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "llm",
    "language model", "generative", "autonomous", "agent", "robotics",
    "foundation model", "compute", "gpu", "data center"
]

def fetch_funding():
    signals = []

    for feed_info in FUNDING_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])

            for entry in feed.entries[:20]:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()
                combined = title + " " + summary

                has_funding = any(kw in combined for kw in FUNDING_KEYWORDS)
                has_ai = any(kw in combined for kw in AI_KEYWORDS)

                if has_funding and has_ai:
                    signals.append({
                        "title": entry.get("title", ""),
                        "source": feed_info["name"],
                        "url": entry.get("link", ""),
                        "summary": entry.get("summary", "")[:300],
                        "published": entry.get("published", ""),
                    })

        except Exception as e:
            print(f"Funding feed failed for {feed_info['name']}: {e}")
            continue

    # Deduplicate by title
    seen = set()
    unique = []
    for s in signals:
        if s["title"] not in seen:
            seen.add(s["title"])
            unique.append(s)

    return unique[:15]


def summarize_funding_signals(signals):
    if not signals:
        return "No AI funding signals today."

    lines = ["VC Funding & Investment Signals (AI & entrepreneurship):\n"]
    for s in signals:
        lines.append(f"  [{s['source']}] {s['title']}")
        if s["summary"]:
            lines.append(f"    → {s['summary'][:150]}")
    return "\n".join(lines)