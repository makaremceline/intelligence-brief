import json
import os
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

load_dotenv()

def render(brief_data):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("brief.html")
    today = brief_data["date"]

    # Load last 7 days of briefs for chatbot context
    past_briefs = []
    briefs_dir = "briefs"
    if os.path.exists(briefs_dir):
        files = sorted([f for f in os.listdir(briefs_dir) if f.endswith(".json")])[-7:]
        for fname in files:
            try:
                with open(os.path.join(briefs_dir, fname), "r") as f:
                    past_briefs.append(json.load(f))
            except:
                continue

    audio_path = brief_data.get("audio_path", None)
    audio_filename = os.path.basename(audio_path) if audio_path else None

    infographic_path = brief_data.get("infographic_path", None)
    infographic_filename = os.path.basename(infographic_path) if infographic_path else None

    # Quiz data — could be a path or raw JSON string
    quiz_data = None
    quiz_path = brief_data.get("quiz_path", None)
    if quiz_path and os.path.exists(quiz_path):
        try:
            with open(quiz_path, "r") as f:
                quiz_data = f.read()
        except:
            quiz_data = None
    elif brief_data.get("quiz_data"):
        quiz_data = brief_data.get("quiz_data")

    # Slides data — could be a URL or raw JSON string
    slides_data = None
    slides_path = brief_data.get("slides_path", None)
    if slides_path:
        if slides_path.startswith("http"):
            slides_data = slides_path  # it's a URL
        elif os.path.exists(slides_path):
            try:
                with open(slides_path, "r") as f:
                    slides_data = f.read()
            except:
                slides_data = None
    elif brief_data.get("slides_data"):
        slides_data = brief_data.get("slides_data")

    # AutoContent API key — passed to template for browser-side polling
    autocontent_api_key = os.getenv("AUTOCONTENT_API_KEY", "")

    output = template.render(
        date=today,
        report=brief_data["report"],
        tags=brief_data.get("tags", {}),
        podcast_script=brief_data.get("podcast_script", []),
        worth_reading=brief_data.get("worth_reading", []),
        past_briefs_json=json.dumps(past_briefs),
        today_brief_json=json.dumps(brief_data),
        audio_filename=audio_filename,
        infographic_filename=infographic_filename,
        quiz_data=quiz_data,
        slides_data=slides_data,
        autocontent_api_key=autocontent_api_key,
    )

    filename = f"briefs/brief_{today}.html"
    os.makedirs("briefs", exist_ok=True)
    with open(filename, "w") as f:
        f.write(output)
    with open("index.html", "w") as f:
        f.write(output)
    print(f"Brief rendered: {filename}")
    return filename
