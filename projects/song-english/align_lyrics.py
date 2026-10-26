#!/usr/bin/env python3
"""Put real lyrics on the music: match lyric lines to Whisper word times.

    python3 align_lyrics.py the-voices                # one song
    python3 align_lyrics.py --all                     # every song in playlist.json
    python3 align_lyrics.py --all --transcribe        # ask the class Whisper first (if no raw file)
    python3 align_lyrics.py --all --report-only       # only print the report, write nothing

Input:
    songs/lyrics/<id>.txt       the lyrics: one sung line per line, empty line between verses,
                                "# source: <url>" on line 1, "#" lines are comments,
                                "[?]" after a word = not sure (kept in the report, hidden on the page)
    songs/raw/<id>.whisper.json the raw Whisper answer with word times (verbose_json)
                                (if it is missing: songs/raw/<id>.approx.json, word times
                                estimated from old line times - less exact, made by --make-approx)
Output:
    songs/<id>.json             lines with start/end; "♪" for music gaps > 8 s

How: lyric words and Whisper words are matched with difflib. A line's start/end come from
its matched words. A line with no matched word gets an estimated time between its neighbours.
Whisper words that match no lyric word are dropped (so invented lines disappear).
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

MAX_GAP = 8.0          # longer gap with no words -> "♪" line
MAX_WORDS = 12         # a longer line is reported
WORD_SECONDS = 0.35    # guess for one sung word, to stretch a line to its unmatched words


def tokens(text):
    """'It's 20/20, x-ray!' -> ['its', '2020', 'x', 'ray']"""
    text = text.lower().replace("’", "'")
    text = re.sub(r"(\d)/(\d)", r"\1\2", text)
    text = text.replace("'", "")
    return re.findall(r"[a-z0-9]+", text)


def read_lyrics(path):
    """-> source, list of {text, check, verse} (verse: first line of a verse)"""
    source = ""
    lines = []
    new_verse = True
    with open(path, encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if raw.startswith("#"):
                m = re.match(r"#\s*source:\s*(.*)", raw)
                if m and not source:
                    source = m.group(1)
                continue
            if not raw:
                new_verse = True
                continue
            check = "[?]" in raw
            text = re.sub(r"\s*\[\?\]", "", raw).strip()
            if text:
                lines.append({"text": text, "check": check, "verse": new_verse})
                new_verse = False
    return source, lines


def whisper_tokens(answer):
    """-> list of (token, start, end); one Whisper word can give several tokens"""
    out = []
    for w in answer.get("words") or []:
        for t in tokens(w["word"]):
            out.append((t, float(w["start"]), float(w["end"])))
    return out


def audio_length(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def align(lyric_lines, wtokens, length):
    # lyric tokens with their line number
    ltok = []
    for i, line in enumerate(lyric_lines):
        for t in tokens(line["text"]):
            ltok.append((t, i))

    # Whisper words after the end of the audio are always invented: drop them
    if length:
        wtokens = [w for w in wtokens if w[1] < length]

    sm = difflib.SequenceMatcher(None, [t for t, _ in ltok], [t for t, _, _ in wtokens], autojunk=False)
    match = {}  # lyric token index -> whisper token index
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            match[a + k] = b + k

    n = len(lyric_lines)
    per_line = [[] for _ in range(n)]       # (position in line, whisper index)
    count = [0] * n
    for idx, (_, li) in enumerate(ltok):
        pos = count[li]
        count[li] += 1
        if idx in match:
            per_line[li].append((pos, match[idx]))

    times = [None] * n
    for li in range(n):
        m = per_line[li]
        if not m:
            continue
        first_pos, first_w = m[0]
        last_pos, last_w = m[-1]
        start = wtokens[first_w][1] - first_pos * WORD_SECONDS
        end = wtokens[last_w][2] + (count[li] - 1 - last_pos) * WORD_SECONDS
        times[li] = [start, end, len(m), count[li]]

    # lines with no match: share the time between the known neighbours
    li = 0
    while li < n:
        if times[li] is not None:
            li += 1
            continue
        j = li
        while j < n and times[j] is None:
            j += 1
        left = times[li - 1][1] if li > 0 else 0.0
        right = times[j][0] if j < n else (length or left + 3.0 * (j - li))
        if right < left:
            right = left
        words = [max(count[k], 1) for k in range(li, j)]
        total = sum(words)
        # no room: share the line before with them, by number of words
        if right - left < total * WORD_SECONDS and li > 0:
            prev_words = max(count[li - 1], 1)
            span_start = times[li - 1][0]
            left = span_start + (right - span_start) * prev_words / (prev_words + total)
            times[li - 1][1] = left
        t = left
        for k in range(li, j):
            d = (right - left) * words[k - li] / total
            times[k] = [t, t + d, 0, count[k]]
            t += d
        li = j

    # times must go up: count problems, then fix them
    backwards = 0
    for k in range(n):
        start, end = times[k][0], times[k][1]
        prev_end = times[k - 1][1] if k else 0.0
        if start < prev_end - 0.05:
            backwards += 1
            start = prev_end
        start = max(start, 0.0)
        end = max(end, start + 0.3)
        if k + 1 < n and end > times[k + 1][0] and times[k + 1][0] > start:
            end = times[k + 1][0]
        times[k][0], times[k][1] = start, end

    matched = len(match)
    return times, matched, len(ltok), backwards


def build_lines(lyric_lines, times, length):
    out = []
    for line, (start, end, _, _) in zip(lyric_lines, times):
        item = {"start": round(start, 2), "end": round(end, 2), "text": line["text"]}
        if line["verse"]:
            item["verse"] = True
        if line["check"]:
            item["check"] = True
        out.append(item)

    with_music = []
    if out and out[0]["start"] > MAX_GAP:
        with_music.append({"start": 0, "end": out[0]["start"], "text": "♪"})
    for i, line in enumerate(out):
        with_music.append(line)
        nxt = out[i + 1]["start"] if i + 1 < len(out) else length
        if nxt and nxt - line["end"] > MAX_GAP:
            with_music.append({"start": line["end"], "end": round(nxt, 2), "text": "♪"})
    return with_music


def make_approx(song_id):
    """Estimate word times from the old line times in songs/<id>.json (only a stand-in
    for the real Whisper file: words are spread evenly inside each line)."""
    out = "songs/raw/%s.approx.json" % song_id
    if os.path.exists(out):
        return out
    with open("songs/%s.json" % song_id, encoding="utf-8") as f:
        old = json.load(f)
    words = []
    for line in old["lines"]:
        if line["text"] == "♪":
            continue
        parts = line["text"].split()
        weights = [len(p) + 2 for p in parts]
        total = sum(weights)
        t = line["start"]
        for p, wgt in zip(parts, weights):
            d = (line["end"] - line["start"]) * wgt / total
            words.append({"word": " " + p, "start": round(t, 2), "end": round(t + d, 2)})
            t += d
    answer = {
        "note": "NOT a Whisper answer: word times estimated from the old line times in songs/%s.json. "
                "Replace with songs/raw/%s.whisper.json (python3 align_lyrics.py %s --transcribe)."
                % (song_id, song_id, song_id),
        "text": " ".join(w["word"].strip() for w in words),
        "words": words,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(answer, f, ensure_ascii=False, indent=1)
    return out


def load_raw(song, transcribe):
    sid = song["id"]
    real = "songs/raw/%s.whisper.json" % sid
    approx = "songs/raw/%s.approx.json" % sid
    if not os.path.exists(real) and transcribe:
        from make_lyrics import transcribe as whisper
        print("  asking Whisper for %s ..." % song["audio"])
        answer = whisper(song["audio"])
        with open(real, "w", encoding="utf-8") as f:
            json.dump(answer, f, ensure_ascii=False, indent=1)
    for path in (real, approx):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return path, json.load(f)
    return None, None


def do_song(song, args):
    sid = song["id"]
    print("== %s (%s)" % (sid, song.get("title", "")))
    lyr_path = "songs/lyrics/%s.txt" % sid
    if not os.path.exists(lyr_path):
        print("  no %s - skipped" % lyr_path)
        return None
    if args.make_approx:
        make_approx(sid)
    raw_path, answer = load_raw(song, args.transcribe)
    if not answer:
        print("  no raw word times (songs/raw/%s.whisper.json) - run with --transcribe" % sid)
        return None

    source, lyric_lines = read_lyrics(lyr_path)
    length = audio_length(song["audio"])
    times, matched, total, backwards = align(lyric_lines, whisper_tokens(answer), length)
    lines = build_lines(lyric_lines, times, length)

    pct = 100.0 * matched / total if total else 0.0
    no_match = [i for i, t in enumerate(times) if t[2] == 0]
    long_lines = [l["text"] for l in lyric_lines if len(l["text"].split()) > MAX_WORDS]
    going_up = all(lines[i]["start"] <= lines[i + 1]["start"] for i in range(len(lines) - 1))
    check = [l["text"] for l in lyric_lines if l["check"]]

    print("  word times : %s%s" % (raw_path, "  (ESTIMATED, not real Whisper)" if "approx" in raw_path else ""))
    print("  matched    : %d / %d lyric words = %.0f%%%s" % (matched, total, pct, "" if pct >= 80 else "  << below 80%"))
    print("  lines      : %d sung + %d ♪   (longest %d words%s)" % (
        len(lyric_lines), len(lines) - len(lyric_lines),
        max(len(l["text"].split()) for l in lyric_lines), ", TOO LONG: %s" % long_lines if long_lines else ""))
    print("  no match   : %s" % (", ".join('%d "%s"' % (i + 1, lyric_lines[i]["text"]) for i in no_match) or "none"))
    print("  backwards  : %d fixed; times always go up: %s" % (backwards, "yes" if going_up else "NO"))
    print("  to check   : %d lines with [?]" % len(check))

    if not args.report_only:
        with open("songs/%s.json" % sid, encoding="utf-8") as f:
            old = json.load(f)
        old["lines"] = lines
        if source:
            old["lyricsSource"] = source
        with open("songs/%s.json" % sid, "w", encoding="utf-8") as f:
            json.dump(old, f, ensure_ascii=False, indent=1)
        print("  wrote songs/%s.json" % sid)
    return pct


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ids", nargs="*")
    p.add_argument("--all", action="store_true", help="every song in playlist.json")
    p.add_argument("--transcribe", action="store_true", help="call the class Whisper if songs/raw/<id>.whisper.json is missing")
    p.add_argument("--make-approx", action="store_true", help="make songs/raw/<id>.approx.json from the old line times")
    p.add_argument("--report-only", action="store_true", help="print the report, do not write songs/<id>.json")
    args = p.parse_args()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("playlist.json", encoding="utf-8") as f:
        songs = json.load(f)["songs"]
    if not args.all:
        if not args.ids:
            sys.exit("give song ids or --all")
        songs = [s for s in songs if s["id"] in args.ids]
    for song in songs:
        do_song(song, args)


if __name__ == "__main__":
    main()
