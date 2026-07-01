import os
import requests
from datetime import datetime, timedelta

# ── CURATED PODCAST LIST ──
# These are the podcasts that matter for AI and entrepreneurship.
# Listen Notes searches these by show name to find new episodes.
CURATED_SHOWS = [
    "20VC with Harry Stebbings",
    "Lex Fridman Podcast",
    "Dwarkesh Podcast",
    "Acquired",
    "BG2 Pod",
    "No Priors: Artificial Intelligence",
    "Latent Space",
    "The AI Daily Brief",
    "Eye on AI",
    "The Knowledge Project",
]

# ── PERMANENT KEYWORDS ──
# These always get searched regardless of the day's brief.
PERMANENT_KEYWORDS = [
    "Anthropic", "OpenAI", "Sam Altman", "Dario Amodei",
    "AI entrepreneurship", "AI startup", "AI regulation",
    "large language model", "AI investment", "AI venture capital"
]


def get_dynamic_keywords(brief_data):
    """Pull key themes and company names from today's brief to use as dynamic search terms."""
    keywords = []
    report = brief_data.get("report", {}) if brief_data else {}

    # Pull from key developments themes
    for dev in report.get("key_developments", [])[:4]:
        theme = dev.get("theme", "")
        if theme and len(theme) > 3:
            keywords.append(theme)

    # Pull from big picture (first 5 words of each sentence)
    big_picture = report.get("big_picture", "")
    if big_picture:
        words = big_picture.split()[:8]
        keywords.append(" ".join(words[:4]))

    return keywords[:5]  # Cap at 5 dynamic keywords


def search_listen_notes(query, api_key, published_after=None):
    """Search Listen Notes for recent podcast episodes matching a query."""
    if not api_key:
        return []
    try:
        params = {
            "q": query,
            "type": "episode",
            "only_in": "title,description",
            "language": "English",
            "len_min": 10,  # at least 10 minutes
            "safe_mode": 0,
        }
        if published_after:
            params["published_after"] = int(published_after.timestamp() * 1000)

        r = requests.get(
            "https://listen-api.listennotes.com/api/v2/search",
            headers={"X-ListenAPI-Key": api_key},
            params=params,
            timeout=10
        )
        if r.status_code != 200:
            return []
        data = r.json()
        return data.get("results", [])
    except Exception as e:
        print(f"Listen Notes search error: {e}")
        return []


def get_transcript_spoken(episode_title, podcast_name, episode_url):
    """
    Get transcript from Spoken.md API.
    $0.10 per transcript, credits never expire.
    Requires SPOKEN_API_KEY in .env
    """
    api_key = os.getenv("SPOKEN_API_KEY")
    if not api_key:
        print("No SPOKEN_API_KEY set — skipping transcript fetch.")
        return None
    try:
        r = requests.post(
            "https://api.spoken.md/v1/transcript",
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json"
            },
            json={"url": episode_url},
            timeout=30
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("transcript") or data.get("text")
        else:
            print(f"Spoken.md error {r.status_code} for {episode_title}")
            return None
    except Exception as e:
        print(f"Spoken.md exception: {e}")
        return None


def fetch_podcasts(brief_data=None, max_transcripts=3):
    """
    Main function called from run.py.
    Searches for new AI/entrepreneurship podcast episodes from the last 24 hours.
    Returns a list of dicts with episode metadata and transcript snippets.
    """
    listen_notes_key = os.getenv("LISTEN_NOTES_API_KEY")
    if not listen_notes_key:
        print("No LISTEN_NOTES_API_KEY set — skipping podcast fetch.")
        return []

    since = datetime.now() - timedelta(hours=48)  # 48h window to avoid missing episodes
    all_episodes = []
    seen_ids = set()

    # Search permanent keywords
    for kw in PERMANENT_KEYWORDS[:5]:  # Limit API calls
        results = search_listen_notes(kw, listen_notes_key, published_after=since)
        for ep in results:
            ep_id = ep.get("id", "")
            if ep_id and ep_id not in seen_ids:
                seen_ids.add(ep_id)
                all_episodes.append(ep)

    # Search dynamic keywords from today's brief
    if brief_data:
        dynamic_kws = get_dynamic_keywords(brief_data)
        for kw in dynamic_kws[:3]:
            results = search_listen_notes(kw, listen_notes_key, published_after=since)
            for ep in results:
                ep_id = ep.get("id", "")
                if ep_id and ep_id not in seen_ids:
                    seen_ids.add(ep_id)
                    all_episodes.append(ep)

    # Filter to curated shows only
    curated_episodes = []
    for ep in all_episodes:
        podcast_title = (ep.get("podcast", {}) or {}).get("title_original", "")
        if any(show.lower() in podcast_title.lower() for show in CURATED_SHOWS):
            curated_episodes.append(ep)

    # If no curated shows found, use top results from all
    if not curated_episodes:
        curated_episodes = all_episodes[:max_transcripts]

    print(f"Found {len(curated_episodes)} relevant podcast episodes in the last 48 hours.")

    # Fetch transcripts for top episodes (costs $0.10 each via Spoken.md)
    signals = []
    for ep in curated_episodes[:max_transcripts]:
        title = ep.get("title_original", "")
        podcast_name = (ep.get("podcast", {}) or {}).get("title_original", "")
        audio_url = ep.get("audio", "") or ep.get("link", "")
        description = ep.get("description_original", "")[:300]

        transcript = None
        if audio_url and os.getenv("SPOKEN_API_KEY"):
            print(f"Fetching transcript: {title[:60]}...")
            transcript = get_transcript_spoken(title, podcast_name, audio_url)
            if transcript:
                # Take first 1500 chars for the brief context — enough for synthesis
                transcript = transcript[:1500]

        signals.append({
            "title": title,
            "podcast": podcast_name,
            "description": description,
            "transcript_snippet": transcript,
            "link": ep.get("link", ""),
            "pub_date": ep.get("pub_date_ms", ""),
        })

    return signals


def summarize_podcast_signals(signals):
    """Format podcast signals for the Claude synthesis prompt."""
    if not signals:
        return "\nNo new podcast episodes found in the last 48 hours from curated shows.\n"
    text = "\nPodcast Intelligence (curated AI & entrepreneurship shows, last 48h):\n"
    for s in signals:
        text += f"\n[{s['podcast']}] {s['title']}\n"
        if s.get("transcript_snippet"):
            text += f"Transcript excerpt: {s['transcript_snippet'][:500]}\n"
        elif s.get("description"):
            text += f"Description: {s['description']}\n"
        if s.get("link"):
            text += f"Link: {s['link']}\n"
    return text
