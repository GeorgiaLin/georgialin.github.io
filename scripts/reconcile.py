#!/usr/bin/env python3
"""Assign speaker labels by aligning the transcript to a ground-truth 原稿.

When we have the original script (原稿) for an episode — with A:/B: turn markers —
its speaker structure is ground truth. We align the (possibly ad-libbed) spoken
transcript to the script with difflib and propagate each matched character's
speaker (A/B) back to the transcript segments. This is far more reliable than
audio diarization, and it naturally keeps a monologue as one A or one B block
instead of over-splitting it.

Matching is done on a punctuation-stripped representation so full/half-width
punctuation and spacing differences don't hurt alignment.

Scripts live in ../transcribe_work/scripts_src/<slug>.txt
"""
import os, re
from difflib import SequenceMatcher

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "..", "transcribe_work", "scripts_src")

_KEEP = re.compile(r"[\u4e00-\u9fffA-Za-z0-9]")   # CJK + latin + digits
_HEADER = re.compile(r"^(?:[一二三四五六七八九十]+、|最后|最终|排名|品牌|门店|均值|数据点数|\d+$)")


def script_path(slug):
    p = os.path.join(SCRIPTS, f"{slug}.txt")
    return p if os.path.exists(p) else None


def parse_script(text):
    """-> list of (speaker, text) turns from A:/B: markers."""
    turns, spk, buf = [], None, []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([AB])\s*[:：]\s*(.*)$", line)
        if m:
            if spk and buf:
                turns.append((spk, "".join(buf)))
            spk, buf = m.group(1), [m.group(2)]
        elif spk and not _HEADER.match(line):
            buf.append(line)          # continuation of current turn
    if spk and buf:
        turns.append((spk, "".join(buf)))
    return turns


def _normalize(chars_with_tag):
    """chars_with_tag: iterable of (char, tag). Keep only CJK/latin/digits.
    Returns (normalized_string, [tag per kept char])."""
    s, tags = [], []
    for ch, tag in chars_with_tag:
        if _KEEP.match(ch):
            s.append(ch.lower())
            tags.append(tag)
    return "".join(s), tags


def align_speakers(raw_segments, script_text):
    turns = parse_script(script_text)
    if not turns:
        return None

    # script side: normalized chars tagged with speaker
    script_norm, script_spk = _normalize(
        (ch, spk) for spk, txt in turns for ch in txt)
    # spoken side: normalized chars tagged with segment index
    spoken_norm, spoken_seg = _normalize(
        (ch, i) for i, s in enumerate(raw_segments) for ch in (s.get("text") or ""))
    if not script_norm or not spoken_norm:
        return None

    # propagate speaker from script -> spoken chars via matching blocks
    char_spk = [None] * len(spoken_norm)
    sm = SequenceMatcher(None, spoken_norm, script_norm, autojunk=False)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            char_spk[i + k] = script_spk[j + k]

    # majority speaker per segment
    votes = {}
    for pos, seg_i in enumerate(spoken_seg):
        sp = char_spk[pos]
        if sp is not None:
            votes.setdefault(seg_i, {"A": 0, "B": 0})[sp] += 1

    labels, last = [], "A"
    for i in range(len(raw_segments)):
        v = votes.get(i)
        if v:
            last = "A" if v["A"] >= v["B"] else "B"
        labels.append(last)
    return labels
