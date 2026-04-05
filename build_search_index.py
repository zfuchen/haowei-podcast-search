#!/usr/bin/env python3
"""
Build a combined search index from all episode JSON files.
Outputs: data/search_index.json (for the web app)
"""
import json, os, glob

DATA_DIR = "/root/podcast_wiki/data"
OUTPUT = os.path.join(DATA_DIR, "search_index.json")

episodes = []
segments_all = []

for path in sorted(glob.glob(os.path.join(DATA_DIR, "EP*.json"))):
    with open(path) as f:
        ep = json.load(f)
    episodes.append({
        "episode": ep["episode"],
        "title": ep["title"],
        "segment_count": len(ep["paragraphs"])
    })
    for p in ep["paragraphs"]:
        segments_all.append({
            "ep": ep["episode"],
            "title": ep["title"],
            "ts": p["timestamp"],
            "start": p["start"],
            "text": p["text"]
        })

index = {
    "episodes": episodes,
    "segments": segments_all,
    "total_episodes": len(episodes),
    "total_segments": len(segments_all)
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, separators=(',', ':'))  # compact for web

print(f"Built index: {len(episodes)} episodes, {len(segments_all)} segments")
print(f"File size: {os.path.getsize(OUTPUT)//1024}KB")
