# YouTube Transcript Downloader (GUI)

This Python application allows you to download transcripts from YouTube videos, playlists, or channels using a simple graphical interface. It uses the `youtube-transcript-api` and basic URL scraping to extract video IDs and save available transcripts.

## 🚀 Features

- Accepts individual YouTube video URLs, playlist URLs, or channel URLs
- Downloads auto-generated or uploaded transcripts (if available)
- Saves each transcript as `VIDEO_ID.txt`
- Also creates a timestamped batch file (`YYYY-MM-DD_HH-MM-SS.txt`) with all transcripts from the current session
- Responsive Tkinter GUI with real-time status output
- Threaded to avoid freezing the interface

## 🖥️ Running the App

### Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
