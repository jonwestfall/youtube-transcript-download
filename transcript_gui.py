import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from datetime import datetime
import os

# Utility functions
def get_video_id(url):
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip("/")
    return None

def get_video_ids_from_playlist(url):
    html = requests.get(url).text
    return list(set(re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)))

def get_video_ids_from_channel(url):
    html = requests.get(url + "/videos").text
    return list(set(re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)))

def save_transcript(video_id, batch_file, output_callback):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        filename = f"{video_id}.txt"
        with open(filename, "w", encoding="utf-8") as f_individual, open(batch_file, "a", encoding="utf-8") as f_batch:
            f_batch.write(f"\n=== Transcript for {video_id} ===\n")
            for entry in transcript:
                line = f"{entry['text']}\n"
                f_individual.write(line)
                f_batch.write(line)
        output_callback(f"Saved: {filename}")
    except (TranscriptsDisabled, NoTranscriptFound):
        output_callback(f"No transcript available: {video_id}")
    except Exception as e:
        output_callback(f"Error for {video_id}: {e}")

# Threaded operation
def process_transcripts(url, mode, count, status_output):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    batch_file = f"{timestamp}.txt"

    def log(msg):
        status_output.insert(tk.END, msg + "\n")
        status_output.see(tk.END)

    try:
        if mode == "video":
            video_id = get_video_id(url)
            if video_id:
                save_transcript(video_id, batch_file, log)
            else:
                log("Could not extract video ID.")
        elif mode == "playlist":
            video_ids = get_video_ids_from_playlist(url)[:count]
            for vid in video_ids:
                save_transcript(vid, batch_file, log)
        elif mode == "channel":
            video_ids = get_video_ids_from_channel(url)[:count]
            for vid in video_ids:
                save_transcript(vid, batch_file, log)
        log(f"\nBatch transcript saved to: {batch_file}")
    except Exception as e:
        log(f"Unexpected error: {e}")

# GUI setup
def launch_gui():
    root = tk.Tk()
    root.title("YouTube Transcript Downloader")

    tk.Label(root, text="YouTube URL:").grid(row=0, column=0, sticky="w")
    url_entry = tk.Entry(root, width=60)
    url_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

    mode_var = tk.StringVar(value="video")
    tk.Radiobutton(root, text="Single Video", variable=mode_var, value="video").grid(row=1, column=0, sticky="w")
    tk.Radiobutton(root, text="Playlist", variable=mode_var, value="playlist").grid(row=1, column=1, sticky="w")
    tk.Radiobutton(root, text="Channel", variable=mode_var, value="channel").grid(row=1, column=2, sticky="w")

    tk.Label(root, text="# of Videos:").grid(row=2, column=0, sticky="w")
    count_spin = tk.Spinbox(root, from_=1, to=100, width=5)
    count_spin.grid(row=2, column=1, sticky="w")

    status_output = tk.Text(root, height=15, width=80)
    status_output.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    def start_download():
        url = url_entry.get()
        mode = mode_var.get()
        count = int(count_spin.get())
        status_output.delete(1.0, tk.END)
        thread = threading.Thread(target=process_transcripts, args=(url, mode, count, status_output))
        thread.start()

    tk.Button(root, text="Download Transcripts", command=start_download).grid(row=3, column=0, columnspan=3, pady=10)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()

