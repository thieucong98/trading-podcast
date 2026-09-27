#!/usr/bin/env python3
"""
Antigravity Session Exporter & Sanitizer
Exports, redacts sensitive keys, and packages Antigravity chat sessions into .antigravity/
and generates readable Markdown logs in docs/chat_history/.
"""

import os
import re
import json
import shutil
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAIN_SRC_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"
CONV_SRC_DIR = Path.home() / ".gemini" / "antigravity-cli" / "conversations"
SUMMARIES_SRC_DB = Path.home() / ".gemini" / "antigravity-cli" / "conversation_summaries.db"

TARGET_ANTIGRAVITY_DIR = PROJECT_ROOT / ".antigravity"
TARGET_CONV_DIR = TARGET_ANTIGRAVITY_DIR / "conversations"
TARGET_BRAIN_DIR = TARGET_ANTIGRAVITY_DIR / "brain"
TARGET_DOCS_DIR = PROJECT_ROOT / "docs" / "chat_history"

TARGET_CONV_DIR.mkdir(parents=True, exist_ok=True)
TARGET_BRAIN_DIR.mkdir(parents=True, exist_ok=True)
TARGET_DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Conversation IDs for trading-podcast
CONVERSATIONS = [
    {
        "id": "dc80f4a9-5ff0-4d5e-9a80-ffa4d985f271",
        "title": "Trading Podcast n8n Workflow & NotebookLM Foundation",
        "md_filename": "01_trading_podcast_notebooklm_session.md",
    },
    {
        "id": "d7d40cd3-2a98-4270-99bf-102cbafd0350",
        "title": "YouTube Faceless Video Studio v3.0 Ultra (Veo 3, Shorts, Trend Radar)",
        "md_filename": "02_youtube_studio_v3_session.md",
    },
]

# Sensitive regex patterns to sanitize
SANITIZE_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk-REDACTED-OPENAI-KEY"),
    (re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"), "AIzaSy-REDACTED-GOOGLE-KEY"),
    (re.compile(r"fal_[A-Za-z0-9_-]{20,}"), "fal-REDACTED-FAL-KEY"),
    (re.compile(r"fal-[A-Za-z0-9_-]{20,}"), "fal-REDACTED-FAL-KEY"),
    (re.compile(r"Bearer\s+[A-Za-z0-9_.-]{25,}"), "Bearer REDACTED-BEARER-TOKEN"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{30,}"), "github_pat_REDACTED_TOKEN"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"), "ghp_REDACTED_TOKEN"),
    (re.compile(r'"sid":\s*"[^"]+"'), '"sid": "REDACTED_COOKIE_SID"'),
    (re.compile(r'"value":\s*"[A-Za-z0-9_.-]{25,}"'), '"value": "REDACTED_COOKIE_VALUE"'),
    (re.compile(r'sidts-[A-Za-z0-9_-]{30,}'), 'sidts-REDACTED_COOKIE_TOKEN'),
    (re.compile(r'(Aaa9EJ[A-Za-z0-9_-]+|ANmZwa[A-Za-z0-9_-]+|AKEyXz[A-Za-z0-9_-]+)'), 'REDACTED_COOKIE_TOKEN'),
    (re.compile(r'TradingPodcast2026!?'), 'YourSecurePasswordHere!'),
    (re.compile(r'("password"\s*:\s*)"[^"]+"'), r'\1"REDACTED_PASSWORD"'),
    (re.compile(r'data:image\/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]{100,}'), 'data:image/png;base64,[STRIPPED_IMAGE_BASE64]'),
]

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    for pattern, repl in SANITIZE_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def export_and_sanitize_sqlite(conv_id: str):
    src_db = CONV_SRC_DIR / f"{conv_id}.db"
    dst_db = TARGET_CONV_DIR / f"{conv_id}.db"
    if not src_db.exists():
        print(f"[WARN] DB not found: {src_db}")
        return

    print(f"Processing and repairing SQLite DB: {src_db.name} -> {dst_db.name}")
    if dst_db.exists():
        dst_db.unlink()

    src_conn = sqlite3.connect(src_db)
    src_cur = src_conn.cursor()
    src_cur.execute("PRAGMA writable_schema = ON;")

    dst_conn = sqlite3.connect(dst_db)
    dst_cur = dst_conn.cursor()

    # Recreate tables
    src_cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")
    for (s,) in src_cur.fetchall():
        try:
            dst_cur.execute(s)
        except Exception:
            pass
    dst_conn.commit()

    # Recover & sanitize table rows
    src_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in src_cur.fetchall()]
    total_recovered = 0

    for table in tables:
        src_cur.execute(f"PRAGMA table_info(`{table}`)")
        cols = [c[1] for c in src_cur.fetchall()]
        cols_str = ", ".join(f"`{c}`" for c in cols)
        placeholders = ", ".join("?" for _ in cols)
        
        # Scan rowids up to 4000
        for rid in range(1, 4000):
            try:
                src_cur.execute(f"SELECT {cols_str} FROM `{table}` WHERE rowid={rid}")
                row = src_cur.fetchone()
                if row:
                    sanitized_row = []
                    for val in row:
                        if val is None:
                            sanitized_row.append(None)
                        elif isinstance(val, (bytes, bytearray)):
                            val_str = val.decode("utf-8", errors="ignore")
                            s_str = sanitize_text(val_str)
                            sanitized_row.append(s_str.encode("utf-8") if s_str != val_str else val)
                        elif isinstance(val, str):
                            sanitized_row.append(sanitize_text(val))
                        else:
                            sanitized_row.append(val)
                    dst_cur.execute(f"INSERT INTO `{table}` ({cols_str}) VALUES ({placeholders})", sanitized_row)
                    total_recovered += 1
            except Exception:
                continue
        dst_conn.commit()

    # Recreate indices
    src_cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
    for (idx_sql,) in src_cur.fetchall():
        try:
            dst_cur.execute(idx_sql)
        except Exception:
            pass
    dst_conn.commit()

    dst_cur.execute("PRAGMA integrity_check;")
    check = dst_cur.fetchall()
    print(f"  Sanitized & recovered {total_recovered} rows in {dst_db.name}. Integrity: {check}")
    dst_cur.execute("VACUUM")
    src_conn.close()
    dst_conn.close()


def export_and_sanitize_brain(conv_id: str, md_filename: str, session_title: str):
    src_brain = BRAIN_SRC_DIR / conv_id
    dst_brain = TARGET_BRAIN_DIR / conv_id
    if not src_brain.exists():
        print(f"[WARN] Brain dir not found: {src_brain}")
        return

    print(f"Packaging brain artifacts: {conv_id}")
    dst_logs = dst_brain / ".system_generated" / "logs"
    dst_logs.mkdir(parents=True, exist_ok=True)

    # Copy & sanitize transcript.jsonl
    src_transcript = src_brain / ".system_generated" / "logs" / "transcript.jsonl"
    dst_transcript = dst_logs / "transcript.jsonl"
    
    dialogues = []
    if src_transcript.exists():
        with open(src_transcript, "r", encoding="utf-8") as infile, \
             open(dst_transcript, "w", encoding="utf-8") as outfile:
            for line in infile:
                sanitized_line = sanitize_text(line)
                outfile.write(sanitized_line)
                try:
                    obj = json.loads(sanitized_line)
                    source = obj.get("source")
                    msg_type = obj.get("type")
                    content = obj.get("content", "")
                    if msg_type == "USER_INPUT" and content:
                        dialogues.append({"role": "User", "content": sanitize_text(content), "time": obj.get("created_at", "")})
                    elif source == "MODEL" and msg_type == "PLANNER_RESPONSE" and content:
                        dialogues.append({"role": "Antigravity (Agent)", "content": sanitize_text(content), "time": obj.get("created_at", "")})
                except Exception:
                    pass

    # Copy top-level artifacts
    for item in src_brain.glob("*"):
        if item.is_file() and not item.name.startswith("."):
            shutil.copy2(item, dst_brain / item.name)

    # Generate Markdown documentation
    out_md = TARGET_DOCS_DIR / md_filename
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(f"# Antigravity Chat Transcript: {session_title}\n\n")
        f.write(f"- **Session ID**: `{conv_id}`\n")
        f.write(f"- **Total Key Dialogue Turns**: {len(dialogues)}\n\n---\n\n")
        for i, turn in enumerate(dialogues, 1):
            role = turn["role"]
            time = turn["time"]
            content = turn["content"]
            f.write(f"### Turn {i}: {role} ({time})\n\n")
            f.write(f"{content.strip()}\n\n---\n\n")
    print(f"  Generated Markdown transcript: {out_md.name} ({len(dialogues)} turns)")


def export_summaries():
    summaries_file = TARGET_ANTIGRAVITY_DIR / "summaries.json"
    if not SUMMARIES_SRC_DB.exists():
        return
    conn = sqlite3.connect(SUMMARIES_SRC_DB)
    cur = conn.cursor()
    ids = [c["id"] for c in CONVERSATIONS]
    placeholders = ",".join("?" for _ in ids)
    cur.execute(f"SELECT conversation_id, title, preview, step_count, last_modified_time, workspace_uris FROM conversation_summaries WHERE conversation_id IN ({placeholders})", ids)
    rows = cur.fetchall()
    summaries = []
    for r in rows:
        summaries.append({
            "conversation_id": r[0],
            "title": r[1],
            "preview": r[2],
            "step_count": r[3],
            "last_modified_time": r[4],
            "workspace_uris": r[5],
        })
    with open(summaries_file, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(summaries)} session summaries to {summaries_file.name}")
    conn.close()


def generate_index_readme():
    readme_path = TARGET_DOCS_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("""# Antigravity Historical Chat Archive

Tài liệu này lưu trữ toàn bộ lịch sử trao đổi, nghiên cứu giải pháp, và các bước triển khai của hệ thống Antigravity cho dự án **Trading Podcast & YouTube Studio**.

## 1. Danh Sách Các Phiên Làm Việc (Chat Sessions)

| Phiên | Session ID | Chủ đề | Bản Đọc Trực Quan |
| :--- | :--- | :--- | :--- |
| **01** | `dc80f4a9-5ff0-4d5e-9a80-ffa4d985f271` | Nền móng Trading Podcast, LangGraph & NotebookLM | [01_trading_podcast_notebooklm_session.md](./01_trading_podcast_notebooklm_session.md) |
| **02** | `d7d40cd3-2a98-4270-99bf-102cbafd0350` | Xây dựng YouTube Faceless Studio v3.0 Ultra | [02_youtube_studio_v3_session.md](./02_youtube_studio_v3_session.md) |

## 2. Cách Khôi Phục & Tiếp Tục Chat (Resume) Trên Máy Khác

1. Chạy script khôi phục tự động:
   ```bash
   python3 scripts/restore_antigravity.py
   ```
2. Resume phiên làm việc mong muốn:
   ```bash
   # Tiếp tục phiên YouTube Studio v3.0 Ultra
   agy --resume d7d40cd3-2a98-4270-99bf-102cbafd0350

   # Hoặc mở Antigravity IDE và chọn phiên trong danh sách Chat History
   ```
""")
    print(f"Generated index: {readme_path.name}")


if __name__ == "__main__":
    print("Starting Antigravity Export & Sanitization Pipeline...")
    for conv in CONVERSATIONS:
        export_and_sanitize_sqlite(conv["id"])
        export_and_sanitize_brain(conv["id"], conv["md_filename"], conv["title"])
    export_summaries()
    generate_index_readme()
    print("\nAntigravity Export & Sanitization Completed Successfully!")
