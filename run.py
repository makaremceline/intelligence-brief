from scripts.fetch import fetch_all
from scripts.summarize import summarize, generate_audio
from scripts.render import render
from scripts.generate_autocontent import generate_podcast, generate_infographic, generate_quiz, generate_slide_deck, build_brief_text
from datetime import date

def run():
    today = date.today().strftime("%Y-%m-%d")

    print("Fetching all intelligence signals...")
    articles, polymarket, jobs, stocks, patents, github, arxiv, funding, regulatory = fetch_all()
    print(f"Fetched {len(articles)} articles, {len(polymarket)} Polymarket, {len(jobs)} jobs, {len(stocks)} stocks, {len(github)} GitHub, {arxiv['total']} arXiv, {len(funding)} funding, {len(regulatory)} regulatory.")

    print("Generating analyst report with Claude...")
    brief_data = summarize(articles, polymarket, jobs, stocks, github, arxiv, funding, regulatory)
    print("Brief generated.")

    brief_text = build_brief_text(brief_data)

    # ── PODCAST ──
    print("Generating AutoContent podcast...")
    podcast_path = generate_podcast(brief_text, today)
    if podcast_path:
        brief_data["audio_path"] = podcast_path
        print("Podcast generated via AutoContent.")
    else:
        print("AutoContent podcast failed — falling back to ElevenLabs...")
        audio_path = generate_audio(brief_data["podcast_script"])
        if audio_path:
            brief_data["audio_path"] = audio_path

    # ── INFOGRAPHIC ──
    print("Generating AutoContent infographic...")
    infographic_path = generate_infographic(brief_text, today)
    if infographic_path:
        brief_data["infographic_path"] = infographic_path
        print("Infographic generated.")
    else:
        print("Infographic generation failed — skipping.")

    # ── QUIZ ──
    print("Generating AutoContent quiz...")
    quiz_result = generate_quiz(brief_text, today)
    if quiz_result:
        # generate_quiz returns the raw JSON string or saves to a path
        if isinstance(quiz_result, str) and quiz_result.startswith("briefs/"):
            brief_data["quiz_path"] = quiz_result
        else:
            brief_data["quiz_data"] = quiz_result
        print("Quiz generated.")
    else:
        print("Quiz generation failed — will generate on demand in browser.")

    # ── SLIDE DECK ──
    print("Generating AutoContent slide deck...")
    slides_result = generate_slide_deck(brief_text, today)
    if slides_result:
        if isinstance(slides_result, str) and slides_result.startswith("http"):
            brief_data["slides_path"] = slides_result  # URL
        elif isinstance(slides_result, str) and slides_result.startswith("briefs/"):
            brief_data["slides_path"] = slides_result  # local path
        else:
            brief_data["slides_data"] = slides_result
        print("Slide deck generated.")
    else:
        print("Slide deck generation failed — will generate on demand in browser.")

    print("Rendering HTML...")
    render(brief_data)
    print("Done. Open index.html to view your brief.")

if __name__ == "__main__":
    run()
