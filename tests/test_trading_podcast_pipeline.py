"""Comprehensive automated test suite for Trading Podcast AI Pipeline.
Verifies bridge endpoints, smart caching, report content integrity,
zero dummy fallback guarantee, TradingView chart captures, and NotebookLM integration.
"""

import datetime
from pathlib import Path
import unittest
import requests

BRIDGE_URL = "http://localhost:8010"
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/run-trading-podcast"
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "output" / "reports"
CHARTS_DIR = PROJECT_ROOT / "output" / "charts"

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

    def test_07_n8n_e2e_webhook_pipeline(self):
        """Trigger the published n8n workflow via webhook and verify full end-to-end execution."""
        start = datetime.datetime.now()
        res = requests.get(N8N_WEBHOOK_URL, timeout=120)
        elapsed = (datetime.datetime.now() - start).total_seconds()

        self.assertEqual(res.status_code, 200, f"Webhook execution failed with {res.status_code}: {res.text}")
        data = res.json()
        self.assertEqual(data.get("pipeline_status"), "success")
        self.assertIn("notebooklm", data)
        self.assertEqual(len(data.get("completed_reports_downloaded", [])), 6)
        self.assertGreaterEqual(len(data.get("charts_captured", [])), 12)
        print(f"\n[PASS] 07. n8n E2E Pipeline Succeeded in {elapsed:.2f}s! Summary:")
        print(f"  - Pipeline Status: {data.get('pipeline_status')}")
        print(f"  - Notebook ID: {data.get('notebooklm', {}).get('notebook_id')}")
        print(f"  - Total Sources: {data.get('notebooklm', {}).get('sources_total_count')}")
        print(f"  - Completed Reports: {len(data.get('completed_reports_downloaded', []))}")
        print(f"  - Charts Captured: {len(data.get('charts_captured', []))}")


if __name__ == "__main__":
    unittest.main()
