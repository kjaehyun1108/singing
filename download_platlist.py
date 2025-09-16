# download_playlist.py
import os
import yt_dlp
import json
import time
import random
import re

# === 설정 ===
PLAYLIST_URL = "https://music.youtube.com/playlist?list=PLhUWQzeeX8LyRvS-2Qo_XesXcGEOHn1sC"
OUTPUT_DIR = "karaoke_dataset"
META_FILE = os.path.join(OUTPUT_DIR, "metadata.json")
ARCHIVE_FILE = os.path.join(OUTPUT_DIR, "downloaded.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# yt-dlp 옵션
ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(OUTPUT_DIR, "%(playlist_index)03d - %(title)s.%(ext)s"),
    "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "192"}],
    "ignoreerrors": True,
    "noplaylist": False,
    "yesplaylist": True,
    "download_archive": ARCHIVE_FILE,
    "quiet": True,
}

# metadata.json 불러오기/초기화
if os.path.exists(META_FILE):
    with open(META_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
else:
    metadata = []

def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', "_", name)

def save_metadata():
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def download_playlist(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "entries" not in info:
            print("플레이리스트 없음")
            return

        for entry in info["entries"]:
            if not entry:
                continue

            idx = entry.get("playlist_index", 0)
            title = entry.get("title", "Unknown Title")
            uploader = entry.get("uploader", "Unknown Artist")
            duration = entry.get("duration", 0)

            safe_title = sanitize_filename(title)
            filename = f"{idx:03d} - {safe_title}.wav"
            filepath = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(filepath):
                print(f"⏭ 이미 존재: {filename}")
            else:
                try:
                    print(f"⏳ 다운로드 중: {filename}")
                    ydl.download([entry["webpage_url"]])
                except Exception as e:
                    print(f"⚠️ 다운로드 실패: {filename} ({e})")
                    continue

            exists = any(d["file"] == filename for d in metadata)
            if not exists:
                if os.path.exists(filepath):
                    metadata.append({
                        "index": idx,
                        "title": title,
                        "artist": uploader,
                        "duration": duration,
                        "file": filename
                    })
                    save_metadata()
                    print(f"💾 metadata.json 저장: {filename}")
                else:
                    print(f"❌ 파일 없음, metadata는 저장하지 않음: {filename}")

            time.sleep(random.uniform(5, 10))

    print(f"✅ 다운로드 완료. 총 {len(metadata)}곡 저장됨.")

if __name__ == "__main__":
    download_playlist(PLAYLIST_URL)
