import json
import os
from jinja2 import Environment, FileSystemLoader

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

    output = template.render(
        date=today,
        report=brief_data["report"],
        tags=brief_data["tags"],
        podcast_script=brief_data["podcast_script"],
        worth_reading=brief_data["worth_reading"],
        past_briefs_json=json.dumps(past_briefs),
        today_brief_json=json.dumps(brief_data),
        audio_filename=audio_filename,
        infographic_filename=infographic_filename,
    )

    filename = f"briefs/brief_{today}.html"
    with open(filename, "w") as f:
        f.write(output)

    with open("index.html", "w") as f:
        f.write(output)

    print(f"Brief rendered: {filename}")
    return filename