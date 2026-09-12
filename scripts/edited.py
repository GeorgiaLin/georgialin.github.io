#!/usr/bin/env python3
"""Build a transcript JSON from a hand-edited Markdown file.

When ../transcribe_work/edit_returned/<slug>.md exists, it is the source of
truth: Georgia's own edited transcript with her segmentation and speaker
labels. We take the text verbatim (only stripping the leading label), map
"Georgia"->A / "Julia"->B, and re-attach an approximate start timestamp per
paragraph by aligning to the cached audio transcription (so click-to-seek still
works; timestamps are secondary per her note).
"""
import os, re
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDIT_DIR = os.path.join(ROOT, "..", "transcribe_work", "edit_returned")
_KEEP = re.compile(r"[一-鿿A-Za-z0-9]")
# Host is always "Georgia"/"A"; the guest label varies per episode
# (Julia, An=余安, …). Any recognised non-host label maps to the guest (B).
_HOST = {"Georgia", "A"}
_GUEST = {"Julia", "Jilia", "Jualia", "An", "Anne", "B"}
_LABELS = _HOST | _GUEST
_SPK = re.compile(r"^\s*(" + "|".join(sorted(_LABELS, key=len, reverse=True)) + r")\s*[:：]?\s*(.*)$",
                  re.IGNORECASE)
_TS = re.compile(r"^\s*\[\d{1,2}:\d{2}\]\s*(.*)$")

# speaker of unlabeled/timestamp-only lines where the speaker switches without a label
_OVERRIDE = {
    "Solidcore其实是美国近几年": "B",
    "这个品类说白了": "B",
}


def edited_path(slug):
    p = os.path.join(EDIT_DIR, f"{slug}.md")
    return p if os.path.exists(p) else None


def _norm(s):
    return "".join(c.lower() for c in s if _KEEP.match(c))


def ensure_period(t):
    t = t.rstrip()
    if not t or t[-1] in "。！？?!…":
        return t
    if t[-1] in "，,、.":
        return t[:-1] + "。"
    return t + "。"


def _to_ab(name):
    return "A" if name.lower() in {h.lower() for h in _HOST} else "B"


def parse(md):
    paras = []                      # (spk|None, text)
    for line in md.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        m = _SPK.match(line)
        if m:
            paras.append((_to_ab(m.group(1)), m.group(2).strip("，,。：: ")))
            continue
        t = _TS.match(line)
        text = (t.group(1) if t else line).strip("，,。：: ")
        paras.append((None, text))
    # resolve unlabeled speakers
    out, prev = [], "A"
    for spk, text in paras:
        if spk is None:
            if "我是Julia" in text:
                spk = "B"
            elif "我是Georgia" in text:
                spk = "A"
            else:
                spk = next((v for k, v in _OVERRIDE.items() if k in text), prev)
        out.append((spk, text))
        prev = spk
    return [(s, t) for s, t in out if t]


def _timestamps(paras, raw_segments):
    spoken, times = [], []
    for s in raw_segments:
        for ch in (s.get("text") or ""):
            if _KEEP.match(ch):
                spoken.append(ch.lower())
                times.append(s["start"])
    spoken = "".join(spoken)
    out, pos = [], 0
    for spk, text in paras:
        n = _norm(text)
        probe = n[:16]
        idx = spoken.find(probe, pos) if probe else -1
        if idx < 0 and probe:
            idx = spoken.find(probe)
        if idx < 0:
            window = spoken[pos:pos + 4000]
            sm = SequenceMatcher(None, window, n[:40], autojunk=False)
            mm = sm.find_longest_match(0, len(window), 0, min(40, len(n)))
            idx = pos + mm.a if mm.size >= 6 else pos
        t = times[idx] if 0 <= idx < len(times) else (times[-1] if times else 0)
        out.append({"t": round(t, 1), "s": ensure_period(text), "spk": spk})
        pos = max(pos, idx + max(1, len(probe)))
    return out


def build(slug, raw_segments):
    p = edited_path(slug)
    if not p:
        return None
    paras = parse(open(p, encoding="utf-8").read())
    if not paras:
        return None
    return _timestamps(paras, raw_segments)
