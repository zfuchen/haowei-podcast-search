#!/usr/bin/env python3
"""
Diarize an episode: detect who is speaking when, merge with Whisper transcript.
Usage: python3 diarize_episode.py <episode_id>
Example: python3 diarize_episode.py EP1
"""
import sys, os, json, time

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env = {}
    if os.path.exists(env_path):
        for line in open(env_path):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

def diarize(audio_path, hf_token, num_speakers=3, timeout=1800):
    from pyannote.audio import Pipeline
    print("Loading pyannote diarization pipeline...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    print(f"Running diarization on {audio_path}...")
    start = time.time()
    diarization = pipeline(audio_path, num_speakers=num_speakers)
    elapsed = time.time() - start
    print(f"Diarization done in {elapsed:.0f}s")

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker
        })
    return segments

def assign_speakers(whisper_segments, diar_segments):
    """
    For each Whisper segment, find the most overlapping diarization speaker.
    """
    def overlap(a_start, a_end, b_start, b_end):
        return max(0, min(a_end, b_end) - max(a_start, b_start))

    result = []
    for seg in whisper_segments:
        best_speaker = "unknown"
        best_overlap = 0
        for d in diar_segments:
            o = overlap(seg["start"], seg["end"], d["start"], d["end"])
            if o > best_overlap:
                best_overlap = o
                best_speaker = d["speaker"]
        result.append({**seg, "speaker": best_speaker})
    return result

def rebuild_paragraphs(segments):
    """Rebuild 30-second paragraphs grouping by speaker."""
    paragraphs = []
    current = {"start": 0, "texts": [], "timestamp": "00:00", "speaker": "unknown"}
    for seg in segments:
        same_speaker = seg["speaker"] == current["speaker"]
        time_ok = seg["start"] - current["start"] <= 30
        if (same_speaker and time_ok) or not current["texts"]:
            current["texts"].append(seg["text"])
            current["speaker"] = seg["speaker"]
            if not current["texts"]:
                m, s = divmod(int(seg["start"]), 60)
                current["timestamp"] = f"{m:02d}:{s:02d}"
                current["start"] = seg["start"]
        else:
            if current["texts"]:
                paragraphs.append({
                    "timestamp": current["timestamp"],
                    "start": current["start"],
                    "speaker": current["speaker"],
                    "text": " ".join(current["texts"])
                })
            m, s = divmod(int(seg["start"]), 60)
            current = {
                "start": seg["start"],
                "texts": [seg["text"]],
                "timestamp": f"{m:02d}:{s:02d}",
                "speaker": seg["speaker"]
            }
    if current["texts"]:
        paragraphs.append({
            "timestamp": current["timestamp"],
            "start": current["start"],
            "speaker": current["speaker"],
            "text": " ".join(current["texts"])
        })
    return paragraphs

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 diarize_episode.py <episode_id>")
        sys.exit(1)

    ep_id = sys.argv[1]
    base = os.path.dirname(__file__)
    # Prefer WAV (faster for pyannote), fallback to MP3
    wav_path = os.path.join(base, "audio", f"{ep_id}.wav")
    mp3_path = os.path.join(base, "audio", f"{ep_id}.mp3")
    audio_path = wav_path if os.path.exists(wav_path) else mp3_path
    ep_json = os.path.join(base, "data", f"{ep_id}.json")
    diar_out = os.path.join(base, "data", f"{ep_id}_diarization.json")

    if not os.path.exists(audio_path):
        print(f"ERROR: Audio not found: {audio_path}")
        sys.exit(1)
    if not os.path.exists(ep_json):
        print(f"ERROR: Transcript not found: {ep_json}")
        sys.exit(1)

    env = load_env()
    hf_token = env.get("HF_TOKEN", os.environ.get("HF_TOKEN", ""))
    if not hf_token:
        print("ERROR: HF_TOKEN not set in .env")
        sys.exit(1)

    # Run diarization
    diar_segments = diarize(audio_path, hf_token)
    with open(diar_out, "w") as f:
        json.dump(diar_segments, f, indent=2)
    print(f"Saved diarization: {diar_out} ({len(diar_segments)} speaker turns)")

    # Print speaker stats
    from collections import Counter
    counts = Counter(d["speaker"] for d in diar_segments)
    print("\nSpeaker time estimate:")
    for sp, cnt in sorted(counts.items()):
        total_sec = sum(d["end"]-d["start"] for d in diar_segments if d["speaker"]==sp)
        print(f"  {sp}: {cnt} turns, {total_sec/60:.1f} min")

    # Merge with whisper segments
    with open(ep_json) as f:
        ep = json.load(f)

    ep["segments"] = assign_speakers(ep["segments"], diar_segments)
    ep["paragraphs"] = rebuild_paragraphs(ep["segments"])

    with open(ep_json, "w") as f:
        json.dump(ep, f, ensure_ascii=False, indent=2)
    print(f"\nUpdated {ep_json} with speaker labels")
    print("\nSample (first 5 paragraphs):")
    for p in ep["paragraphs"][:5]:
        sp = p.get("speaker", "unknown")
        print(f"  [{p['timestamp']}] {sp}: {p['text'][:60]}...")

if __name__ == "__main__":
    main()
