#!/usr/bin/env python3
"""
Antigravity Cross-Machine Session Restorer
Restores Antigravity chat sessions, transcripts, artifacts, and summary registry
onto any local machine so you can seamlessly resume conversations.
"""

import os
import sys
import json
import shutil
import sqlite3
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_ANTIGRAVITY_DIR = PROJECT_ROOT / ".antigravity"
SOURCE_CONV_DIR = SOURCE_ANTIGRAVITY_DIR / "conversations"
SOURCE_BRAIN_DIR = SOURCE_ANTIGRAVITY_DIR / "brain"
SOURCE_SUMMARIES = SOURCE_ANTIGRAVITY_DIR / "summaries.json"

# Destination directories on the host machine
APP_DATA_DIR = Path.home() / ".gemini" / "antigravity-cli"
DEST_CONV_DIR = APP_DATA_DIR / "conversations"
DEST_BRAIN_DIR = APP_DATA_DIR / "brain"
DEST_SUMMARIES_DB = APP_DATA_DIR / "conversation_summaries.db"


def restore_conversations():
    if not SOURCE_CONV_DIR.exists():
        print(f"[ERROR] Source conversations directory not found: {SOURCE_CONV_DIR}")
        sys.exit(1)

    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DEST_CONV_DIR.mkdir(parents=True, exist_ok=True)
    DEST_BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--> Target Antigravity Data Directory: {APP_DATA_DIR}")

    # 1. Restore SQLite DBs
    restored_convs = []
    for db_file in SOURCE_CONV_DIR.glob("*.db"):
        dest_file = DEST_CONV_DIR / db_file.name
        print(f"  [+] Restoring SQLite session: {db_file.name}")
        shutil.copy2(db_file, dest_file)
        restored_convs.append(db_file.stem)

    # 2. Restore Brain Artifacts & Transcripts
    if SOURCE_BRAIN_DIR.exists():
        for b_dir in SOURCE_BRAIN_DIR.iterdir():
            if b_dir.is_dir():
                dest_b = DEST_BRAIN_DIR / b_dir.name
                print(f"  [+] Restoring brain directory: {b_dir.name}")
                shutil.copytree(b_dir, dest_b, dirs_exist_ok=True)

    # 3. Register in conversation_summaries.db
    print("  [+] Updating conversation registry...")
    conn = sqlite3.connect(DEST_SUMMARIES_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS `conversation_summaries` (
            `conversation_id` text,
            `title` text NOT NULL DEFAULT "",
            `preview` text NOT NULL DEFAULT "",
            `step_count` integer NOT NULL DEFAULT 0,
            `last_modified_time` datetime NOT NULL,
            `workspace_uris` text NOT NULL,
            `status` text NOT NULL DEFAULT "",
            `source` text NOT NULL DEFAULT "",
            `project_id` text NOT NULL DEFAULT "",
            `agent_name` text NOT NULL DEFAULT "",
            `parent_conversation_id` text NOT NULL DEFAULT "",
            `nesting_depth` integer NOT NULL DEFAULT 0,
            `battle_id` text NOT NULL DEFAULT "",
            `winning_conversation_id` text NOT NULL DEFAULT "",
            `not_fully_idle` numeric NOT NULL DEFAULT false,
            `killed` numeric NOT NULL DEFAULT false,
            `last_user_input_time` datetime NOT NULL,
            `last_user_input_step_index` integer NOT NULL DEFAULT -1,
            `app_data_dir` text NOT NULL DEFAULT "",
            `raw_summary` blob,
            `group_id` text NOT NULL DEFAULT "",
            PRIMARY KEY (`conversation_id`)
        )
    """)

    current_workspace_uri = f"file://{PROJECT_ROOT}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if SOURCE_SUMMARIES.exists():
        with open(SOURCE_SUMMARIES, "r", encoding="utf-8") as f:
            summaries = json.load(f)
        for s in summaries:
            cid = s.get("conversation_id")
            title = s.get("title", "Trading Podcast Session")
            preview = s.get("preview", "")
            step_count = s.get("step_count", 100)
            
            cur.execute("""
                INSERT OR REPLACE INTO conversation_summaries (
                    conversation_id, title, preview, step_count, last_modified_time,
                    workspace_uris, last_user_input_time, app_data_dir
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cid, title, preview, step_count, now_iso,
                current_workspace_uri, now_iso, str(APP_DATA_DIR)
            ))
            print(f"    Registered session: '{title}' ({cid})")

    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print("SUCCESS: All Antigravity sessions have been restored on this machine!")
    print("=" * 70)
    print("To resume any session, run the following in terminal:")
    for cid in restored_convs:
        print(f"  agy --resume {cid}")
    print("\nOr open the Antigravity IDE to view and continue your chat sessions.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    restore_conversations()
