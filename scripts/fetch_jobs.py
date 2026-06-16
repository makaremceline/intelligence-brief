import requests

# AI companies that use Greenhouse ATS
# Add or remove companies by their Greenhouse slug
AI_COMPANIES = [
    "anthropic",
    "openai",
    "databricks",
    "huggingface",
    "cohere",
    "mistral",
    "perplexity",
    "harvey",
    "cognition",
    "aisera",
    "scale",
    "together",
    "anyscale",
]

# Keywords that signal strategic shifts worth flagging
SIGNAL_KEYWORDS = [
    "research", "policy", "strategy", "government", "education",
    "enterprise", "foundation model", "agent", "safety", "alignment",
    "robotics", "hardware", "chip", "infrastructure", "sovereign",
    "regulation", "compliance", "partnership", "academic"
]

def fetch_jobs():
    all_jobs = []

    for company in AI_COMPANIES:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
            response = requests.get(url, timeout=8)

            if response.status_code != 200:
                continue

            jobs = response.json().get("jobs", [])

            for job in jobs[:15]:  # top 15 per company
                title = job.get("title", "")
                department = ""
                departments = job.get("departments", [])
                if departments:
                    department = departments[0].get("name", "")

                location = ""
                offices = job.get("offices", [])
                if offices:
                    location = offices[0].get("name", "")

                # Only include jobs with signal keywords
                title_lower = title.lower()
                dept_lower = department.lower()
                is_signal = any(
                    kw in title_lower or kw in dept_lower
                    for kw in SIGNAL_KEYWORDS
                )

                all_jobs.append({
                    "company": company.title(),
                    "title": title,
                    "department": department,
                    "location": location,
                    "url": job.get("absolute_url", ""),
                    "is_signal": is_signal,
                })

        except Exception as e:
            print(f"Job fetch failed for {company}: {e}")
            continue

    # Sort: signal jobs first
    all_jobs.sort(key=lambda x: x["is_signal"], reverse=True)
    return all_jobs[:20]  # return top 20 total


def summarize_job_signals(jobs):
    """Group jobs by company and return a signal summary string for Claude."""
    if not jobs:
        return "No job listing data available today."

    # Group by company
    by_company = {}
    for job in jobs:
        company = job["company"]
        if company not in by_company:
            by_company[company] = []
        by_company[company].append(job)

    lines = ["Job Listing Signals (what AI companies are hiring for right now):\n"]
    for company, company_jobs in by_company.items():
        signal_jobs = [j for j in company_jobs if j["is_signal"]]
        all_titles = [j["title"] for j in company_jobs[:8]]
        lines.append(f"{company}: {len(company_jobs)} open roles")
        if signal_jobs:
            signal_titles = [j["title"] for j in signal_jobs[:4]]
            lines.append(f"  Strategic signals: {', '.join(signal_titles)}")
        lines.append(f"  All roles include: {', '.join(all_titles[:5])}")
        lines.append("")

    return "\n".join(lines)