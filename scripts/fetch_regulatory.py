import feedparser
import datetime

REGULATORY_FEEDS = [
    # FTC — press releases (primary source)
    "https://www.ftc.gov/feeds/press-release.xml",
    # FTC — news and events
    "https://www.ftc.gov/feeds/news.xml",
    # FCC — news releases
    "https://docs.fcc.gov/public/attachments/rss/dailydigest.xml",
    # FCC — proceedings
    "https://www.fcc.gov/rss/news-releases.xml",
    # NIST AI — standards and guidelines
    "https://www.nist.gov/blogs/cybersecurity-insights/rss.xml",
    # White House briefings — AI executive orders
    "https://www.whitehouse.gov/feed/",
    # Congress.gov — AI bills
    "https://www.congress.gov/rss/most-viewed-bills.xml",
    # EU AI Act tracker via Politico
    "https://rss.politico.com/tech.xml",
]

AI_REGULATORY_KEYWORDS = [
    "artificial intelligence", "AI", "machine learning", "algorithm",
    "large language model", "LLM", "OpenAI", "Anthropic", "Google AI",
    "tech regulation", "data privacy", "antitrust tech", "AI safety",
    "generative AI", "chatbot", "foundation model", "AI governance",
    "AI policy", "AI regulation", "AI executive order", "AI legislation",
    "Section 230", "digital markets", "platform regulation"
]

def fetch_regulatory():
    signals = []
    cutoff = datetime.datetime.now() - datetime.timedelta(days=7)

    for feed_url in REGULATORY_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                continue
            for entry in feed.entries[:20]:
                title = entry.get("title", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                link = entry.get("link", "")
                text = (title + " " + summary).lower()

                # Filter to AI/tech relevant only
                if not any(kw.lower() in text for kw in AI_REGULATORY_KEYWORDS):
                    continue

                # Parse date
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    try:
                        pub_dt = datetime.datetime(*pub[:6])
                        if pub_dt < cutoff:
                            continue
                    except:
                        pass

                signals.append({
                    "title": title,
                    "summary": summary[:300],
                    "link": link,
                    "source": feed.feed.get("title", feed_url),
                    "date": entry.get("published", "")[:10] if entry.get("published") else ""
                })
        except Exception as e:
            print(f"Regulatory feed error ({feed_url}): {e}")
            continue

    # Deduplicate by title
    seen = set()
    unique = []
    for s in signals:
        if s["title"] not in seen:
            seen.add(s["title"])
            unique.append(s)

    print(f"Fetched {len(unique)} regulatory signals.")
    return unique


def summarize_regulatory_signals(signals):
    if not signals:
        return "\nNo AI-relevant regulatory signals this week.\n"
    text = "\nRegulatory & Policy Intelligence (AI-relevant):\n"
    for s in signals[:8]:
        text += f"- [{s['source']}] {s['title']}"
        if s.get("summary"):
            text += f": {s['summary'][:150]}"
        if s.get("link"):
            text += f" | {s['link']}"
        text += "\n"
    return text
