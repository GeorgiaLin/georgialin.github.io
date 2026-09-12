#!/usr/bin/env python3
"""Local transcription step (run on your own machine — needs Whisper + ffmpeg).

For every episode in _podcast/ that doesn't yet have a transcript (or with
--force / a specific slug) this:
  1. downloads the audio,
  2. runs Whisper large-v3 with a punctuation prompt,
  3. caches the RAW segments to ../transcribe_work/<slug>.raw.json, and
  4. calls postprocess.py to write _data/transcripts/<slug>.json
     (turn-merge + heuristic A/B speakers + corrections).

Keeping the raw cache means you can re-tune speaker splitting / merging /
corrections instantly via postprocess.py, without re-transcribing.

Companion to sync_podcast.py (which pulls new episodes from RSS). Intentionally
NOT run in CI — CPU-only runners are slow; run it locally, commit the JSON.

Usage:
    .podvenv/bin/python scripts/transcribe.py            # all missing
    .podvenv/bin/python scripts/transcribe.py ep-06      # one episode
    .podvenv/bin/python scripts/transcribe.py --force    # redo all

Requires (in a venv):  pip install openai-whisper   (+ ffmpeg on PATH)
"""
import os, re, sys, json, time, glob, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # so `import postprocess` works
import postprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POD = os.path.join(ROOT, "_podcast")
RAW = os.path.join(ROOT, "..", "transcribe_work")
OUT = os.path.join(ROOT, "_data", "transcripts")
MODEL = "large-v3"
PROMPT = "以下是一段普通话对话播客的转写，请使用完整的句子并加上标点符号，如逗号、句号、问号。"


def parse_eps():
    eps = []
    for f in sorted(glob.glob(f"{POD}/*.md")):
        fm = open(f, encoding="utf-8").read().split("---", 2)[1]
        g = lambda k: (re.search(rf'^{k}:\s*"?(.*?)"?\s*$', fm, re.M) or [None, None])[1]
        eps.append(dict(slug=os.path.basename(f)[:-3], number=int(g("number")),
                        audio=g("audio"), duration=g("duration"), guid=g("guid")))
    dsec = lambda d: (lambda p: p[0] * 60 + p[1] if len(p) == 2 else p[0] * 3600 + p[1] * 60 + p[2])(
        [int(x) for x in d.split(":")])
    eps.sort(key=lambda e: dsec(e["duration"]))
    return eps


def main(argv):
    import whisper
    force = "--force" in argv
    only = [a for a in argv if not a.startswith("-")]
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    todo = [e for e in parse_eps()
            if (not only or e["slug"] in only)
            and (force or not os.path.exists(f"{OUT}/{e['slug']}.json"))]
    if not todo:
        print("Nothing to transcribe (use --force to redo).")
        return
    print(f"loading {MODEL} ...", flush=True)
    model = whisper.load_model(MODEL)

    for e in todo:
        slug = e["slug"]
        ext = e["audio"].split(".")[-1].split("?")[0]
        audio = os.path.join(RAW, f"{slug}.{ext}")
        if not os.path.exists(audio):
            print(f"downloading {slug} ...", flush=True)
            urllib.request.urlretrieve(e["audio"], audio)
        print(f"transcribing {slug} ({e['duration']}) ...", flush=True)
        s = time.time()
        r = model.transcribe(audio, language="zh", fp16=False, verbose=False, initial_prompt=PROMPT)
        raw = {"slug": slug, "number": e["number"], "guid": e["guid"],
               "generated": time.strftime("%Y-%m-%d"), "model": MODEL,
               "segments": [{"start": round(x["start"], 2), "end": round(x["end"], 2),
                             "text": x["text"].strip()} for x in r["segments"] if x["text"].strip()]}
        json.dump(raw, open(f"{RAW}/{slug}.raw.json", "w"), ensure_ascii=False)
        postprocess.process(slug)   # writes _data/transcripts/<slug>.json
        print(f"  {len(raw['segments'])} raw segments in {time.time()-s:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
