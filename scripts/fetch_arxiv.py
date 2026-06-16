import feedparser
from datetime import datetime, timedelta
from collections import defaultdict

AI_CATEGORIES = [
    "cs.AI",   # Artificial Intelligence
    "cs.LG",   # Machine Learning
    "cs.CL",   # Computation and Language
    "cs.CV",   # Computer Vision
    "cs.NE",   # Neural and Evolutionary Computing
]

def fetch_arxiv():
    papers = []
    keyword_counts = defaultdict(int)

    for category in AI_CATEGORIES:
        try:
            url = f"https://rss.arxiv.org/rss/{category}"
            feed = feedparser.parse(url)

            for entry in feed.entries[:20]:
                title = entry.get("title", "").replace("\n", " ").strip()
                summary = entry.get("summary", "")[:300].replace("\n", " ").strip()
                published = entry.get("published", "")
                link = entry.get("link", "")
                authors = entry.get("author", "")

                # Extract keywords from title for velocity tracking
                title_lower = title.lower()
                for kw in ["agent", "reasoning", "multimodal", "alignment", "rlhf",
                           "fine-tuning", "retrieval", "benchmark", "safety",
                           "autonomous", "diffusion", "transformer", "scaling"]:
                    if kw in title_lower:
                        keyword_counts[kw] += 1

                papers.append({
                    "title": title,
                    "summary": summary,
                    "category": category,
                    "published": published,
                    "url": link,
                    "authors": authors,
                })

        except Exception as e:
            print(f"arXiv fetch failed for {category}: {e}")
            continue

    # Find velocity signals — topics with 3+ papers today
    velocity_signals = {kw: count for kw, count in keyword_counts.items() if count >= 3}

    return {
        "papers": papers[:30],
        "velocity": velocity_signals,
        "total": len(papers)
    }


def summarize_arxiv_signals(arxiv_data):
    if not arxiv_data or not arxiv_data.get("papers"):
        return "No arXiv preprint data available today."

    papers = arxiv_data["papers"]
    velocity = arxiv_data["velocity"]
    total = arxiv_data["total"]

    lines = [f"Academic Preprint Intelligence ({total} papers scanned across {len(AI_CATEGORIES)} AI categories):\n"]

    if velocity:
        lines.append("Velocity signals (topics with 3+ independent papers today — field is converging):")
        for kw, count in sorted(velocity.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  '{kw}': {count} papers — researchers are converging on this topic")
        lines.append("")

    lines.append("Notable papers today:")
    for p in papers[:8]:
        lines.append(f"  [{p['category']}] {p['title']}")
        if p["summary"]:
            lines.append(f"    → {p['summary'][:120]}")

    return "\n".join(lines)