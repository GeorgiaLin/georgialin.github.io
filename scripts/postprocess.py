#!/usr/bin/env python3
"""Turn raw Whisper segments into the final transcript JSON the site renders.

Reads cached raw segments (../transcribe_work/<slug>.raw.json, from transcribe.py)
and writes _data/transcripts/<slug>.json with, per entry:
    {"t": <start sec>, "s": "<paragraph text>", "spk": "A" | "B"}

Pipeline:
  1. Merge consecutive raw segments into a *turn* — a new turn starts when the
     silence gap between segments exceeds GAP_TURN seconds.
  2. Label each turn A/B:
       - if resemblyzer + the cached audio are available -> cluster the turns'
         voice embeddings into 2 speakers (token-free, see diarize.py);
       - otherwise fall back to A/B alternation.
  3. Merge consecutive same-speaker turns into one paragraph.
  4. Apply scripts/corrections.json (wrong -> right).

Reads only cached data, so re-running is instant — tune the constants or edit
corrections.json and re-run without re-transcribing:
    python3 scripts/postprocess.py           # rebuild all cached episodes
    python3 scripts/postprocess.py ep-05      # just one
"""
import os, re, sys, json, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_data", "transcripts")
RAW = os.path.join(ROOT, "..", "transcribe_work")
CORR_FILE = os.path.join(ROOT, "scripts", "corrections.json")

GAP_TURN = 0.8       # silence (s) between segments that marks a new turn
BACKCHANNEL = 6      # chars; used only by the alternation fallback


def load_corrections():
    return json.load(open(CORR_FILE, encoding="utf-8")) if os.path.exists(CORR_FILE) else {}


_FULLWIDTH = {",": "，", "?": "？", "!": "！", ";": "；", ":": "："}


def to_fullwidth(text):
    """Whisper often emits half-width punctuation in Chinese; normalise it.
    Skips punctuation that sits between ASCII chars (e.g. inside numbers/URLs)."""
    out = []
    for i, ch in enumerate(text):
        if ch in _FULLWIDTH:
            prev = text[i - 1] if i > 0 else ""
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if (prev.isascii() and prev.isalnum()) and (nxt.isascii() and nxt.isalnum()):
                out.append(ch)          # keep, e.g. "3:15" or "a,b" inside latin
            else:
                out.append(_FULLWIDTH[ch])
        else:
            out.append(ch)
    return "".join(out)


def apply_corrections(text, corr):
    for wrong, right in corr.items():
        text = text.replace(wrong, right)
    return to_fullwidth(text)


def label_segments(raw_segments, audio_path):
    """One A/B label per raw segment. Voice clustering if possible, else pauses."""
    if audio_path and os.path.exists(audio_path):
        try:
            import diarize
            labels = diarize.diarize(audio_path, raw_segments)
            if labels:
                return labels, "voice"
        except Exception as e:
            print(f"  (voice diarization unavailable, using alternation: {e})")
    labels, spk, prev_end = [], "A", None
    for s in raw_segments:
        if prev_end is not None and (s["start"] - prev_end) >= GAP_TURN:
            spk = "B" if spk == "A" else "A"
        labels.append(spk)
        prev_end = s["end"]
    return labels, "alternation"


def build(raw_segments, corr, audio_path=None):
    labels, method = label_segments(raw_segments, audio_path)
    # merge consecutive same-speaker segments into paragraphs
    out = []
    for s, lab in zip(raw_segments, labels):
        txt = (s.get("text") or "").strip()
        if not txt:
            continue
        if out and out[-1]["spk"] == lab:
            out[-1]["s"] += txt
        else:
            out.append({"t": round(s["start"], 1), "s": txt, "spk": lab})
    for o in out:
        o["s"] = apply_corrections(o["s"].strip(), corr)
    return out, method


def find_audio(slug):
    for p in sorted(glob.glob(os.path.join(RAW, f"{slug}.*"))):
        if not p.endswith(".raw.json"):
            return p
    return None


def process(slug, corr):
    raw_path = os.path.join(RAW, f"{slug}.raw.json")
    if not os.path.exists(raw_path):
        print(f"! no raw cache for {slug}")
        return
    raw = json.load(open(raw_path, encoding="utf-8"))
    raw_segs = raw["segments"] if isinstance(raw, dict) else raw
    meta = raw if isinstance(raw, dict) else {}
    segs, method = build(raw_segs, corr, find_audio(slug))
    os.makedirs(OUT, exist_ok=True)
    json.dump({"slug": slug, "number": meta.get("number"), "guid": meta.get("guid"),
               "generated": meta.get("generated"), "model": meta.get("model", "large-v3"),
               "speakers_method": method, "segments": segs},
              open(os.path.join(OUT, f"{slug}.json"), "w"), ensure_ascii=False, indent=1)
    a = sum(1 for s in segs if s["spk"] == "A")
    print(f"{slug}: {len(raw_segs)} raw -> {len(segs)} paragraphs "
          f"(A={a}, B={len(segs)-a}, speakers={method})")


def main(argv):
    corr = load_corrections()
    only = [a for a in argv if not a.startswith("-")]
    slugs = only or [os.path.basename(p)[:-9] for p in sorted(glob.glob(f"{RAW}/*.raw.json"))]
    if not slugs:
        print("No raw caches found. Run transcribe.py first.")
    for slug in slugs:
        process(slug, corr)


if __name__ == "__main__":
    main(sys.argv[1:])
