from flask import Flask, request, jsonify, send_file
import os
import subprocess
import uuid
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    youtube_url = data.get("youtube_url")
    user_id = data.get("user_id")

    if not youtube_url or not user_id:
        return jsonify({"error": "Missing YouTube URL or user_id"}), 400

    session_id = str(uuid.uuid4())
    user_dir = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    wordcloud_path = os.path.join(user_dir, f"{session_id}.png")

    # Extract video ID from URL
    def extract_video_id(url):
        match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
        return match.group(1) if match else None

    video_id = extract_video_id(youtube_url)
    words = []

    try:
        # Try yt-dlp first
        subtitle_path = os.path.join(UPLOAD_DIR, f"{session_id}.vtt")
        subprocess.run([
            'yt-dlp',
            '--write-auto-sub',
            '--sub-lang', 'en',
            '--skip-download',
            '--output', os.path.join(UPLOAD_DIR, f'{session_id}.%(ext)s'),
            youtube_url
        ], check=True)

        vtt_file = next((f for f in os.listdir(UPLOAD_DIR) if f.startswith(session_id) and f.endswith('.vtt')), None)
        if vtt_file:
            with open(os.path.join(UPLOAD_DIR, vtt_file), 'r') as f:
                lines = f.readlines()
            for line in lines:
                if "-->" not in line and not line.strip().isdigit():
                    words.extend(line.strip().split())
        else:
            raise FileNotFoundError

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to youtube-transcript-api
        if not video_id:
            return jsonify({"error": "Could not extract video ID."}), 400
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            for entry in transcript:
                words.extend(entry['text'].split())
        except (TranscriptsDisabled, NoTranscriptFound):
            return jsonify({"error": "Subtitles not available for this video."}), 404
        except Exception as e:
            return jsonify({"error": f"Transcript fetch failed: {str(e)}"}), 500

    word_counts = Counter(w.lower() for w in words if w.isalpha())

    wc = WordCloud(width=800, height=400, background_color='white')
    wc.generate_from_frequencies(word_counts)
    wc.to_file(wordcloud_path)

    return jsonify({
        "status": "success",
        "wordcloud_image": f"/wordcloud/{user_id}/{session_id}.png",
        "word_count": sum(word_counts.values())
    })

@app.route('/wordcloud/<user_id>/<image_name>')
def serve_wordcloud(user_id, image_name):
    image_path = os.path.join(UPLOAD_DIR, user_id, image_name)
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    return jsonify({"error": "Image not found."}), 404

@app.route("/", methods=["GET"])
def home():
    return "WordCloud API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
