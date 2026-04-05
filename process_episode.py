#!/usr/bin/env python3
"""
Podcast Episode Processor
Usage: python3 process_episode.py <episode_url> <episode_title> [--model tiny|small|medium]
Downloads, transcribes, and outputs structured JSON for the wiki.
"""
import sys, os, json, time, argparse, subprocess, tempfile
import urllib.request
import whisper

def download_episode(url, output_path, timeout=120):
    print(f"Downloading: {url[:60]}...")
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r, open(output_path, 'wb') as f:
            total = int(r.headers.get('Content-Length', 0))
            downloaded = 0
            while chunk := r.read(65536):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded/total*100
                    print(f"\r  {pct:.0f}% ({downloaded//1024//1024}MB/{total//1024//1024}MB)", end='', flush=True)
        print(f"\n  Done in {time.time()-start:.0f}s")
        return True
    except Exception as e:
        print(f"\n  FAILED: {e}")
        return False

def transcribe(audio_path, model_name="tiny", lang="zh", timeout=3600):
    print(f"Loading whisper {model_name} model...")
    model = whisper.load_model(model_name)
    print(f"Transcribing (timeout={timeout}s)...")
    start = time.time()
    result = model.transcribe(audio_path, language=lang, verbose=False)
    elapsed = time.time() - start
    print(f"Transcription done: {elapsed:.0f}s, {len(result['segments'])} segments")
    return result

def build_structured(raw, episode_id, title, podcast_name):
    segments = []
    for seg in raw["segments"]:
        m, s = divmod(int(seg["start"]), 60)
        segments.append({
            "id": seg["id"],
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "timestamp": f"{m:02d}:{s:02d}",
            "text": seg["text"].strip(),
            "speaker": "unknown"
        })

    # 合併成 30 秒段落
    paragraphs = []
    current = {"start": 0, "texts": [], "timestamp": "00:00"}
    for seg in segments:
        if seg["start"] - current["start"] > 30 and current["texts"]:
            paragraphs.append({
                "timestamp": current["timestamp"],
                "start": current["start"],
                "text": " ".join(current["texts"])
            })
            current = {"start": seg["start"], "texts": [seg["text"]], "timestamp": seg["timestamp"]}
        else:
            current["texts"].append(seg["text"])
    if current["texts"]:
        paragraphs.append({"timestamp": current["timestamp"], "start": current["start"], "text": " ".join(current["texts"])})

    return {
        "episode": episode_id,
        "title": title,
        "podcast": podcast_name,
        "segments": segments,
        "paragraphs": paragraphs
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("episode_id")
    parser.add_argument("title")
    parser.add_argument("--model", default="tiny", choices=["tiny","small","medium","large"])
    parser.add_argument("--output-dir", default="/root/podcast_wiki/data")
    parser.add_argument("--audio-dir", default="/root/podcast_wiki/audio")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.audio_dir, exist_ok=True)

    audio_path = os.path.join(args.audio_dir, f"{args.episode_id}.mp3")
    output_path = os.path.join(args.output_dir, f"{args.episode_id}.json")

    if os.path.exists(output_path):
        print(f"Already processed: {output_path}")
        return

    if not os.path.exists(audio_path):
        if not download_episode(args.url, audio_path):
            sys.exit(1)

    raw = transcribe(audio_path, model_name=args.model)
    structured = build_structured(raw, args.episode_id, args.title, "好味小姐開束縛我還你原形")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
