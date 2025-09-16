import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

# === 설정 ===
OUTPUT_DIR = "karaoke_dataset"
META_FILE = os.path.join(OUTPUT_DIR, "metadata.json")

# 메타데이터 불러오기
with open(META_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# 검색 함수
def search_songs():
    query = entry.get().lower()
    results.delete(*results.get_children())

    for song in metadata:
        if query in song["title"].lower() or query in song["artist"].lower():
            results.insert("", "end", values=(song["index"], song["title"], song["artist"], song["file"]))

# 선택한 곡 재생
def play_song():
    selected = results.focus()
    if not selected:
        messagebox.showwarning("선택 필요", "곡을 선택하세요!")
        return
    values = results.item(selected, "values")
    filepath = os.path.join(OUTPUT_DIR, values[3])
    if os.path.exists(filepath):
        # OS 기본 플레이어로 실행 (Windows: start, Mac: open, Linux: xdg-open)
        if os.name == "nt":  # Windows
            os.startfile(filepath)
        elif os.name == "posix":  # Linux/Mac
            subprocess.Popen(["xdg-open", filepath])
        else:
            messagebox.showerror("에러", "이 운영체제에서는 자동 실행이 지원되지 않습니다.")
    else:
        messagebox.showerror("파일 없음", f"{filepath} 파일이 존재하지 않습니다.")

# === Tkinter UI 구성 ===
root = tk.Tk()
root.title("🎤 AI Karaoke Song Selector")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="검색 (곡명 / 가수명):").grid(row=0, column=0, padx=5)
entry = tk.Entry(frame, width=40)
entry.grid(row=0, column=1, padx=5)
tk.Button(frame, text="검색", command=search_songs).grid(row=0, column=2, padx=5)

# 검색 결과 테이블
columns = ("번호", "제목", "가수", "파일")
results = ttk.Treeview(root, columns=columns, show="headings", height=15)
for col in columns:
    results.heading(col, text=col)
    results.column(col, width=150)
results.pack(pady=10, fill="both", expand=True)

# 버튼
tk.Button(root, text="선택 곡 재생 🎵", command=play_song).pack(pady=10)

root.mainloop()
