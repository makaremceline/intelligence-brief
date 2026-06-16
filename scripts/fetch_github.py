import requests
from datetime import datetime, timedelta

# Top AI researchers and labs to monitor
GITHUB_ACCOUNTS = [
    "openai", "anthropics", "google-deepmind", "microsoft",
    "meta-llama", "huggingface", "mistralai", "ollama",
    "karpathy", "llm-efficiency-challenge", "EleutherAI",
    "stanford-crfm", "facebookresearch", "deepseek-ai"
]

def fetch_github():
    signals = []
    headers = {"Accept": "application/vnd.github.v3+json"}
    since = (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z"

    for account in GITHUB_ACCOUNTS:
        try:
            # Get recent repos
            url = f"https://api.github.com/users/{account}/repos"
            response = requests.get(
                url,
                headers=headers,
                params={"sort": "updated", "per_page": 5},
                timeout=8
            )

            if response.status_code != 200:
                continue

            repos = response.json()
            if not isinstance(repos, list):
                continue

            for repo in repos:
                updated = repo.get("updated_at", "")
                stars = repo.get("stargazers_count", 0)
                name = repo.get("name", "")
                description = repo.get("description", "") or ""
                is_new = repo.get("created_at", "") >= since

                # Flag if recently updated and notable
                if stars > 100 or is_new:
                    signals.append({
                        "account": account,
                        "repo": name,
                        "description": description[:200],
                        "stars": stars,
                        "updated": updated[:10],
                        "is_new": is_new,
                        "url": repo.get("html_url", ""),
                    })

        except Exception as e:
            print(f"GitHub fetch failed for {account}: {e}")
            continue

    # Sort: new repos first, then by stars
    signals.sort(key=lambda x: (x["is_new"], x["stars"]), reverse=True)
    return signals[:25]


def summarize_github_signals(signals):
    if not signals:
        return "No GitHub activity signals today."

    lines = ["GitHub Activity Signals (what AI labs are building right now):\n"]

    new_repos = [s for s in signals if s["is_new"]]
    if new_repos:
        lines.append("New repositories (just launched):")
        for s in new_repos[:5]:
            lines.append(f"  [{s['account']}] {s['repo']} — {s['description'][:100]}")
            lines.append(f"    {s['url']}")
        lines.append("")

    lines.append("Most active repositories (updated in last 48hrs):")
    for s in signals[:10]:
        star_label = f"★{s['stars']}" if s["stars"] > 0 else ""
        lines.append(f"  [{s['account']}] {s['repo']} {star_label} — {s['description'][:100]}")

    return "\n".join(lines)
    