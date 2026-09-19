import asyncio
import datetime
import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import requests

from .chart_capturer import capture_tradingview_charts
from .notebooklm_client import DEFAULT_VIETNAMESE_PROMPT, notebooklm_client
from .report_aggregator import build_podcast_briefing_markdown

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bridge_service")

app = FastAPI(
    title="Trading Podcast Automation Bridge",
    description="FastAPI service connecting TradingAgents, TradingView charts, and Google NotebookLM Studio Podcast",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/app/output"))
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORTS_DIR = OUTPUT_DIR / "reports"
PODCASTS_DIR = OUTPUT_DIR / "podcasts"

for d in [CHARTS_DIR, REPORTS_DIR, PODCASTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class ChartCaptureRequest(BaseModel):
    symbols: list[str] = Field(default=["XAUUSD", "XAGUSD"])
    intervals: list[str] = Field(default=["15", "60", "240", "D"])
    force_recapture: bool = Field(default=False, description="If False, reuses existing charts on disk")


class ReportSynthesizeRequest(BaseModel):
    reports: list[dict[str, Any]]
    date: str | None = None


class NotebookLMUploadSourcesRequest(BaseModel):
    briefing_md_path: str | None = None
    report_md_paths: list[str] = Field(default=[])
    chart_image_paths: list[str] = Field(default=[])
    notebook_title: str | None = None
    notebook_id: str | None = None
    date: str | None = None


class PodcastGenerateRequest(BaseModel):
    notebook_id: str | None = None
    briefing_md_path: str | None = None
    chart_image_paths: list[str] = Field(default=[])
    custom_prompt: str | None = Field(default=DEFAULT_VIETNAMESE_PROMPT)
    wait_for_completion: bool = False
    date: str | None = None


class MarketAnalysisRequest(BaseModel):
    tickers: list[str] = Field(default=["XAUUSD", "SPY", "BTC-USD"])
    tradingagents_backend_url: str = Field(default="http://tradingagents-backend:8000")
    llm_provider: str | None = Field(default=None, description="e.g. openai_compatible, openai, google, anthropic, deepseek")
    deep_think_llm: str | None = Field(default=None, description="Model ID for deep reasoning (e.g. ag/gemini-3.8-flash-high)")
    quick_think_llm: str | None = Field(default=None, description="Model ID for quick reasoning (e.g. ag/gemini-3.8-flash-high)")
    max_debate_rounds: int | None = Field(default=None, description="Number of bull/bear debate rounds (1-5)")
    max_risk_discuss_rounds: int | None = Field(default=None, description="Number of risk debate rounds (1-5)")
    output_language: str | None = Field(default=None, description="e.g. Vietnamese, English")
    force_reanalyze: bool = Field(default=False, description="If False, reuses existing completed reports for today")
    date: str | None = None


class FullPipelineRequest(BaseModel):
    tickers: list[str] = Field(default=["XAUUSD", "SPY", "BTC-USD"])
    chart_symbols: list[str] = Field(default=["XAUUSD", "XAGUSD"])
    chart_intervals: list[str] = Field(default=["15", "60", "240", "D"])
    tradingagents_backend_url: str = Field(default="http://tradingagents-backend:8000")
    llm_provider: str | None = None
    deep_think_llm: str | None = None
    quick_think_llm: str | None = None
    max_debate_rounds: int | None = None
    max_risk_discuss_rounds: int | None = None
    output_language: str | None = None
    force_reanalyze: bool = False
    force_recapture_charts: bool = False
    custom_prompt: str | None = Field(default=DEFAULT_VIETNAMESE_PROMPT)
    date: str | None = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Trading Podcast Bridge",
        "notebooklm_authenticated": notebooklm_client.is_authenticated(),
        "storage_state_path": notebooklm_client.storage_state_path,
        "output_dir": str(OUTPUT_DIR.resolve()),
    }


@app.post("/api/charts/capture")
async def capture_charts_endpoint(req: ChartCaptureRequest):
    """Capture multi-timeframe charts from TradingView with caching support."""
    logger.info(f"Received chart capture request for {req.symbols} across {req.intervals} (force_recapture={req.force_recapture})")
    try:
        results = await capture_tradingview_charts(
            symbols=req.symbols,
            intervals=req.intervals,
            output_dir=CHARTS_DIR,
            force_recapture=req.force_recapture,
        )
        return {"status": "success", "count": len(results), "charts": results}
    except Exception as e:
        logger.error(f"Failed capturing charts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reports/synthesize")
async def synthesize_reports_endpoint(req: ReportSynthesizeRequest):
    """Aggregate individual asset reports into a structured podcast briefing markdown."""
    logger.info(f"Synthesizing briefing for {len(req.reports)} asset reports...")
    try:
        result = build_podcast_briefing_markdown(
            reports=req.reports,
            date_str=req.date,
            output_dir=REPORTS_DIR,
        )
        return result
    except Exception as e:
        logger.error(f"Failed synthesizing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notebooklm/upload-sources")
async def upload_sources_endpoint(req: NotebookLMUploadSourcesRequest):
    """Create Google NotebookLM notebook (or use existing) and upload individual completed reports and chart images."""
    logger.info(f"Uploading sources to NotebookLM (notebook_id={req.notebook_id}, reports={len(req.report_md_paths)}, charts={len(req.chart_image_paths)})...")
    try:
        result = await notebooklm_client.upload_sources_to_notebooklm(
            report_md_paths=req.report_md_paths,
            briefing_md_path=req.briefing_md_path,
            chart_image_paths=req.chart_image_paths,
            notebook_title=req.notebook_title,
            notebook_id=req.notebook_id,
            date_str=req.date,
        )
        return result
    except Exception as e:
        logger.error(f"Failed uploading sources to NotebookLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notebooklm/generate-podcast")
async def generate_podcast_endpoint(req: PodcastGenerateRequest):
    """Trigger Google NotebookLM Studio Podcast generation with Vietnamese prompt."""
    logger.info(f"Generating podcast via NotebookLM Studio (notebook_id={req.notebook_id})...")
    try:
        result = await notebooklm_client.generate_podcast_studio(
            notebook_id=req.notebook_id,
            briefing_md_path=req.briefing_md_path,
            chart_image_paths=req.chart_image_paths,
            custom_prompt=req.custom_prompt,
            wait_for_completion=req.wait_for_completion,
            date_str=req.date,
            output_dir=PODCASTS_DIR,
        )
        return result
    except Exception as e:
        logger.error(f"Failed generating podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline/analyze-markets")
async def analyze_markets_endpoint(req: MarketAnalysisRequest):
    """Trigger TradingAgents jobs for tickers and poll for completion (granular step)."""
    today = req.date or datetime.datetime.now().strftime("%Y-%m-%d")
    base_url = req.tradingagents_backend_url.rstrip("/")
    collected_reports = []

    provider = req.llm_provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai_compatible")
    deep_model = req.deep_think_llm or os.getenv("DEFAULT_DEEP_THINK_LLM", "ag/gemini-3.8-flash-high")
    quick_model = req.quick_think_llm or os.getenv("DEFAULT_QUICK_THINK_LLM", "ag/gemini-3.8-flash-high")
    debate_rounds = req.max_debate_rounds if req.max_debate_rounds is not None else 3
    risk_rounds = req.max_risk_discuss_rounds if req.max_risk_discuss_rounds is not None else 3
    language = req.output_language or "Vietnamese"

    logger.info(f"Executing granular market analysis for tickers: {req.tickers} using provider={provider}, deep={deep_model}, quick={quick_model}, rounds={debate_rounds}/{risk_rounds}, lang={language} on date {today} (force_reanalyze={req.force_reanalyze})")

    # Check for already completed jobs today if force_reanalyze is False
    cached_reports = {}
    if not req.force_reanalyze:
        try:
            jobs_res = requests.get(f"{base_url}/api/v1/jobs", timeout=10)
            if jobs_res.status_code == 200:
                all_jobs = jobs_res.json().get("jobs", [])
                for job in all_jobs:
                    if job.get("trade_date") == today and job.get("status") == "completed":
                        t = job.get("ticker")
                        if t in req.tickers and t not in cached_reports:
                            rep_res = requests.get(f"{base_url}/api/v1/reports/{job['id']}", timeout=10)
                            if rep_res.status_code == 200:
                                rep_dict = rep_res.json()
                                rep_dict["job_id"] = job["id"]
                                cached_reports[t] = rep_dict
                                logger.info(f"Reusing completed analysis for {t} from job {job['id']} (trade_date: {today})")
        except Exception as e:
            logger.warning(f"Error checking cached jobs: {e}")

    for ticker in req.tickers:
        if ticker in cached_reports:
            logger.info(f"Using cached analysis for {ticker} (force_reanalyze=False)")
            collected_reports.append(cached_reports[ticker])
            continue

        asset_type = "crypto" if "BTC" in ticker or "ETH" in ticker else "stock"
        job_payload = {
            "ticker": ticker,
            "trade_date": today,
            "asset_type": asset_type,
            "analysts": ["market", "social", "news", "fundamentals"],
            "output_language": language,
            "llm_provider": provider,
            "deep_think_llm": deep_model,
            "quick_think_llm": quick_model,
            "max_debate_rounds": debate_rounds,
            "max_risk_discuss_rounds": risk_rounds,
        }
        try:
            logger.info(f"Granular: Creating job for {ticker} at {base_url}/api/v1/jobs...")
            res = requests.post(f"{base_url}/api/v1/jobs", json=job_payload, timeout=15)
            if res.status_code in (200, 201):
                job_data = res.json()
                job_id = job_data["id"]
                logger.info(f"Job {job_id} created for {ticker}. Polling status...")

                max_polls = 12
                completed = False
                for _ in range(max_polls):
                    await asyncio.sleep(5)
                    poll_res = requests.get(f"{base_url}/api/v1/jobs/{job_id}", timeout=10)
                    if poll_res.status_code == 200:
                        status_val = poll_res.json().get("status")
                        if status_val == "completed":
                            completed = True
                            break
                        elif status_val in ("failed", "cancelled"):
                            break

                if completed:
                    rep_res = requests.get(f"{base_url}/api/v1/reports/{job_id}", timeout=10)
                    if rep_res.status_code == 200:
                        rep_dict = rep_res.json()
                        rep_dict["job_id"] = job_id
                        collected_reports.append(rep_dict)
            else:
                logger.warning(f"Failed starting job for {ticker}: {res.text}")
        except Exception as e:
            logger.warning(f"Error calling TradingAgents for {ticker}: {e}")

    if not collected_reports:
        for ticker in req.tickers:
            collected_reports.append({
                "ticker": ticker,
                "trade_date": today,
                "recommendation": "Quan sát kỹ thuật (Wait & Watch)",
                "executive_summary": f"Phân tích kỹ thuật và dòng tiền tổng thể cho {ticker} ngày {today}.",
                "entry_price": 0.0,
                "market_report_md": f"Dữ liệu thị trường cho {ticker}.",
                "news_report_md": f"Các diễn biến kinh tế vĩ mô liên quan tới {ticker}.",
            })

    # Download and persist individual Completed Reports as raw Markdown files
    report_files = []
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for rep in collected_reports:
        ticker = rep.get("ticker", "REPORT")
        clean_ticker = ticker.replace("^", "").replace("/", "_").replace(":", "_").strip()
        job_id = rep.get("job_id") or rep.get("id")
        md_filename = f"TradingAgents_{clean_ticker}_{today}_Complete.md"
        md_path = REPORTS_DIR / md_filename

        md_content = None
        if job_id:
            try:
                dl_res = requests.get(f"{base_url}/api/v1/reports/{job_id}/download?tab=complete", timeout=15)
                if dl_res.status_code == 200 and len(dl_res.text) > 100:
                    md_content = dl_res.text
            except Exception as ex:
                logger.warning(f"Error downloading complete report for {ticker} (job {job_id}): {ex}")

        if not md_content:
            md_content = rep.get("complete_report_md") or rep.get("executive_summary") or f"# Báo cáo phân tích {ticker} ngày {today}"

        md_path.write_text(md_content, encoding="utf-8")
        logger.info(f"Saved completed markdown report for {ticker} to {md_path} ({len(md_content)} chars)")
        report_files.append(str(md_path.resolve()))

    return {
        "status": "success",
        "date": today,
        "tickers": req.tickers,
        "reports_count": len(collected_reports),
        "report_files": report_files,
        "reports": collected_reports,
    }


@app.post("/api/pipeline/run-full-flow")
async def run_full_pipeline(req: FullPipelineRequest):
    """Complete end-to-end execution:
    1. Triggers TradingAgents jobs for tickers
    2. Polls until completion & fetches markdown reports
    3. Captures TradingView charts for XAUUSD & XAGUSD
    4. Aggregates reports into single Podcast Briefing markdown
    5. Sends sources to NotebookLM & generates Vietnamese Audio Overview
    """
    today = req.date or datetime.datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Starting Full Trading Podcast Pipeline for date: {today}")

    # 1. Trigger jobs on TradingAgents
    base_url = req.tradingagents_backend_url.rstrip("/")
    collected_reports = []

    provider = req.llm_provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai_compatible")
    deep_model = req.deep_think_llm or os.getenv("DEFAULT_DEEP_THINK_LLM", "ag/gemini-3.8-flash-high")
    quick_model = req.quick_think_llm or os.getenv("DEFAULT_QUICK_THINK_LLM", "ag/gemini-3.8-flash-high")
    debate_rounds = req.max_debate_rounds if req.max_debate_rounds is not None else 3
    risk_rounds = req.max_risk_discuss_rounds if req.max_risk_discuss_rounds is not None else 3
    language = req.output_language or "Vietnamese"

    for ticker in req.tickers:
        asset_type = "crypto" if "BTC" in ticker or "ETH" in ticker else "stock"
        job_payload = {
            "ticker": ticker,
            "trade_date": today,
            "asset_type": asset_type,
            "analysts": ["market", "social", "news", "fundamentals"],
            "output_language": language,
            "llm_provider": provider,
            "deep_think_llm": deep_model,
            "quick_think_llm": quick_model,
            "max_debate_rounds": debate_rounds,
            "max_risk_discuss_rounds": risk_rounds,
        }
        try:
            logger.info(f"Creating job for {ticker} at {base_url}/api/v1/jobs...")
            res = requests.post(f"{base_url}/api/v1/jobs", json=job_payload, timeout=15)
            if res.status_code in (200, 201):
                job_data = res.json()
                job_id = job_data["id"]
                logger.info(f"Job {job_id} created for {ticker}. Polling status...")

                # Poll up to 60s (or retrieve cached/finished)
                max_polls = 12
                completed = False
                for _ in range(max_polls):
                    await asyncio.sleep(5)
                    poll_res = requests.get(f"{base_url}/api/v1/jobs/{job_id}", timeout=10)
                    if poll_res.status_code == 200:
                        status_val = poll_res.json().get("status")
                        if status_val == "completed":
                            completed = True
                            break
                        elif status_val in ("failed", "cancelled"):
                            break

                # Fetch report if completed
                if completed:
                    rep_res = requests.get(f"{base_url}/api/v1/reports/{job_id}", timeout=10)
                    if rep_res.status_code == 200:
                        collected_reports.append(rep_res.json())
            else:
                logger.warning(f"Failed starting job for {ticker}: {res.text}")
        except Exception as e:
            logger.warning(f"Error calling TradingAgents for {ticker}: {e}")

    # If no live reports were collected (e.g. backend busy or mock mode), create informative fallback reports
    if not collected_reports:
        for ticker in req.tickers:
            collected_reports.append({
                "ticker": ticker,
                "trade_date": today,
                "recommendation": "Quan sát kỹ thuật (Wait & Watch)",
                "executive_summary": f"Phân tích kỹ thuật và dòng tiền tổng thể cho {ticker} ngày {today}.",
                "entry_price": 0.0,
                "market_report_md": f"Dữ liệu thị trường cho {ticker}.",
                "news_report_md": f"Các diễn biến kinh tế vĩ mô liên quan tới {ticker}.",
            })

    # 2. Capture TradingView Charts
    chart_results = await capture_tradingview_charts(
        symbols=req.chart_symbols,
        intervals=req.chart_intervals,
        output_dir=CHARTS_DIR,
    )
    chart_files = [c["filepath"] for c in chart_results if c.get("status") == "success"]

    # 3. Synthesize Briefing Markdown
    briefing_meta = build_podcast_briefing_markdown(
        reports=collected_reports,
        date_str=today,
        output_dir=REPORTS_DIR,
    )

    # 4. NotebookLM Studio Podcast Generation
    podcast_result = await notebooklm_client.generate_podcast_studio(
        briefing_md_path=briefing_meta["filepath"],
        chart_image_paths=chart_files,
        custom_prompt=req.custom_prompt,
        date_str=today,
        output_dir=PODCASTS_DIR,
    )

    return {
        "status": "success",
        "date": today,
        "tickers_analyzed": req.tickers,
        "charts_captured": len(chart_files),
        "chart_files": chart_files,
        "briefing_markdown_path": briefing_meta["filepath"],
        "podcast_result": podcast_result,
    }


@app.get("/api/download/chart/{filename}")
async def download_chart(filename: str):
    file_path = CHARTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    return FileResponse(path=str(file_path), media_type="image/png", filename=filename)


@app.get("/api/download/report/{filename}")
async def download_report(filename: str):
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(path=str(file_path), media_type="text/markdown", filename=filename)
