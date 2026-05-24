from scripts.fetch import fetch_all
from scripts.summarize import summarize, generate_audio
from scripts.render import render

def run():
    print("Fetching articles, X posts and Polymarket data...")
    articles, polymarket = fetch_all()
    print(f"Fetched {len(articles)} articles, {len(polymarket)} Polymarket signals.")

    print("Generating analyst report with Claude...")
    brief_data = summarize(articles, polymarket)
    print("Brief generated.")

    print("Generating podcast audio with ElevenLabs...")
    audio_path = generate_audio(brief_data["podcast_script"])
    if audio_path:
        brief_data["audio_path"] = audio_path

    print("Rendering HTML...")
    render(brief_data)
    print("Done. Open index.html to view your brief.")

if __name__ == "__main__":
    run()