import re
import sys
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from datetime import datetime

YOUTUBE_BASE = "https://www.youtube.com"

def get_video_id(url):
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip("/")
    return None

def get_video_ids_from_playlist(url):
    print("📥 Fetching playlist videos...")
    html = requests.get(url).text
    return list(set(re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)))

def get_video_ids_from_channel(url):
    print("📥 Fetching channel videos...")
    html = requests.get(url + "/videos").text
    return list(set(re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)))

def save_transcript(video_id, batch_file):
    print(f"⏳ Downloading transcript for video ID: {video_id}")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        filename = f"{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f_individual, open(batch_file, "a", encoding="utf-8") as f_batch:
            f_batch.write(f"\n=== Transcript for {video_id} ===\n")
            for entry in transcript:
                line = f"{entry['text']}\n"
                f_individual.write(line)
                f_batch.write(line)
        print(f"✅ Saved transcript to {filename}")
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"⚠️ No transcript available for {video_id}")
    except Exception as e:
        print(f"❌ Error for {video_id}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_transcript.py <YouTube URL>")
        return

    url = sys.argv[1]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    batch_file = f"{timestamp}.txt"

    if "playlist?list=" in url:
        video_ids = get_video_ids_from_playlist(url)
        print(f"📃 Found {len(video_ids)} videos in playlist.")
        count = int(input("How many videos would you like to process? "))
        for vid in video_ids[:count]:
            save_transcript(vid, batch_file)

    elif any(segment in url for segment in ["/channel/", "/user/", "/c/"]):
        video_ids = get_video_ids_from_channel(url)
        print(f"📃 Found {len(video_ids)} recent videos on channel.")
        count = int(input("How many videos would you like to process? "))
        for vid in video_ids[:count]:
            save_transcript(vid, batch_file)

    else:
        video_id = get_video_id(url)
        if video_id:
            save_transcript(video_id, batch_file)
        else:
            print("❌ Could not extract video ID from URL.")

    print(f"\n📁 Batch transcript saved to: {batch_file}")

if __name__ == "__main__":
    main()
