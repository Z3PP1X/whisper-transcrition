import argparse
import base64
import os
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

from postprocess import write_markdown
from preprocess import extract_audio_chunks, find_videos

load_dotenv()
URL = os.getenv("OPENROUTER_ENDPOINT") or "https://openrouter.ai/api/v1/audio/transcriptions"
API_KEY = os.environ["OPENROUTER_API_KEY"]


def transcribe(audio: Path) -> dict:
    payload = {
        "model": "openai/whisper-large-v3",
        "input_audio": {"data": base64.b64encode(audio.read_bytes()).decode(), "format": "mp3"},
        # Ask for segment timestamps; ignored by providers that don't support it.
        "response_format": "verbose_json",
    }
    r = requests.post(URL, headers={"Authorization": f"Bearer {API_KEY}"}, json=payload, timeout=600)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser(description="Transcribe videos to markdown via Whisper on OpenRouter")
    ap.add_argument("input", type=Path, help="video file or folder of videos")
    ap.add_argument("-o", "--output", type=Path, default=Path("transcripts"))
    args = ap.parse_args()

    for video in find_videos(args.input):
        print(f"Processing {video.name} ...")
        segments = []
        with tempfile.TemporaryDirectory() as tmp:
            for offset, chunk in extract_audio_chunks(video, Path(tmp)):
                result = transcribe(chunk)
                if result.get("segments"):
                    segments += [(offset + s["start"], s["text"]) for s in result["segments"]]
                else:  # no segment data: fall back to one timestamp per chunk
                    segments.append((offset, result["text"]))
        print("  ->", write_markdown(video, segments, args.output))


if __name__ == "__main__":
    main()
