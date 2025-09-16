# lyrics_fetch.py
import os
import json
import requests

META_FILE = "karaoke_dataset/metadata.json"
LYRICS_DIR = "karaoke_dataset_lyrics"
GENIUS_API_TOKEN = "YOUR_GENIUS_API_TOKEN"  # 발급 필요

os.makedirs(LYRICS_DIR, exist_ok=True)

with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

def fetch_lyrics(artist, title):
    base_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    params = {"q": f"{artist} {title}"}

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    hits = data.get("response", {}).get("hits", [])
    if hits:
        # 첫 번째 결과 URL 가져오기
        song_url = hits[0]["result"]["url"]
        return song_url
    return None

for entry in metadata:
    filename = entry["file"]
    lyrics_file = os.path.join(LYRICS_DIR, os.path.splitext(filename)[0] + ".txt")

    if os.path.exists(lyrics_file):
        print(f"⏭ 이미 존재: {lyrics_file}")
        continue

    lyrics_url = fetch_lyrics(entry["artist"], entry["title"])
    if lyrics_url:
        with open(lyrics_file, "w", encoding="utf-8") as f:
            f.write(lyrics_url)  # 실제 가사 크롤링 대신 URL 저장 (추후 확장 가능)
        print(f"💾 저장: {lyrics_file}")
    else:
        print(f"❌ 가사 없음: {entry['title']}")
# lyrics_fetch.py
import os
import json
import requests

META_FILE = "karaoke_dataset/metadata.json"
LYRICS_DIR = "karaoke_dataset_lyrics"
GENIUS_API_TOKEN = "YOUR_GENIUS_API_TOKEN"  # 발급 필요

os.makedirs(LYRICS_DIR, exist_ok=True)

with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

def fetch_lyrics(artist, title):
    base_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}
    params = {"q": f"{artist} {title}"}

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    hits = data.get("response", {}).get("hits", [])
    if hits:
        # 첫 번째 결과 URL 가져오기
        song_url = hits[0]["result"]["url"]
        return song_url
    return None

for entry in metadata:
    filename = entry["file"]
    lyrics_file = os.path.join(LYRICS_DIR, os.path.splitext(filename)[0] + ".txt")

    if os.path.exists(lyrics_file):
        print(f"⏭ 이미 존재: {lyrics_file}")
        continue

    lyrics_url = fetch_lyrics(entry["artist"], entry["title"])
    if lyrics_url:
        with open(lyrics_file, "w", encoding="utf-8") as f:
            f.write(lyrics_url)  # 실제 가사 크롤링 대신 URL 저장 (추후 확장 가능)
        print(f"💾 저장: {lyrics_file}")
    else:
        print(f"❌ 가사 없음: {entry['title']}")
