# Song English — our plan

**Goal:** learn English with songs: listen, read the lyrics, translate, do tests, talk with AI, write, watch.

**Where:** `~/work/projects/song-english/` — one page app (plain HTML, CSS, JS).

## Steps

| # | Step | Status | What it does |
|---|------|--------|--------------|
| 1 | Player + speed control | ✅ done | Play/pause, −5s/+5s, progress bar, speed 0.5x–1.5x (`index.html`, demo sound `demo.wav`). |
| 2 | Songs + lyrics | ✅ done | 5 free songs in `songs/` (Wired CD, CC Sampling Plus 1.0; Josh Woodward and Brad Sucks, CC BY / CC BY-SA from archive.org); lyrics made from Whisper word times (`make_lyrics.py`); pick a song, the lines highlight with the music, click a line to jump. |
| 3 | Translation | ✅ done | Button "Translate": the class chat model translates the lyrics to Russian or Kazakh under each line; press again to hide; one call per song+language. |
| 4 | Interactive tests | ✅ done | Button "Make test": AI picks 5 useful words/phrases from the lyrics and asks what each one means, 4 simple-English choices; "▶ Listen to the line" plays that part of the song; an answer turns green or red and the score shows. |
| 5 | AI conversation | ✅ done | Box "Talk about the song": the AI knows the lyrics, answers questions about words and lines in easy English, fixes your mistakes gently and asks a question back; "Clear chat" starts again; the chat empties when you pick another song. |
| 6 | Essay | ✅ done | Box "Essay": write 4–8 sentences about the song (at least 20 words), press "Check my essay"; the AI says what is good, lists the mistakes with a correction and a short reason, gives a corrected version and one tip. Errors show on the page; the draft stays when you change songs. |
| 7 | Video | ⬜ last | Hardest: free video with synced text, or a "video-like" page (picture + text moving with the song). Decide later. |
| 8 | Popular songs | ⬜ next | No download (copyright). Use the official YouTube embed player: the user picks a video, pastes the lyrics, the text shows next to the player; speed inside YouTube's own player (0.25x–2x). |

## Finishing the site (phases)

| Phase | What | Status | Notes |
|---|---|---|---|
| 1 | Correct lyrics for all songs | 🟡 drafts done, need ear check + real Whisper times | `songs/lyrics/<id>.txt` (drafts from Whisper, unsure words `[?]`), `align_lyrics.py` (difflib match, ♪ gaps, report). No official lyrics sites and no class Whisper were reachable from the build machine, so word times are **estimated** (`songs/raw/<id>.approx.json`). In the class workspace run `python3 align_lyrics.py --all --transcribe` → saves `songs/raw/<id>.whisper.json` and re-times every line. Invented lines removed ("We'll be right back.", "Thank you.", 200× "oh"). |
| 2 | New layout (sticky player, tabs, language setting) | ⬜ | |
| 3 | Learning tools (repeat line, word popup, My words, keys, saved progress) | ⬜ | |
| 4 | Solid AI (callAI, AI-off mode, saved translations, better test/chat/essay) | ⬜ | |
| 5 | YouTube songs + tap to sync | ⬜ | |
| 6 | Karaoke / full-screen mode | ⬜ | |
| 7 | Clean up, README, accessibility, publish | ⬜ | |

**How to make lyrics for a song:** write `songs/lyrics/<id>.txt` (`# source: <url>` on line 1, one sung line per line,
empty line between verses, `[?]` after an unsure word) → `python3 align_lyrics.py <id> --transcribe` → read the report
(target: 80%+ matched, times always go up, no line over 12 words).

## Rules (important)

- **Popular songs:** no download — copyright. Free songs only.
- **Later option:** official YouTube embed player. No download, speed works inside its player (0.25x–2x), you type the lyrics yourself.
- **One step at a time:** build one step → test it → then the next. Every step gets its own test.
- **Publishing:** `frp-publish projects/song-english` after the page is ready (model calls do not work on the public link).

**Next command:** `/build` → step 8 (popular songs: official YouTube embed + pasted lyrics), then step 7 (video).
