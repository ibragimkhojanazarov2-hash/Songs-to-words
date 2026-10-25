#!/usr/bin/env python3
"""Make lyrics with line times for a song.

    python3 make_lyrics.py songs/name.mp3 --id name --title "Title" --artist "Artist"
    python3 make_lyrics.py --id name --json saved_whisper.json   # reuse an answer

The words come from the class speech model (Whisper, English). Lines are short
(up to 8 words or 6 seconds), and a "no words" line (music) fills long gaps.
Writes songs/<id>.json.
"""
import argparse
import json
import re
import sys

import requests

API = "http://127.0.0.1:19040/v1"


def transcribe(path):
    with open(path, "rb") as audio:
        r = requests.post(
            API + "/audio/transcriptions",
            files={"file": audio},
            data={
                "model": "whisper",
                "language": "en",
                "response_format": "verbose_json",
                "timestamp_granularities[]": "word",
            },
            timeout=600,
        )
    r.raise_for_status()
    return r.json()


def make_lines(words, max_words=8, max_seconds=6.0, max_gap=8.0):
    lines = []
    current = []

    def flush():
        if current:
            text = " ".join(w["word"].strip() for w in current)
            text = re.sub(r"\s+", " ", text).strip()
            lines.append({
                "start": round(current[0]["start"], 2),
                "end": round(current[-1]["end"], 2),
                "text": text,
            })
            current.clear()

    for w in words:
        if current:
            long_line = len(current) >= max_words or w["end"] - current[0]["start"] > max_seconds
            sentence_end = re.search(r"[.!?]$", current[-1]["word"].strip())
            pause = w["start"] - current[-1]["end"] > max_gap
            if long_line or sentence_end or pause:
                flush()
        current.append(w)
    flush()

    # music with no words: intro and long pauses
    with_music = []
    if lines and lines[0]["start"] > max_gap:
        with_music.append({"start": 0, "end": lines[0]["start"], "text": "♪"})
    for i, line in enumerate(lines):
        with_music.append(line)
        if i + 1 < len(lines) and lines[i + 1]["start"] - line["end"] > max_gap:
            with_music.append({"start": line["end"], "end": lines[i + 1]["start"], "text": "♪"})
    return with_music


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio", nargs="?")
    p.add_argument("--json", help="use a saved Whisper verbose_json answer instead of calling the model")
    p.add_argument("--id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--artist", default="")
    p.add_argument("--license", dest="license_name", default="")
    p.add_argument("--license-url", default="")
    p.add_argument("--source", default="")
    args = p.parse_args()

    if args.json:
        with open(args.json) as f:
            answer = json.load(f)
    elif args.audio:
        answer = transcribe(args.audio)
    else:
        sys.exit("give an audio file or --json")

    words = answer.get("words") or []
    if not words:
        sys.exit("no words in the answer: check the request (form fields) first")

    song = {
        "id": args.id,
        "title": args.title,
        "artist": args.artist,
        "license": args.license_name,
        "licenseUrl": args.license_url,
        "source": args.source,
        "lines": make_lines(words),
    }
    out = "songs/%s.json" % args.id
    with open(out, "w", encoding="utf-8") as f:
        json.dump(song, f, ensure_ascii=False, indent=1)
    print("wrote %s: %d lines, %d words" % (out, len(song["lines"]), len(words)))


if __name__ == "__main__":
    main()
