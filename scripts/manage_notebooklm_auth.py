#!/usr/bin/env python3
"""Manage NotebookLM Authentication, Cookie Rotation & Keepalive.

Provides operational commands to check, rotate, import, and monitor
Google NotebookLM session credentials automatically.

Usage:
    python3 scripts/manage_notebooklm_auth.py check [--test]
    python3 scripts/manage_notebooklm_auth.py refresh
    python3 scripts/manage_notebooklm_auth.py import <cookie_file.json>
    python3 scripts/manage_notebooklm_auth.py keepalive [--interval 900]
"""

import argparse
import json
import os
from pathlib import Path
import sys
import time
import requests

BRIDGE_URL = os.getenv("BRIDGE_URL", "http://localhost:8010")


def print_banner():
    print("=" * 65)
    print("  TRADING PODCAST STUDIO — NotebookLM Authentication Manager")
    print("=" * 65)


def cmd_check(args):
    test_token = getattr(args, "test", False)
    print(f"\n[*] Querying NotebookLM auth status from Bridge ({BRIDGE_URL})...")
    if test_token:
        print("    [Info] --test specified: Testing live token against Google backend...")

    try:
        res = requests.get(f"{BRIDGE_URL}/api/notebooklm/auth/status", params={"test_token": test_token}, timeout=30)
        if res.status_code != 200:
            print(f"[!] Bridge returned HTTP {res.status_code}: {res.text}")
            return 1

        data = res.json()
        status = data.get("status", "unknown").upper()
        auth = data.get("authenticated", False)
        token_valid = data.get("token_valid")
        cookies_count = data.get("cookies_count", 0)
        has_psidts = data.get("has_psidts", False)
        email = data.get("account_email") or "(Not detected / Default)"
        keepalive = data.get("keepalive", {})

        print(f"\n[+] Auth Status     : {status}")
        print(f"    Account Email   : {email}")
        print(f"    Storage Exists  : {data.get('storage_exists')}")
        print(f"    Cookies Present : {auth} ({cookies_count} cookies loaded)")
        print(f"    __Secure-1PSIDTS: {has_psidts} (Rotation anchor)")

        if token_valid is not None:
            token_display = "VALID (Active)" if token_valid else "EXPIRED / INVALID"
            print(f"    Google Live Test: {token_display}")

        if data.get("error"):
            print(f"\n[!] Notice / Error  :\n    {data.get('error')}")

        print("\n--- Keepalive Daemon State ---")
        print(f"    Active in Bridge: {keepalive.get('task_active')}")
        print(f"    Daemon Enabled  : {keepalive.get('enabled')}")
        print(f"    Interval        : {keepalive.get('interval_seconds')} seconds")
        print(f"    Last Run        : {keepalive.get('last_run') or 'Never'}")
        print(f"    Last Result     : {keepalive.get('last_status') or 'Pending'}")

        if status == "VALID":
            print("\n[SUCCESS] NotebookLM session is authenticated and operational.")
            return 0
        else:
            print("\n[WARNING] NotebookLM session is expired or requires refresh/login.")
            return 2

    except requests.exceptions.ConnectionError:
        print(f"[!] Could not connect to Bridge service at {BRIDGE_URL}.")
        print("    Make sure trading-podcast-bridge Docker container is running.")
        return 1


def cmd_refresh(args):
    print(f"\n[*] Triggering Google cookie rotation via Bridge ({BRIDGE_URL})...")
    try:
        res = requests.post(f"{BRIDGE_URL}/api/notebooklm/auth/refresh", json={"verify": True}, timeout=35)
        if res.status_code != 200:
            print(f"[!] Bridge returned HTTP {res.status_code}: {res.text}")
            return 1

        data = res.json()
        st = data.get("status")
        msg = data.get("message")
        if st == "success":
            print(f"[+] SUCCESS: {msg}")
            print("    Google cookies successfully rotated and synced back to storage_state.json.")
            return 0
        else:
            print(f"[!] FAILED: {msg or data.get('error')}")
            print("    The current token has expired past Google's grace period.")
            print("    Please import fresh cookies or run 'notebooklm login'.")
            return 2

    except requests.exceptions.ConnectionError:
        print(f"[!] Could not connect to Bridge service at {BRIDGE_URL}.")
        return 1


def cmd_import(args):
    target = args.file_or_json
    print(f"\n[*] Preparing cookie import from: {target}...")

    raw_data = None
    if target == "-" or not target:
        print("    Reading JSON payload from standard input...")
        raw_data = sys.stdin.read().strip()
    elif Path(target).exists():
        print(f"    Reading file: {target}")
        raw_data = Path(target).read_text(encoding="utf-8")
    else:
        raw_data = target

    try:
        parsed = json.loads(raw_data)
    except Exception as e:
        print(f"[!] Failed parsing input as valid JSON: {e}")
        return 1

    print(f"[*] Sending payload to {BRIDGE_URL}/api/notebooklm/auth/import-cookies...")
    try:
        res = requests.post(f"{BRIDGE_URL}/api/notebooklm/auth/import-cookies", json={"cookies": parsed}, timeout=30)
        if res.status_code != 200:
            print(f"[!] Bridge returned HTTP {res.status_code}: {res.text}")
            return 1

        data = res.json()
        if data.get("status") == "success":
            print(f"[+] SUCCESS: {data.get('message')}")
            ver = data.get("verification", {})
            print(f"    Live Test Status: {ver.get('status')}")
            print(f"    Account Email   : {ver.get('account_email') or 'Default'}")
            print("    Storage state and profile successfully updated and synchronized.")
            return 0
        else:
            print(f"[!] Import failed: {data.get('message')}")
            return 2
    except requests.exceptions.ConnectionError:
        print(f"[!] Could not connect to Bridge service at {BRIDGE_URL}.")
        return 1


def cmd_keepalive(args):
    interval = args.interval
    print(f"\n[*] Starting standalone keepalive loop (interval={interval}s)...")
    print("    Press Ctrl+C to stop.")
    while True:
        try:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Triggering cookie rotation...")
            res = requests.post(f"{BRIDGE_URL}/api/notebooklm/auth/refresh", json={"verify": True}, timeout=35)
            if res.status_code == 200:
                data = res.json()
                print(f"    Status: {data.get('status')} | {data.get('message')}")
            else:
                print(f"    HTTP {res.status_code}: {res.text}")
        except Exception as e:
            print(f"    Error during keepalive tick: {e}")

        time.sleep(interval)


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="NotebookLM Authentication & Keepalive Manager")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # check
    p_check = subparsers.add_parser("check", help="Check Google auth status and credentials")
    p_check.add_argument("--test", action="store_true", help="Perform active live token test with Google")

    # refresh
    subparsers.add_parser("refresh", help="Force Google cookie rotation keepalive")

    # import
    p_import = subparsers.add_parser("import", help="Import cookies from file or JSON string")
    p_import.add_argument("file_or_json", help="Path to cookie JSON file, raw JSON string, or '-' for stdin")

    # keepalive
    p_keepalive = subparsers.add_parser("keepalive", help="Run standalone keepalive monitor")
    p_keepalive.add_argument("--interval", type=int, default=900, help="Interval in seconds (default: 900)")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "check":
        sys.exit(cmd_check(args))
    elif args.subcommand == "refresh":
        sys.exit(cmd_refresh(args))
    elif args.subcommand == "import":
        sys.exit(cmd_import(args))
    elif args.subcommand == "keepalive":
        sys.exit(cmd_keepalive(args))


if __name__ == "__main__":
    main()
