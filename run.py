from scripts.fetch import fetch_all
from scripts.summarize import summarize, generate_audio
from scripts.render import render
from scripts.generate_autocontent import generate_podcast, generate_infographic, build_brief_text
from datetime import date

def run():
    today = date.today().strftime("%Y-%m-%d")

    print("Fetching all intelligence signals...")
    articles, polymarket, jobs, stocks, patents, github, arxiv, funding, regulatory = fetch_all()
    print(f"Fetched {len(articles)} articles, {len(polymarket)} Polymarket, {len(jobs)} jobs, {len(stocks)} stocks, {len(github)} GitHub, {arxiv['total']} arXiv, {len(funding)} funding, {len(regulatory)} regulatory.")

    print("Generating analyst report with Claude...")
    brief_data = summarize(articles, polymarket, jobs, stocks, github, arxiv, funding, regulatory)
    print("Brief generated.")

    print("Generating AutoContent podcast...")
    brief_text = build_brief_text(brief_data)
    podcast_path = generate_podcast(brief_text, today)
    if podcast_path:
        brief_data["audio_path"] = podcast_path
        print("Podcast generated via AutoContent.")
    else:
        print("AutoContent podcast failed — falling back to ElevenLabs...")
        audio_path = generate_audio(brief_data["podcast_script"])
        if audio_path:
            brief_data["audio_path"] = audio_path

    print("Generating AutoContent infographic...")
    infographic_path = generate_infographic(brief_text, today)
    if infographic_path:
        brief_data["infographic_path"] = infographic_path
        print("Infographic generated.")
    else:
        print("Infographic generation failed — skipping.")

    print("Rendering HTML...")
    render(brief_data)
    print("Done. Open index.html to view your brief.")

if __name__ == "__main__":
    run()