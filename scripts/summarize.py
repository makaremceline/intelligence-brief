import anthropic
import os
import json
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def load_feedback():
    try:
        with open("feedback.json", "r") as f:
            return json.load(f)
    except:
        return []

def summarize(articles, polymarket):
    today = date.today().strftime("%Y-%m-%d")

    article_text = ""
    for i, a in enumerate(articles):
        article_text += f"[{i}] Source: {a['source']} | Title: {a['title']} | URL: {a['link']} | Summary: {a['summary']}\n\n"

    polymarket_text = ""
    if polymarket:
        polymarket_text = "\nPolymarket AI & Entrepreneurship Markets (current smart money odds):\n"
        for p in polymarket:
            polymarket_text += f"- {p['question']}: {p['odds']}% probability | Volume: ${p['volume']:,.0f} | {p['url']}\n"
    else:
        polymarket_text = "\nNo active Polymarket markets found for AI & entrepreneurship today.\n"

    feedback = load_feedback()
    feedback_text = ""
    if feedback:
        feedback_text = "\nPast feedback to incorporate:\n"
        for f in feedback[-5:]:
            label = {1: "Useful", 2: "Missed something", 3: "Not relevant"}.get(f["rating"], "")
            feedback_text += f"- {f['date']} | {label}"
            if f.get("note"):
                feedback_text += f": {f['note']}"
            feedback_text += "\n"

    prompt = f"""
You are a senior intelligence analyst and AI & entrepreneurship expert writing a daily brief for a sophisticated audience — founders, investors, and professors who need signal, not noise.

Today's date: {today}
{feedback_text}

Here are today's articles and X posts:
{article_text}
{polymarket_text}

Produce THREE outputs:

---

OUTPUT 1: ANALYST REPORT
Write a single, long-form research report synthesizing everything. NOT a list of summaries — a real analyst report that draws connections, adds context, and tells the reader what it all means.

Sections:
- **The Big Picture**: 2-3 sentences on the single most important thing happening today
- **Key Developments**: 4-6 meaty paragraphs, each covering a major theme. Cite sources inline like (TechCrunch), (a16z), (@karpathy). Add your own analysis and historical context. Make each paragraph substantial — at least 5-6 sentences.
- **Signals to Watch**: 3 forward-looking observations based on today's news and Polymarket
- **Polymarket Intelligence**: A full paragraph interpreting the probability swings — what shifted, why it likely happened, what it signals for AI & entrepreneurship

Tone: Smart but approachable. Like a brilliant analyst over coffee. Full paragraphs, no bullet lists.

---

OUTPUT 2: ARTICLES
Group articles into dynamic tags. Each gets: title, source, url, date, one-sentence summary.

---

OUTPUT 3: PODCAST SCRIPT
Write a DEEP DIVE podcast script — minimum 10-12 minutes when read aloud (roughly 1500-2000 words of dialogue).

Two hosts:
- Alex: analytical, precise, loves connecting dots across industries
- Jordan: curious, asks the questions a smart non-expert would ask, occasionally skeptical

Structure:
1. Cold open — one provocative hook line from Alex
2. Main story 1 — deep dive, back and forth, at least 6-8 exchanges
3. Main story 2 — different topic, equally deep, 6-8 exchanges
3. Polymarket segment — Jordan asks what the market is saying, Alex interprets
4. Signals segment — what to watch this week
5. Sign off — natural, not stiff

Rules:
- Natural conversation — interruptions, follow-up questions, "wait, so what you're saying is..."
- Each line should be 2-4 sentences minimum, not one-liners
- Go deep on context and implications, not just "X happened"
- Reference specific sources and quotes where relevant

---

Return ONLY this JSON, no preamble:
{{
  "date": "{today}",
  "report": {{
    "big_picture": "2-3 sentence paragraph...",
    "key_developments": [
      {{"theme": "Theme title", "content": "Substantial paragraph with inline citations..."}}
    ],
    "signals_to_watch": ["Signal 1 full sentence...", "Signal 2...", "Signal 3..."],
    "polymarket_intelligence": "Full paragraph..."
  }},
  "tags": [
    {{
      "tag": "Tag Name",
      "articles": [
        {{
          "title": "Article title",
          "source": "Source name",
          "url": "https://...",
          "date": "{today}",
          "summary": "One sentence."
        }}
      ]
    }}
  ],
  "podcast_script": [
    {{"speaker": "Alex", "line": "2-4 sentence line..."}},
    {{"speaker": "Jordan", "line": "2-4 sentence line..."}}
  ],
  "worth_reading": {{
    "title": "Article title",
    "url": "https://...",
    "source": "Source name",
    "reason": "One line reason"
  }}
}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    clean = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)

    os.makedirs("briefs", exist_ok=True)
    with open(f"briefs/brief_{today}.json", "w") as f:
        json.dump(data, f, indent=2)

    return data


def generate_audio(podcast_script):
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import VoiceSettings

        el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

        voices = {
            "Alex": "6u6JbqKdaQy89ENzLSju",
            "Jordan": "KwXKDxukTBuBpah1Xv41"
        }

        today = date.today().strftime("%Y-%m-%d")
        os.makedirs("briefs", exist_ok=True)
        output_path = f"briefs/podcast_{today}.mp3"

        audio_segments = []
        for i, line in enumerate(podcast_script):
            speaker = line["speaker"]
            text = line["line"]
            voice_id = voices.get(speaker, voices["Alex"])
            print(f"  Generating line {i+1}/{len(podcast_script)} ({speaker})...")

            try:
                audio = el_client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id="eleven_turbo_v2_5",
                    voice_settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75,
                        style=0.3,
                        use_speaker_boost=True
                    )
                )
                audio_segments.append(b"".join(audio))
            except Exception as line_error:
                print(f"  Skipping line {i+1}: {line_error}")
                continue

        if not audio_segments:
            print("No audio segments generated.")
            return None

        with open(output_path, "wb") as f:
            for segment in audio_segments:
                f.write(segment)

        print(f"Podcast audio saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"Audio generation failed: {e}")
        return None