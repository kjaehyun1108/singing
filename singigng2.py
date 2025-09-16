import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import sounddevice as sd
import soundfile as sf
import numpy as np

OUTPUT_DIR = "karaoke_dataset"
META_FILE = os.path.join(OUTPUT_DIR, "metadata.json")

# metadata 불러오기
if os.path.exists(META_FILE):
    with open(META_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
else:
    metadata = []

# ==== 간단한 곡 검색 함수 ====
def search_song(query):
    results = []
    query_lower = query.lower()
    for song in metadata:
        if query_lower in song["title"].lower() or query_lower in song["artist"].lower():
            results.append(song)
    return results

# ==== 녹음 함수 ====
def record_song(duration=15, fs=44100):
    print("🎤 녹음 시작...")
    recording = sd.rec(int(duration*fs), samplerate=fs, channels=1)
    sd.wait()
    print("✅ 녹음 종료")
    return recording, fs

# ==== 단순 비교 점수 예시 (피치/크로마 등 고급 알고리즘 가능) ====
def score_recording(user_audio, fs, target_file):
    # 여기서는 단순 RMS 차이로 임시 점수
    target, _ = sf.read(target_file)
    min_len = min(len(target), len(user_audio))
    target = target[:min_len]
    user_audio = user_audio[:min_len]
    score = max(0, 100 - np.abs(np.mean(target) - np.mean(user_audio))*1000)
    return round(score,1)

# ==== Tkinter UI ====
root = tk.Tk()
root.title("Karaoke Search & Score")

# 검색창
search_entry = tk.Entry(root, width=40)
search_entry.grid(row=0, column=0, padx=5, pady=5)
search_button = tk.Button(root, text="검색")
search_button.grid(row=0, column=1, padx=5, pady=5)

# 검색 결과 Listbox
result_listbox = tk.Listbox(root, width=60, height=10)
result_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# 녹음 + 점수 버튼
def start_singing():
    selection = result_listbox.curselection()
    if not selection:
        messagebox.showinfo("알림", "곡을 선택하세요")
        return
    idx = selection[0]
    song = current_results[idx]
    target_file = os.path.join(OUTPUT_DIR, song["file"])
    if not os.path.exists(target_file):
        messagebox.showerror("오류", f"곡 파일이 없습니다: {target_file}")
        return

    # 녹음
    duration = simpledialog.askinteger("녹음 길이", "녹음 길이(초):", minvalue=5, maxvalue=60)
    if not duration:
        return
    user_audio, fs = record_song(duration=duration)

    # 점수 계산
    score = score_recording(user_audio, fs, target_file)
    messagebox.showinfo("점수", f"{song['artist']} - {song['title']}\n점수: {score}점")

sing_button = tk.Button(root, text="노래 시작!", command=start_singing)
sing_button.grid(row=2, column=0, columnspan=2, pady=10)

# 검색 버튼 이벤트
current_results = []
def do_search():
    global current_results
    query = search_entry.get()
    current_results = search_song(query)
    result_listbox.delete(0, tk.END)
    for song in current_results:
        result_listbox.insert(tk.END, f"{song['artist']} - {song['title']}")

search_button.config(command=do_search)

root.mainloop()
