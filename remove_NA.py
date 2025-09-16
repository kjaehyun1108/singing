import os
import json

OUTPUT_DIR = "karaoke_dataset"
META_FILE = os.path.join(OUTPUT_DIR, "metadata.json")

# 1) NA 파일 제거
for fname in os.listdir(OUTPUT_DIR):
    if fname.startswith("NA-") and fname.endswith(".wav"):
        try:
            os.remove(os.path.join(OUTPUT_DIR, fname))
            print(f"❌ NA 파일 제거: {fname}")
        except Exception as e:
            print(f"⚠️ 제거 실패: {fname} ({e})")

# 2) metadata.json 동기화
if os.path.exists(META_FILE):
    with open(META_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # 존재하지 않는 파일이나 NA 파일은 제거
    metadata = [m for m in metadata if os.path.exists(os.path.join(OUTPUT_DIR, m["file"])) 
                and not m["file"].startswith("NA-")]

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print("✅ metadata.json 동기화 완료")
else:
    print("⚠️ metadata.json 없음")
