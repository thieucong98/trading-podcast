#!/usr/bin/env python3
"""
Antigravity Cross-Platform Session Restorer
Restores Antigravity chat sessions, transcripts, artifacts, and summary registry
onto any local machine (Windows, Linux, macOS, WSL) so you can seamlessly resume conversations.
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


def get_target_antigravity_dirs():
    """
    Auto-detect all Antigravity application directories on the host machine.
    Supports Antigravity IDE, Antigravity CLI, and cross-mount WSL paths.
    """
    candidates = []
    home = Path.home()

    # Standard locations relative to user home
    known_subdirs = ["antigravity-ide", "antigravity", "antigravity-cli"]
    for sub in known_subdirs:
        p = home / ".gemini" / sub
        if p.exists() and p not in candidates:
            candidates.append(p)

    # In WSL, also check Windows host user profile if mounted
    if sys.platform != "win32":
        mnt_c_users = Path("/mnt/c/Users")
        if mnt_c_users.exists():
            for user_dir in mnt_c_users.iterdir():
                if user_dir.is_dir() and not user_dir.name.startswith((".", "Public", "Default")):
                    for sub in known_subdirs:
                        wp = user_dir / ".gemini" / sub
                        if wp.exists() and wp not in candidates:
                            candidates.append(wp)

    # Fallback if no profile exists yet
    if not candidates:
        default_dir = home / ".gemini" / ("antigravity-ide" if sys.platform == "win32" else "antigravity-cli")
        candidates.append(default_dir)

    return candidates


def compute_workspace_uri(target_dir: Path):
    """
    Computes a workspace URI suitable for the target environment.
    """
    # If target is on Windows mount or Windows native
    is_windows_target = "Users" in str(target_dir) or sys.platform == "win32"
    
    posix_path = PROJECT_ROOT.as_posix()
    if is_windows_target:
        # Normalize to Windows URI format: file:///d:/Project/...
        if not posix_path.startswith("/"):
            posix_path = "/" + posix_path
        return f"file://{posix_path}"
    else:
        return f"file://{PROJECT_ROOT}"


def restore_conversations():
    if not SOURCE_CONV_DIR.exists():
        print(f"[ERROR] Source conversations directory not found: {SOURCE_CONV_DIR}")
        sys.exit(1)

    target_dirs = get_target_antigravity_dirs()
    print("=" * 70)
    print("ANTIGRAVITY CROSS-PLATFORM SESSION RESTORER")
    print("=" * 70)
    print(f"Project Source: {PROJECT_ROOT}")
    print(f"Detected {len(target_dirs)} Antigravity environment(s):")
    for t in target_dirs:
        print(f"  -> {t}")
    print("-" * 70)

    all_restored = []

    for app_data_dir in target_dirs:
        print(f"\n[+] Restoring into target: {app_data_dir}")
        dest_conv_dir = app_data_dir / "conversations"
        dest_brain_dir = app_data_dir / "brain"
        dest_summaries_db = app_data_dir / "conversation_summaries.db"

        dest_conv_dir.mkdir(parents=True, exist_ok=True)
        dest_brain_dir.mkdir(parents=True, exist_ok=True)

        # 1. Restore SQLite DBs
        for db_file in SOURCE_CONV_DIR.glob("*.db"):
            dest_file = dest_conv_dir / db_file.name
            print(f"  [+] SQLite session: {db_file.name}")
            shutil.copy2(db_file, dest_file)
            if db_file.stem not in all_restored:
                all_restored.append(db_file.stem)

        # 2. Restore Brain Artifacts & Transcripts
        if SOURCE_BRAIN_DIR.exists():
            for b_dir in SOURCE_BRAIN_DIR.iterdir():
                if b_dir.is_dir():
                    dest_b = dest_brain_dir / b_dir.name
                    print(f"  [+] Brain logs & artifacts: {b_dir.name}")
                    shutil.copytree(b_dir, dest_b, dirs_exist_ok=True)

        # 3. Register in conversation_summaries.db
        current_workspace_uri = compute_workspace_uri(app_data_dir)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        try:
            conn = sqlite3.connect(dest_summaries_db)
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

            if SOURCE_SUMMARIES.exists():
                with open(SOURCE_SUMMARIES, "r", encoding="utf-8") as f:
                    summaries = json.load(f)
                for s in summaries:
                    cid = s.get("conversation_id")
                    title = s.get("title", "Trading Podcast Session")
                    preview = s.get("preview", "")
                    step_count = s.get("step_count", 100)

                    workspace_json = json.dumps([current_workspace_uri])

                    cur.execute("""
                        INSERT OR REPLACE INTO conversation_summaries (
                            conversation_id, title, preview, step_count, last_modified_time,
                            workspace_uris, last_user_input_time, app_data_dir
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cid, title, preview, step_count, now_iso,
                        workspace_json, now_iso, str(app_data_dir)
                    ))
                    print(f"  [+] Registered summary: '{title}' ({cid})")

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"  [!] Note on summary DB ({dest_summaries_db.name}): {e}")

    print("\n" + "=" * 70)
    print("SUCCESS: All Antigravity sessions have been restored successfully!")
    print("=" * 70)
    print("Restored Sessions:")
    for cid in all_restored:
        print(f"  - Session ID: {cid}")
        print(f"    Resume Command: agy --resume {cid}")
    print("\nAntigravity IDE:")
    print("  You can now open Antigravity IDE and access the conversations")
    print("  directly from your chat history / session switcher.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    restore_conversations()
