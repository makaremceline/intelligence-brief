import requests
import time
import os

AUTOCONTENT_API_URL = "https://api.autocontentapi.com/content/Create"
AUTOCONTENT_STATUS_URL = "https://api.autocontentapi.com/content/Status"


def build_brief_text(brief_data):
    report = brief_data.get("report", {})
    lines = []
    lines.append("Daily Intelligence Brief")
    lines.append(report.get("big_picture", ""))
    for dev in report.get("key_developments", []):
        lines.append(dev.get("theme", "") + ": " + dev.get("content", ""))
    for s in report.get("signals_to_watch", []):
        lines.append("- " + s)
    lines.append(report.get("polymarket_intelligence", ""))
    lines.append(report.get("funding_intelligence", ""))
    lines.append(report.get("regulatory_intelligence", ""))
    return "\n".join(lines)


def generate_podcast(brief_text, today):
    api_key = os.getenv("AUTOCONTENT_API_KEY")
    try:
        print("Requesting AutoContent podcast...")
        r = requests.post(
            AUTOCONTENT_API_URL,
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json"
            },
            json={
                "resources": [{"type": "text", "content": brief_text}],
                "text": "Generate a 10-minute two-host podcast on AI and entrepreneurship.",
                "outputType": "audio"
            },
            timeout=30
        )
        print("Status code:", r.status_code)
        d = r.json()
        print("Response:", d)
        rid = d.get("requestId") or d.get("request_id") or d.get("id")
        if not rid:
            print("No ID found")
            return None
        print("Polling for ID:", rid)
        for attempt in range(60):
            time.sleep(10)
            sr = requests.get(
                AUTOCONTENT_STATUS_URL + "/" + rid,
                headers={"Authorization": "Bearer " + api_key},
                timeout=10
            )
            sd = sr.json()
            status = sd.get("status", "")
            print("Attempt", attempt + 1, "status:", status, "| full:", sd)
            if status == 100 or status == "completed":
                url = sd.get("audio_url") or sd.get("audioUrl") or sd.get("url")
                if url:
                    audio = requests.get(url, timeout=60)
                    os.makedirs("briefs", exist_ok=True)
                    path = "briefs/podcast_" + today + ".mp3"
                    with open(path, "wb") as f:
                        f.write(audio.content)
                    print("Saved:", path)
                    return path
            elif status == "failed" or status == -1:
                print("Failed")
                return None
        return None
    except Exception as e:
        print("Error:", e)
        return None


def generate_infographic(brief_text, today):
    api_key = os.getenv("AUTOCONTENT_API_KEY")
    try:
        print("Requesting AutoContent infographic...")
        r = requests.post(
            AUTOCONTENT_API_URL,
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json"
            },
            json={
                "resources": [{"type": "text", "content": brief_text}],
                "text": "Generate a professional infographic summarizing today's AI developments.",
                "outputType": "infographic"
            },
            timeout=30
        )
        d = r.json()
        rid = d.get("requestId") or d.get("request_id") or d.get("id")
        if not rid:
            return None
        print("Polling for ID:", rid)
        for attempt in range(60):
            time.sleep(10)
            sr = requests.get(
                AUTOCONTENT_STATUS_URL + "/" + rid,
                headers={"Authorization": "Bearer " + api_key},
                timeout=10
            )
            sd = sr.json()
            status = sd.get("status", "")
            print("Attempt", attempt + 1, "status:", status, "| full:", sd)
            if status == "completed" or status == 100:
                url = sd.get("url") or sd.get("imageUrl") or sd.get("image_url")
                if url:
                    img = requests.get(url, timeout=60)
                    os.makedirs("briefs", exist_ok=True)
                    path = "briefs/infographic_" + today + ".png"
                    with open(path, "wb") as f:
                        f.write(img.content)
                    print("Saved:", path)
                    return path
            elif status == "failed" or status == -1:
                return None
        return None
    except Exception as e:
        print("Error:", e)
        return None