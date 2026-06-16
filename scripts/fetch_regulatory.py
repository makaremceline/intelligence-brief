import feedparser

REGULATORY_FEEDS = [
    {
        "name": "FTC",
        "url": "https://www.ftc.gov/feeds/press-releases.xml"
    },
    {
        "name": "FCC",
        "url": "https://docs.fcc.gov/public/attachments/rss/daily-digest.xml"
    },
]

AI_KEYWORDS = [
    "artificial intelligence", "ai", "machine learning", "algorithm",
    "automated", "data privacy", "surveillance", "deepfake", "chatbot",
    "generative", "technology", "digital", "platform", "big tech",
    "antitrust", "merger", "acquisition", "monopoly", "competition"
]

def fetch_regulatory():
    signals = []

    for feed_info in REGULATORY_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])

            for entry in feed.entries[:15]:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()
                combined = title + " " + summary

                is_relevant = any(kw in combined for kw in AI_KEYWORDS)

                if is_relevant:
                    signals.append({
                        "title": entry.get("title", ""),
                        "source": feed_info["name"],
                        "url": entry.get("link", ""),
                        "summary": entry.get("summary", "")[:300],
                        "published": entry.get("published", ""),
                    })

        except Exception as e:
            print(f"Regulatory feed failed for {feed_info['name']}: {e}")
            continue

    seen = set()
    unique = []
    for s in signals:
        if s["title"] not in seen:
            seen.add(s["title"])
            unique.append(s)

    return unique[:10]


def summarize_regulatory_signals(signals):
    if not signals:
        return "No regulatory signals today."

    lines = ["Regulatory & Policy Signals (FTC / FCC):\n"]
    for s in signals:
        lines.append(f"  [{s['source']}] {s['title']}")
        if s["summary"]:
            lines.append(f"    → {s['summary'][:150]}")
    return "\n".join(lines)