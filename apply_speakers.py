#!/usr/bin/env python3
"""
Apply speaker names from speaker_mapping.json to an episode's transcript.
Usage: python3 apply_speakers.py <episode_id>
Run after filling in names in data/speaker_mapping.json.
"""
import sys, os, json

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 apply_speakers.py <episode_id>")
        sys.exit(1)

    ep_id = sys.argv[1]
    base = os.path.dirname(os.path.abspath(__file__))
    ep_json = os.path.join(base, "data", f"{ep_id}.json")
    mapping_json = os.path.join(base, "data", "speaker_mapping.json")

    with open(ep_json) as f:
        ep = json.load(f)
    with open(mapping_json) as f:
        mapping_data = json.load(f)

    mapping = {k: v["name"] for k, v in mapping_data["speakers"].items() if v["name"]}
    if not mapping:
        print("ERROR: speaker_mapping.json 裡的 name 欄位都是空的，請先填寫人名")
        sys.exit(1)

    print(f"Applying speaker names: {mapping}")

    def apply(speaker):
        return mapping.get(speaker, speaker)

    for seg in ep["segments"]:
        seg["speaker"] = apply(seg["speaker"])
    for para in ep["paragraphs"]:
        para["speaker"] = apply(para.get("speaker", "unknown"))

    with open(ep_json, "w") as f:
        json.dump(ep, f, ensure_ascii=False, indent=2)

    print(f"Done. Updated {ep_json}")
    print("\nSample:")
    for p in ep["paragraphs"][:5]:
        print(f"  [{p['timestamp']}] {p.get('speaker','?')}: {p['text'][:60]}...")

if __name__ == "__main__":
    main()
