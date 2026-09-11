#!/usr/bin/env python3
"""Token-free speaker diarization by clustering voice embeddings.

diarize(audio_path, segments) embeds each Whisper segment with Resemblyzer's
pretrained voice encoder (bundled, no Hugging Face token), clusters the
embeddings into 2 speakers with KMeans, smooths the label sequence to remove
isolated flips, and returns an "A"/"B" label per segment. "A" = the speaker of
the earliest segment (the host opens the show).

Speaker turns therefore come from actual voice changes, not from pauses. If
resemblyzer or the audio is missing, postprocess.py falls back to alternation.
"""
import numpy as np

SR = 16000
MIN_LEN = 0.7   # pad slices shorter than this before embedding
SKIP_LEN = 0.2  # segments with less audio than this are labelled by a neighbour


def _smooth(labels, passes=2, window=1):
    """Majority-vote smoothing to remove single-segment flicker."""
    labels = list(labels)
    for _ in range(passes):
        out = labels[:]
        for i in range(len(labels)):
            lo, hi = max(0, i - window), min(len(labels), i + window + 1)
            win = labels[lo:hi]
            out[i] = max(set(win), key=win.count)
        labels = out
    return labels


def diarize(audio_path, segments, n_speakers=2):
    import librosa
    from resemblyzer import VoiceEncoder
    from sklearn.cluster import KMeans

    # load at 16k mono WITHOUT silence trimming so sample offsets match segment times
    wav, _ = librosa.load(audio_path, sr=SR, mono=True)
    encoder = VoiceEncoder(verbose=False)

    embs, idx = [], []
    for i, s in enumerate(segments):
        a, b = int(s["start"] * SR), int(s["end"] * SR)
        if b - a < int(SKIP_LEN * SR):
            continue
        if b - a < int(MIN_LEN * SR):             # widen short slices around centre
            mid = (a + b) // 2
            half = int(MIN_LEN * SR / 2)
            a, b = max(0, mid - half), min(len(wav), mid + half)
        try:
            embs.append(encoder.embed_utterance(wav[a:b]))
            idx.append(i)
        except Exception:
            continue

    if len(embs) < n_speakers:
        return None

    km = KMeans(n_clusters=n_speakers, n_init=10, random_state=0).fit(np.array(embs))
    raw = {i: int(l) for i, l in zip(idx, km.labels_)}
    # fill skipped segments from nearest embedded neighbour
    labels = []
    for i in range(len(segments)):
        if i in raw:
            labels.append(raw[i])
        else:
            nearest = min(idx, key=lambda k: abs(k - i))
            labels.append(raw[nearest])

    labels = _smooth(labels)
    a_cluster = labels[0]
    return ["A" if l == a_cluster else "B" for l in labels]
