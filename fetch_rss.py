#!/usr/bin/env python3
"""
Fetch RSS feed and generate episode manifest (url, title, duration).
"""
import sys, json, urllib.request, xml.etree.ElementTree as ET

RSS_URL = "https://feeds.soundon.fm/podcasts/adf29720-e93b-4856-a09e-b73544147ec4.xml"

def main():
    print(f"Fetching RSS: {RSS_URL}")
    req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        content = r.read().decode('utf-8')

    root = ET.fromstring(content)
    ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
    items = root.findall('.//item')

    episodes = []
    for item in items:
        title_el = item.find('title')
        enc = item.find('enclosure')
        dur_el = item.find('itunes:duration', ns)
        pub_el = item.find('pubDate')
        if enc is None: continue

        title = title_el.text if title_el is not None else ''
        url = enc.attrib.get('url', '')
        dur = int(dur_el.text) if dur_el is not None else 0

        # Extract EP number from title
        ep_id = title.split(' ')[0] if title else 'UNKNOWN'

        episodes.append({
            "episode_id": ep_id,
            "title": title,
            "url": url,
            "duration_sec": dur,
            "pub_date": pub_el.text if pub_el is not None else ''
        })

    out = "/root/podcast_wiki/data/manifest.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(episodes)} episodes to {out}")

if __name__ == "__main__":
    main()
