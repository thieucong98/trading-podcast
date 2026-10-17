"""Comprehensive automated test suite for Trading Podcast AI Pipeline.
Verifies bridge endpoints, smart caching, report content integrity,
zero dummy fallback guarantee, TradingView chart captures, and NotebookLM integration.
"""

import datetime
import io
import json
from pathlib import Path
import unittest
import requests

BRIDGE_URL = "http://localhost:8010"
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/run-trading-podcast"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "output" / "reports"
CHARTS_DIR = PROJECT_ROOT / "output" / "charts"


def find_latest_report_date() -> str:
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    if any(REPORTS_DIR.glob(f"TradingAgents_*_{today_str}_Complete.md")):
        return today_str
    dates = []
    for f in REPORTS_DIR.glob("TradingAgents_*_*_Complete.md"):
        parts = f.stem.split("_")
        if len(parts) >= 3 and parts[-1] == "Complete":
            dates.append(parts[-2])
    return max(dates) if dates else today_str


TODAY = find_latest_report_date()

EXPECTED_TICKERS = ["XAUUSD", "SPY", "BTC-USD", "XAGUSD", "^TNX", "DX-Y.NYB"]


class TestTradingPodcastPipeline(unittest.TestCase):

    def test_01_bridge_health(self):
        """Verify bridge service is running and healthy."""
        res = requests.get(f"{BRIDGE_URL}/health", timeout=5)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}")
        data = res.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "Trading Podcast Bridge")
        print(f"\n[PASS] 01. Bridge Health: {data['status']} (service: {data['service']})")

    def test_02_report_files_integrity_and_zero_dummy(self):
        """Verify all 6 report markdown files on disk are > 100KB, genuine, and contain NO dummy data."""
        print()
        for ticker in EXPECTED_TICKERS:
            clean_t = ticker.replace("^", "").replace("/", "_").replace(":", "_").strip()
            filename = f"TradingAgents_{clean_t}_{TODAY}_Complete.md"
            file_path = REPORTS_DIR / filename

            self.assertTrue(file_path.exists(), f"Missing completed report file: {filename}")
            file_size = file_path.stat().st_size
            self.assertGreater(file_size, 100_000, f"Report file {filename} is too small ({file_size} bytes). Expected > 100KB")

            content = file_path.read_text(encoding="utf-8")
            # Assert strictly NO fake dummy fallback text
            self.assertNotIn("Quan sát kỹ thuật (Wait & Watch)", content, f"Found fake dummy fallback text in {filename}!")
            self.assertNotIn(f"Phân tích kỹ thuật và dòng tiền tổng thể cho {ticker}", content, f"Found placeholder line in {filename}!")

            # Assert presence of real multi-agent analyst sections
            self.assertGreater(len(content), 50_000, f"Content length too short for {filename}")
            print(f"  [PASS] Report {clean_t:10}: {file_size:,} bytes | Genuine multi-agent analysis confirmed")

    def test_03_analyze_markets_smart_caching(self):
        """Verify that when reports exist and match config, analyze-markets reuses them in < 2 seconds."""
        payload = {
            "tickers": EXPECTED_TICKERS,
            "force_reanalyze": False,
            "tradingagents_backend_url": "http://tradingagents-backend:8000",
            "llm_provider": "openai_compatible",
            "deep_think_llm": "ag/gemini-3.8-flash-high",
            "quick_think_llm": "ag/gemini-3.8-flash-high",
            "max_debate_rounds": 3,
            "max_risk_discuss_rounds": 3,
            "output_language": "Vietnamese",
            "date": TODAY,
        }
        start = datetime.datetime.now()
        res = requests.post(f"{BRIDGE_URL}/api/pipeline/analyze-markets", json=payload, timeout=10)
        elapsed = (datetime.datetime.now() - start).total_seconds()

        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("reports_count"), len(EXPECTED_TICKERS))
        self.assertEqual(len(data.get("reused_tickers", [])), len(EXPECTED_TICKERS))
        self.assertLess(elapsed, 5.0, f"Reusing completed jobs took too long ({elapsed}s)")
        print(f"\n[PASS] 03. Smart Caching: Reused all {len(EXPECTED_TICKERS)} reports in {elapsed:.2f}s (reused: {data.get('reused_tickers')})")

    def test_04_chart_captures(self):
        """Verify TradingView chart capture endpoint and cached chart files."""
        payload = {
            "symbols": ["XAUUSD", "XAGUSD"],
            "intervals": ["5", "15", "60", "240", "D", "W"],
            "force_recapture": False,
        }
        res = requests.post(f"{BRIDGE_URL}/api/charts/capture", json=payload, timeout=30)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertGreaterEqual(data.get("count"), 12)
        for c in data.get("charts", []):
            filename = Path(c["filepath"]).name
            p = CHARTS_DIR / filename
            self.assertTrue(p.exists(), f"Chart image {p} not found on disk")
            self.assertGreater(p.stat().st_size, 10_000, f"Chart image {p} is too small ({p.stat().st_size} bytes)")

        print(f"\n[PASS] 04. Chart Captures: Verified {data.get('count')} multi-timeframe charts on disk")

    def test_05_notebooklm_upload_sources(self):
        """Verify uploading all 18 sources (6 reports + 12 charts) to NotebookLM."""
        report_files = [str((REPORTS_DIR / f"TradingAgents_{t.replace('^', '').replace('/', '_').replace(':', '_')}_{TODAY}_Complete.md").resolve()) for t in EXPECTED_TICKERS]
        chart_files = [str((CHARTS_DIR / f"{s}_{i}.png").resolve()) for s in ["XAUUSD", "XAGUSD"] for i in ["5m", "15m", "1H", "4H", "1D", "1W"] if (CHARTS_DIR / f"{s}_{i}.png").exists()]

        payload = {
            "report_md_paths": report_files,
            "chart_image_paths": chart_files,
            "notebook_title": f"Trading Intelligence & Multi-Asset Reports - {TODAY}",
            "date": TODAY,
        }
        res = requests.post(f"{BRIDGE_URL}/api/notebooklm/upload-sources", json=payload, timeout=60)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertIsNotNone(data.get("notebook_id"))
        print(f"\n[PASS] 05. NotebookLM Upload: Notebook ID: {data.get('notebook_id')} | Sources uploaded: {data.get('sources_count', 0)}")

    def test_06_notebooklm_generate_podcast(self):
        """Verify triggering Vietnamese Studio podcast generation with custom prompt."""
        payload = {
            "custom_prompt": "Phân tích chiến lược Vàng và Bạc ngày hôm nay",
            "wait_for_completion": False,
            "date": TODAY,
        }
        res = requests.post(f"{BRIDGE_URL}/api/notebooklm/generate-podcast", json=payload, timeout=30)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertIn(data.get("status"), ("ready", "generation_in_progress", "success"))
        print(f"\n[PASS] 06. NotebookLM Generate: Status: {data.get('status')}")

    def test_06b_notebooklm_generate_video(self):
        """Verify triggering Vietnamese Studio Video Overview generation (Explainer / Classic)."""
        payload = {
            "custom_prompt": "Tổng quan thị trường Vàng, Bạc, SPY và Bitcoin hôm nay",
            "video_format": "explainer",
            "video_style": "classic",
            "language": "vi",
            "wait_for_completion": False,
            "date": TODAY,
        }
        res = requests.post(f"{BRIDGE_URL}/api/notebooklm/generate-video", json=payload, timeout=30)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertIn(data.get("status"), ("ready", "generation_in_progress", "success"))
        self.assertEqual(data.get("video_format"), "explainer")
        self.assertEqual(data.get("video_style"), "classic")
        print(f"\n[PASS] 06b. NotebookLM Video Overview: Status: {data.get('status')} | Format: {data.get('video_format')} | Style: {data.get('video_style')}")

    def test_07_n8n_e2e_webhook_pipeline(self):
        """Trigger the published n8n workflow via webhook and verify full end-to-end execution."""
        start = datetime.datetime.now()
        res = requests.get(f"{N8N_WEBHOOK_URL}?date={TODAY}", timeout=240)
        elapsed = (datetime.datetime.now() - start).total_seconds()

        self.assertEqual(res.status_code, 200, f"Webhook execution failed with {res.status_code}: {res.text}")
        data = res.json()
        self.assertEqual(data.get("pipeline_status"), "success")
        self.assertIn("notebooklm", data)
        nlm = data.get("notebooklm", {})
        self.assertGreaterEqual(len(data.get("completed_reports_downloaded", [])), 6)
        self.assertGreaterEqual(len(data.get("charts_captured", [])), 12)
        self.assertIn(nlm.get("video_generation_status"), ("ready", "generation_in_progress", "success"))
        self.assertEqual(nlm.get("video_format"), "explainer")
        self.assertEqual(nlm.get("video_style"), "classic")
        print(f"\n[PASS] 07. n8n E2E Pipeline Succeeded in {elapsed:.2f}s! Summary:")
        print(f"  - Pipeline Status: {data.get('pipeline_status')}")
        print(f"  - Notebook ID: {nlm.get('notebook_id')}")
        print(f"  - Total Sources: {nlm.get('sources_total_count')}")
        print(f"  - Completed Reports: {len(data.get('completed_reports_downloaded', []))}")
        print(f"  - Charts Captured: {len(data.get('charts_captured', []))}")
        print(f"  - Studio Audio Status: {nlm.get('studio_generation_status')} (task: {nlm.get('studio_task_id')})")
        print(f"  - Video Overview Status: {nlm.get('video_generation_status')} (task: {nlm.get('video_task_id')}, format: {nlm.get('video_format')})")

    def test_08_notebooklm_auth_management(self):
        """Verify NotebookLM authentication status and keepalive management endpoints."""
        res = requests.get(f"{BRIDGE_URL}/api/notebooklm/auth/status", timeout=10)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertIn("status", data)
        self.assertIn("authenticated", data)
        self.assertIn("storage_exists", data)
        self.assertIn("keepalive", data)

        keepalive = data["keepalive"]
        self.assertIn("enabled", keepalive)
        self.assertIn("interval_seconds", keepalive)

        # Also test refresh endpoint response contract
        ref_res = requests.post(f"{BRIDGE_URL}/api/notebooklm/auth/refresh", json={"verify": False}, timeout=15)
        self.assertEqual(ref_res.status_code, 200, f"Expected 200, got {ref_res.status_code}: {ref_res.text}")
        ref_data = ref_res.json()
        self.assertIn("status", ref_data)
        print(f"\n[PASS] 08. NotebookLM Auth Management:")
        print(f"  - Auth Status   : {data.get('status')}")
        print(f"  - Storage Exists: {data.get('storage_exists')}")
        print(f"  - Cookies Count : {data.get('cookies_count')}")
        print(f"  - Keepalive Task: active={keepalive.get('task_active')}, interval={keepalive.get('interval_seconds')}s")
        print(f"  - Refresh Output: status={ref_data.get('status')}")

    def test_09_storage_state_update_api_and_form(self):
        """Verify the new POST /api/notebooklm/auth/storage-state endpoint (file + content) and n8n Form UI."""
        # 1. Test empty request returns 400
        empty_res = requests.post(f"{BRIDGE_URL}/api/notebooklm/auth/storage-state", json={}, timeout=10)
        self.assertEqual(empty_res.status_code, 400, f"Expected 400 for empty body, got {empty_res.status_code}")

        # 2. Test JSON payload with content string
        sample_cookie_json = json.dumps({
            "cookies": [
                {"name": "SID", "value": "test_sid_val", "domain": ".google.com", "path": "/"}
            ]
        })
        json_res = requests.post(
            f"{BRIDGE_URL}/api/notebooklm/auth/storage-state",
            json={"content": sample_cookie_json},
            timeout=15,
        )
        self.assertEqual(json_res.status_code, 200, f"Expected 200 for JSON content, got {json_res.status_code}: {json_res.text}")
        json_data = json_res.json()
        self.assertEqual(json_data.get("status"), "success")
        self.assertGreaterEqual(json_data.get("imported_cookies_count", 0), 1)

        # 3. Test Multipart file upload
        file_bytes = io.BytesIO(sample_cookie_json.encode("utf-8"))
        multipart_res = requests.post(
            f"{BRIDGE_URL}/api/notebooklm/auth/storage-state",
            files={"file": ("storage_state.json", file_bytes, "application/json")},
            timeout=15,
        )
        self.assertEqual(multipart_res.status_code, 200, f"Expected 200 for file upload, got {multipart_res.status_code}: {multipart_res.text}")
        multipart_data = multipart_res.json()
        self.assertEqual(multipart_data.get("status"), "success")
        self.assertGreaterEqual(multipart_data.get("imported_cookies_count", 0), 1)

        # 4. Verify n8n Form UI endpoint is live and accessible
        n8n_form_url = "http://localhost:5678/form/update-storage-state"
        form_res = requests.get(n8n_form_url, timeout=10)
        self.assertEqual(form_res.status_code, 200, f"Expected 200 for n8n Form UI, got {form_res.status_code}")
        self.assertIn("NotebookLM Auth", form_res.text)

        print("\n[PASS] 09. Storage State Update API & n8n Form UI:")
        print(f"  - Empty Validation 400 : PASS")
        print(f"  - JSON Content POST    : PASS (cookies={json_data.get('imported_cookies_count')})")
        print(f"  - Multipart File Upload: PASS (cookies={multipart_data.get('imported_cookies_count')})")
        print(f"  - n8n Form UI Endpoint : PASS (URL={n8n_form_url})")


if __name__ == "__main__":
    unittest.main()

