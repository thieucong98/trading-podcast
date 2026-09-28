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

        mt_present = data.get("master_token_present", False)
        mt_info = data.get("master_token", {})

        print(f"\n[+] Auth Status     : {status}")
        print(f"    Account Email   : {email}")
        print(f"    Storage Exists  : {data.get('storage_exists')}")
        print(f"    Cookies Present : {auth} ({cookies_count} cookies loaded)")
        print(f"    __Secure-1PSIDTS: {has_psidts} (Rotation anchor)")
        print(f"    Master Token    : {'ACTIVE (Headless Auto-Mint Enabled)' if mt_present else 'None (Manual cookie mode)'}")
        if mt_info.get("email"):
            print(f"    Master Account  : {mt_info.get('email')}")

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


def cmd_bootstrap(args):
    email = args.email
    oauth_token = args.oauth_token
    cdp_url = args.cdp_url

    print("\n" + "=" * 65)
    print("  GOOGLE MASTER TOKEN HEADLESS BOOTSTRAP (1-TIME SETUP)")
    print("=" * 65)

    if not email:
        print("\n[?] Nhập địa chỉ Gmail Google của bạn (ví dụ: tradingbot@gmail.com):")
        email = input("    Email: ").strip()

    if not email or "@" not in email:
        print("[!] Email không hợp lệ. Đã hủy.")
        return 1

    if not oauth_token and not cdp_url:
        print("\n--- HƯỚNG DẪN LẤY OAUTH TOKEN (CHỈ CẦN LÀM 1 LẦN DUY NHẤT) ---")
        print("1. Mở trình duyệt Google Chrome trên máy tính của bạn.")
        print("2. Truy cập địa chỉ sau và đăng nhập tài khoản Google của bạn:")
        print("   👉  https://accounts.google.com/EmbeddedSetup")
        print("3. Sau khi đăng nhập xong, mở DevTools (bấm F12 hoặc chuột phải chọn Inspect):")
        print("   -> Vào tab 'Application' (hoặc 'Bộ nhớ lưu trữ')")
        print("   -> Bên cột trái chọn: Storage -> Cookies -> https://accounts.google.com")
        print("   -> Tìm dòng có tên cookie là: oauth_token")
        print("   -> Copy toàn bộ chuỗi giá trị (Value) của oauth_token.")
        print("4. Dán giá trị 'oauth_token' vừa copy vào bên dưới:")
        try:
            oauth_token = input("    oauth_token: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Đã hủy thao tác.")
            return 1

    payload = {"email": email}
    if oauth_token:
        payload["oauth_token"] = oauth_token
    if cdp_url:
        payload["cdp_url"] = cdp_url

    print(f"\n[*] Gửi yêu cầu khởi tạo Master Token tới Bridge ({BRIDGE_URL})...")
    try:
        res = requests.post(
            f"{BRIDGE_URL}/api/notebooklm/auth/master-token/bootstrap",
            json=payload,
            timeout=60,
        )
        data = res.json()
        if res.status_code == 200 and data.get("status") == "success":
            print("\n[+] THÀNH CÔNG RỰC RỠ! 🎉")
            print(f"    Tài khoản : {email}")
            print("    Google Master Token đã được tạo và lưu trữ an toàn (0600).")
            print("    Từ bây giờ, hệ thống sẽ TỰ ĐỘNG sinh mới cookie (storage_state.json) ngầm vĩnh viễn!")
            print("    Bạn KHÔNG BAO GIỜ cần phải copy cookie thủ công nữa!")
            return 0
        else:
            print(f"\n[!] Thất bại: {data.get('detail') or data.get('message')}")
            return 2
    except requests.exceptions.ConnectionError:
        print(f"[!] Không thể kết nối tới Bridge service tại {BRIDGE_URL}.")
        return 1


def cmd_remint(args):
    print(f"\n[*] Kích hoạt headless re-mint từ Google Master Token qua Bridge ({BRIDGE_URL})...")
    try:
        res = requests.post(f"{BRIDGE_URL}/api/notebooklm/auth/master-token/remint", timeout=45)
        if res.status_code == 200:
            data = res.json()
            print("[+] THÀNH CÔNG: Cookie mới đã được sinh ra từ Master Token và nạp vào storage_state.json!")
            print(f"    Chi tiết: {data.get('message')}")
            return 0
        else:
            print(f"[!] Lỗi ({res.status_code}): {res.text}")
            return 2
    except requests.exceptions.ConnectionError:
        print(f"[!] Không thể kết nối tới Bridge tại {BRIDGE_URL}.")
        return 1


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

    # bootstrap
    p_boot = subparsers.add_parser("bootstrap", help="Bootstrap durable Google Master Token (1-time setup)")
    p_boot.add_argument("--email", help="Google account email (e.g. tradingbot@gmail.com)")
    p_boot.add_argument("--oauth-token", help="Single-use EmbeddedSetup oauth_token cookie")
    p_boot.add_argument("--cdp-url", help="Optional Chrome DevTools Protocol endpoint (e.g. http://host.docker.internal:9222)")

    # remint
    subparsers.add_parser("remint", help="Force re-mint cookies headlessly from Master Token")

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
    elif args.subcommand == "bootstrap":
        sys.exit(cmd_bootstrap(args))
    elif args.subcommand == "remint":
        sys.exit(cmd_remint(args))


if __name__ == "__main__":
    main()
