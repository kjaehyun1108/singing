#!/usr/bin/env python3
import os
import json
import re
import shutil
from difflib import SequenceMatcher

# 설정
OUTPUT_DIR = "karaoke_dataset"
META_FILE = os.path.join(OUTPUT_DIR, "metadata.json")
UNMATCHED_FILE = os.path.join(OUTPUT_DIR, "unmatched.json")

# 안전 리네임(파일명 실제 변경) 여부: 기본 False
RENAME_FILES = False

# 퍼지 매칭 임계값 (0~1). 0.65 정도 권장, 낮추면 더 관대해짐
FUZZY_THRESHOLD = 0.65

# 유틸: 문자열 정규화 (소문자, 괄호내용/특수문자 제거, 공백 정리)
def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = s.lower()
    # 괄호 안의 내용 제거(대괄호/소괄호/중괄호)
    s = re.sub(r'\(.*?\)|\[.*?\]|{.*?}|<.*?>', ' ', s)
    # 특수문자 제거 (한글/영문/숫자/공백만 남김)
    s = re.sub(r"[^0-9a-z가-힣\s]", " ", s)
    # 다중공백 -> 단일공백, 양쪽 공백 제거
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# 유틸: 시퀀스매처 유사도
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 메인
if not os.path.exists(META_FILE):
    print("❌ metadata.json이 없습니다. 먼저 download_playlist.py 를 실행하세요.")
    raise SystemExit(1)

with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# 실제 폴더의 wav 파일 리스트 수집
wav_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(".wav")]
wav_files_set = set(wav_files)

print(f"폴더에서 발견된 WAV 파일 수: {len(wav_files)}")
print(f"metadata 항목 수: {len(metadata)}")

# 파일명에서 인덱스 및 본문을 뽑아 normalize한 캐시 생성
file_info = []
for fn in wav_files:
    # 인덱스 추출 (시작 001, 001-, 001_ 등)
    m = re.match(r'^\s*(\d{1,3})\s*[-_ ]\s*(.*)$', fn)
    if m:
        idx = int(m.group(1))
        body = m.group(2).rsplit('.', 1)[0]
    else:
        idx = None
        body = os.path.splitext(fn)[0]
    file_info.append({
        "filename": fn,
        "index": idx,
        "body": body,
        "norm": normalize_text(body)
    })

# 메타데이터 항목별로 매칭 시도
unmatched = []
matched_count = 0

# 먼저 인덱스 기반 매칭: metadata.index -> 파일 시작 숫자 match
for song in metadata:
    expected_idx = song.get("index")
    expected_name = f"{expected_idx:03d}" if isinstance(expected_idx, int) else None
    matched = False

    # 1) 인덱스로 정확 매칭 (파일명 앞부분 숫자와 일치)
    if expected_name:
        candidates = [fi for fi in file_info if fi["index"] == expected_idx]
        if len(candidates) == 1:
            # 한 개 찾음 -> 확정
            song["file"] = candidates[0]["filename"]
            matched = True
            matched_count += 1
            continue
        elif len(candidates) > 1:
            # 여러 후보면 제목 유사도로 선택
            norm_title = normalize_text(song.get("title",""))
            best = None
            best_score = -1
            for c in candidates:
                sc = similarity(norm_title, c["norm"])
                if sc > best_score:
                    best_score = sc
                    best = c
            if best:
                song["file"] = best["filename"]
                matched = True
                matched_count += 1
                continue

    # 2) 파일명에 metadata 'file' 값이 정확히 존재하는지 체크 (혹시 이미 정확함)
    existing = song.get("file")
    if existing and existing in wav_files_set:
        matched = True
        matched_count += 1
        continue

    # 3) 타이틀-아티스트 기반의 퍼지 매칭 (가장 비례 높은 후보 사용)
    norm_title = normalize_text(song.get("title",""))
    norm_artist = normalize_text(song.get("artist",""))
    best = None
    best_score = 0.0
    for c in file_info:
        score_title = similarity(norm_title, c["norm"])
        # 보통 제목 유사도 우선, 아티스트 포함 여부로 가중치
        artist_in_name = (normalize_text(c["body"]).find(norm_artist) != -1) if norm_artist else False
        score = score_title + (0.15 if artist_in_name else 0.0)
        if score > best_score:
            best_score = score
            best = c

    if best and best_score >= FUZZY_THRESHOLD:
        song["file"] = best["filename"]
        matched = True
        matched_count += 1
        continue

    # 4) 실패: unmatched로 기록
    unmatched.append({
        "index": song.get("index"),
        "title": song.get("title"),
        "artist": song.get("artist"),
        "expected_file": song.get("file")
    })

# 리포트
print(f"\n매칭 완료: 총 {matched_count}개 항목이 metadata에 연결되었습니다.")
print(f"매칭 실패 항목 수: {len(unmatched)} (상세: {UNMATCHED_FILE})")

# unmatched 파일 저장
with open(UNMATCHED_FILE, "w", encoding="utf-8") as f:
    json.dump(unmatched, f, ensure_ascii=False, indent=2)

# 선택적: 파일 리네임 (metadata 기준으로 파일명을 정리)
if RENAME_FILES:
    print("\n⚠️ RENAME_FILES=True: 실제 파일명을 metadata 기준으로 변경합니다.")
    for song in metadata:
        expected_fn = song.get("file")
        if not expected_fn:
            continue
        expected_path = os.path.join(OUTPUT_DIR, expected_fn)
        # 만약 이미 존재하면 건너뜀
        if os.path.exists(expected_path):
            continue
        # 현재 파일 중 매칭되는 파일 찾기 (filename == song['file'] already handled)
        # find a file that was assigned (by previous steps) which is different
        assigned = None
        for fi in file_info:
            if normalize_text(fi["filename"].rsplit('.',1)[0]) == normalize_text(song.get("title","")):
                assigned = fi["filename"]
                break
        # fallback: find any file that was used for this song in matching pass
        candidates = [fi["filename"] for fi in file_info if song.get("title") and normalize_text(song.get("title")) in fi["norm"]]
        if candidates:
            assigned = candidates[0]
        if assigned:
            src = os.path.join(OUTPUT_DIR, assigned)
            dst = os.path.join(OUTPUT_DIR, expected_fn)
            # 안전하게 이동 (덮어쓰기 방지)
            if os.path.exists(dst):
                print(f"⚠️ 리네임 스킵(대상존재): {dst}")
                continue
            try:
                shutil.move(src, dst)
                print(f"🔁 파일명 변경: {assigned} -> {expected_fn}")
            except Exception as e:
                print(f"❌ 리네임 실패: {src} -> {dst} ({e})")

# 마지막: metadata.json 덮어쓰기 (갱신)
with open(META_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("\n완료: metadata.json 업데이트됨.")
print("매칭 실패 항목은 unmatched.json에서 확인하세요.")
