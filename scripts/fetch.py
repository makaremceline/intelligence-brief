import feedparser
import requests
import json
import re
from datetime import datetime, timezone

SOURCES = {
    "a16z": "https://a16z.com/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",
    "MIT Tech Review": "https://www.technologyreview.com/feed/",
    "Hacker News": "https://hnrss.org/frontpage",
}

X_ACCOUNTS = [
    "sama", "pmarca", "garrytan", "paulg", "jvisserlabs",
    "benedictevans", "karpathy", "ylecun", "emollick",
    "naval", "jason", "levelsio", "OpenAI", "AnthropicAI",
    "GoogleDeepMind", "mmitchell_ai"
]

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "llm", "gpt",
    "startup", "entrepreneur", "venture", "funding", "ycombinator",
    "openai", "anthropic", "deepmind", "agent", "model", "foundation model"
]

POLYMARKET_AI_KEYWORDS = [
    "ai", "artificial intelligence", "openai", "anthropic", "google",
    "meta", "microsoft", "startup", "tech", "gpt", "llm",
    "regulation", "agi", "robot", "automation", "nvidia", "spacex",
    "entrepreneur", "venture", "ipo", "acquisition", "elon", "musk",
    "apple", "amazon", "tesla", "crypto", "bitcoin", "sam altman",
    "chatgpt", "gemini", "claude", "deepmind", "silicon valley",
    "interest rate", "fed", "economy", "recession", "market"
]

def is_duplicate(title, seen_titles, threshold=0.6):
    title_words = set(title.lower().split())
    for seen in seen_titles:
        seen_words = set(seen.lower().split())
        if not title_words or not seen_words:
            continue
        overlap = len(title_words & seen_words) / max(len(title_words), len(seen_words))
        if overlap > threshold:
            return True
    return False

def fetch_articles():
    articles = []
    seen_titles = []
    for source_name, url in SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:6]:
            title = entry.get("title", "")
            if not title:
                continue
            if is_duplicate(title, seen_titles):
                continue
            seen_titles.append(title)
            articles.append({
                "source": source_name,
                "title": title,
                "summary": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "date": entry.get("published", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            })
    return articles

def fetch_x_posts():
    posts = []
    seen_titles = []
    for account in X_ACCOUNTS:
        try:
            url = f"https://nitter.privacydev.net/{account}/rss"
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                title = entry.get("title", "")
                if not title or len(title) < 20:
                    continue
                title_lower = title.lower()
                if not any(kw in title_lower for kw in AI_KEYWORDS):
                    continue
                if is_duplicate(title, seen_titles):
                    continue
                seen_titles.append(title)
                posts.append({
                    "source": f"@{account} on X",
                    "title": title[:200],
                    "summary": "",
                    "link": entry.get("link", f"https://x.com/{account}"),
                    "date": entry.get("published", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                })
        except:
            continue
    return posts

def fetch_polymarket():
    try:
        url = "https://gamma-api.polymarket.com/markets?closed=false&limit=100&order=volume&ascending=false"
        response = requests.get(url, timeout=10)
        markets = response.json()
        relevant = []
        for market in markets:
            try:
                question = market.get("question", "")
                question_lower = question.lower()
                if not any(re.search(r'\b' + re.escape(kw) + r'\b', question_lower) for kw in POLYMARKET_AI_KEYWORDS):
                    continue
                if market.get("closed") or market.get("resolved"):
                    continue
                outcomes = market.get("outcomePrices", "")
                if not outcomes:
                    continue
                if isinstance(outcomes, str):
                    prices = json.loads(outcomes)
                else:
                    prices = outcomes
                prices = [float(p) for p in prices]
                if not prices:
                    continue
                best_price = round(max(prices) * 100, 1)
                if best_price > 95 or best_price < 5:
                    continue
                volume = float(market.get("volume", 0))
                relevant.append({
                    "question": question,
                    "odds": best_price,
                    "volume": volume,
                    "url": f"https://polymarket.com/event/{market.get('slug', '')}",
                })
            except:
                continue
        relevant.sort(key=lambda x: x["volume"], reverse=True)
        return relevant[:3]
    except Exception as e:
        print(f"Polymarket fetch failed: {e}")
        return []

def fetch_all():
    print("Fetching RSS articles...")
    articles = fetch_articles()
    print("Fetching X posts...")
    x_posts = fetch_x_posts()
    articles += x_posts
    print("Fetching Polymarket signals...")
    polymarket = fetch_polymarket()
    return articles, polymarket