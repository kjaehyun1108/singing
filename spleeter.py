# spleeter_separate.py
import os
from spleeter.separator import Separator
import json

INPUT_DIR = "karaoke_dataset"
OUTPUT_DIR = "karaoke_dataset_separated"
META_FILE = os.path.join(INPUT_DIR, "metadata.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Spleeter 2stems 모델
separator = Separator('spleeter:2stems')

# metadata 불러오기
with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

for entry in metadata:
    filename = entry["file"]
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, os.path.splitext(filename)[0])

    if not os.path.exists(input_path):
        print(f"❌ 원본 WAV 없음: {input_path}")
        continue

    try:
        print(f"🎵 Spleeter 분리 중: {filename}")
        separator.separate_to_file(input_path, output_path)
    except Exception as e:
        print(f"⚠️ 분리 실패: {filename} ({e})")
