#!/usr/bin/env python3
"""Token-free speaker diarization tuned for this 2-person Mandarin podcast.

Pipeline (per the research recommendation):
  1. sherpa-onnx offline diarization: pyannote-segmentation-3.0 (ONNX) +
     a Mandarin CAM++ voice-embedding model, with num_speakers fixed to 2.
  2. Label the two clusters with an *enrolled* reference voiceprint of the host
     (Georgia, who appears in every episode): whichever cluster is closer to her
     voiceprint = "A" (Georgia), the other = "B" (guest). This fixes the
     label-permutation problem that blind clustering can't solve.
  3. Assign each Whisper segment to a speaker by maximum time overlap.

Models live in ../transcribe_work/diar_models (downloaded once, not committed).
The host voiceprint is cached at ../transcribe_work/georgia_ref.npy.
"""
import os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "..", "transcribe_work")
MODELS = os.path.join(WORK, "diar_models")
SEG = os.path.join(MODELS, "sherpa-onnx-pyannote-segmentation-3-0", "model.onnx")
EMB = os.path.join(MODELS, "campplus.onnx")
REF = os.path.join(WORK, "georgia_ref.npy")
SR = 16000

# clean solo-Georgia openings used to build her reference voiceprint (slug, start, end)
ENROLL_CLIPS = [("ep-05", 1, 20), ("ep-06", 1, 22), ("ep-04", 1, 24)]

_extractor = None


def _load_audio(path, start=None, end=None):
    import librosa
    wav, _ = librosa.load(path, sr=SR, mono=True)
    if start is not None:
        wav = wav[int(start * SR):int(end * SR)]
    return np.ascontiguousarray(wav, dtype=np.float32)


def _embedder():
    global _extractor
    if _extractor is None:
        import sherpa_onnx
        cfg = sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=EMB)
        _extractor = sherpa_onnx.SpeakerEmbeddingExtractor(cfg)
    return _extractor


def _embed(samples):
    ext = _embedder()
    s = ext.create_stream()
    s.accept_waveform(SR, samples)
    s.input_finished()
    return np.array(ext.compute(s), dtype=np.float32)


def _cos(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _find_audio(slug):
    import glob
    for p in sorted(glob.glob(os.path.join(WORK, f"{slug}.*"))):
        if not p.endswith(".raw.json"):
            return p
    return None


def georgia_reference():
    if os.path.exists(REF):
        return np.load(REF)
    embs = []
    for slug, a, b in ENROLL_CLIPS:
        ap = _find_audio(slug)
        if ap:
            embs.append(_embed(_load_audio(ap, a, b)))
    if not embs:
        return None
    ref = np.mean(embs, axis=0)
    np.save(REF, ref)
    return ref


def diarize(audio_path, segments, n_speakers=2):
    import sherpa_onnx
    cfg = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=SEG)),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=EMB),
        clustering=sherpa_onnx.FastClusteringConfig(num_clusters=n_speakers),
        min_duration_on=0.3, min_duration_off=0.5,
    )
    sd = sherpa_onnx.OfflineSpeakerDiarization(cfg)
    wav = _load_audio(audio_path)
    res = sd.process(wav).sort_by_start_time()
    turns = [(s.start, s.end, s.speaker) for s in res]
    if not turns:
        return None

    # map cluster index -> A/B using Georgia's voiceprint
    ref = georgia_reference()
    label = {}
    if ref is not None:
        for spk in set(t[2] for t in turns):
            # mean embedding over this cluster's longest few turns
            segs = sorted([t for t in turns if t[2] == spk], key=lambda t: t[1] - t[0], reverse=True)[:6]
            embs = [_embed(wav[int(a * SR):int(b * SR)]) for a, b, _ in segs if b - a >= 0.5]
            label[spk] = np.mean([_cos(e, ref) for e in embs]) if embs else -1
        georgia_cluster = max(label, key=label.get)
        spk2ab = {spk: ("A" if spk == georgia_cluster else "B") for spk in label}
    else:
        spk2ab = {spk: ("A" if spk == turns[0][2] else "B") for spk in set(t[2] for t in turns)}

    # assign each Whisper segment to the max-overlap diarization turn
    out = []
    for seg in segments:
        s0, s1 = seg["start"], seg["end"]
        best, best_ov = None, 0.0
        for a, b, spk in turns:
            ov = max(0.0, min(s1, b) - max(s0, a))
            if ov > best_ov:
                best_ov, best = ov, spk
        out.append(spk2ab.get(best, "A") if best is not None else (out[-1] if out else "A"))
    return out
