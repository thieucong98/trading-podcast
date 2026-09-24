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


def _clean_ticker(ticker: str) -> str:
    return ticker.replace("^", "").replace("/", "_").replace(":", "_").strip()


def _download_report_markdown(base_url: str, job_id: str) -> str | None:
    """Download the complete raw markdown report from TradingAgents backend."""
    try:
        url = f"{base_url}/api/v1/reports/{job_id}/download?tab=complete"
        res = requests.get(url, timeout=20)
        if res.status_code == 200 and len(res.text.strip()) > 1000:
            return res.text.strip()
    except Exception as e:
        logger.warning(f"Failed download tab=complete for job {job_id}: {e}")

    try:
        url = f"{base_url}/api/v1/reports/{job_id}"
        res = requests.get(url, timeout=20)
        if res.status_code == 200:
            data = res.json()
            full_md = data.get("complete_report_md")
            if full_md and len(full_md.strip()) > 1000:
                return full_md.strip()
    except Exception as e:
        logger.warning(f"Failed fetching report JSON for job {job_id}: {e}")

    return None


async def _poll_job_until_done(
    base_url: str,
    job_id: str,
    ticker: str,
    max_wait_seconds: int = 1800,
    poll_interval: int = 10,
) -> tuple[bool, str | None]:
    """Poll a TradingAgents job until completed, failed, or timed out."""
    elapsed = 0
    last_stage = None
    last_progress = None

    while elapsed < max_wait_seconds:
        try:
            poll_res = requests.get(f"{base_url}/api/v1/jobs/{job_id}", timeout=10)
            if poll_res.status_code == 200:
                job_info = poll_res.json()
                st = job_info.get("status")
                stage = job_info.get("current_stage")
                progress = job_info.get("progress")
                err = job_info.get("error_message")

                if stage != last_stage or progress != last_progress:
                    logger.info(f"[{ticker}] Job {job_id}: status={st}, progress={progress}%, stage='{stage}' (elapsed: {elapsed}s)")
                    last_stage = stage
                    last_progress = progress

                if st == "completed":
                    logger.info(f"[{ticker}] Job {job_id} COMPLETED in {elapsed}s.")
                    return True, None
                elif st in ("failed", "cancelled"):
                    logger.error(f"[{ticker}] Job {job_id} {st.upper()}: {err}")
                    return False, err or f"Job {st}"
        except Exception as e:
            logger.warning(f"[{ticker}] Error polling job {job_id}: {e}")

        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    return False, f"Timeout after {max_wait_seconds}s waiting for job {job_id}"


async def _execute_ticker_analysis(
    base_url: str,
    ticker: str,
    today: str,
    job_payload: dict[str, Any],
    existing_job_id: str | None = None,
    max_retries: int = 2,
) -> tuple[str, str, int]:
    """Run or adopt analysis for a single ticker with automatic retries on transient errors.
    Returns (ticker, saved_file_path, content_length).
    Raises RuntimeError on permanent failure.
    """
    clean_t = _clean_ticker(ticker)
    md_path = REPORTS_DIR / f"TradingAgents_{clean_t}_{today}_Complete.md"

    current_job_id = existing_job_id
    attempts = 0

    while attempts <= max_retries:
        if not current_job_id:
            logger.info(f"[{ticker}] Starting new analysis job (attempt {attempts + 1}/{max_retries + 1})...")
            try:
                res = requests.post(f"{base_url}/api/v1/jobs", json=job_payload, timeout=20)
                if res.status_code in (200, 201):
                    current_job_id = res.json().get("id")
                    logger.info(f"[{ticker}] Spawned Job ID: {current_job_id}")
                else:
                    err_msg = f"HTTP {res.status_code}: {res.text}"
                    logger.error(f"[{ticker}] Failed creating job: {err_msg}")
                    attempts += 1
                    if attempts <= max_retries:
                        await asyncio.sleep(10)
                    continue
            except Exception as e:
                logger.error(f"[{ticker}] Request error creating job: {e}")
                attempts += 1
                if attempts <= max_retries:
                    await asyncio.sleep(10)
                continue

        # Poll the active job
        success, error_msg = await _poll_job_until_done(
            base_url=base_url,
            job_id=current_job_id,
            ticker=ticker,
            max_wait_seconds=1800,
            poll_interval=10,
        )

        if success:
            content = _download_report_markdown(base_url, current_job_id)
            if content and len(content) > 1000:
                md_path.write_text(content, encoding="utf-8")
                logger.info(f"[{ticker}] Successfully saved verified report to {md_path} ({len(content)} chars)")
                return ticker, str(md_path.resolve()), len(content)
            else:
                logger.warning(f"[{ticker}] Job {current_job_id} completed but report content is too short/missing ({len(content or '')} chars)")
                error_msg = "Report content missing or under 1000 characters"

        # If job failed or report was invalid, prepare for retry
        attempts += 1
        current_job_id = None
        if attempts <= max_retries:
            backoff_sec = attempts * 15
            logger.warning(f"[{ticker}] Retrying in {backoff_sec}s after failure: {error_msg}...")
            await asyncio.sleep(backoff_sec)

    raise RuntimeError(f"Analysis failed for {ticker} after {max_retries + 1} attempts. Last error: {error_msg}")


@app.post("/api/pipeline/analyze-markets")
async def analyze_markets_endpoint(req: MarketAnalysisRequest):
    """Trigger TradingAgents jobs for tickers and poll for completion (granular step).
    Strictly verifies all reports - NEVER produces fake/dummy placeholder files.
    """
    today = req.date or datetime.datetime.now().strftime("%Y-%m-%d")
    base_url = req.tradingagents_backend_url.rstrip("/")

    provider = req.llm_provider or os.getenv("DEFAULT_LLM_PROVIDER", "openai_compatible")
    deep_model = req.deep_think_llm or os.getenv("DEFAULT_DEEP_THINK_LLM", "ag/gemini-3.8-flash-high")
    quick_model = req.quick_think_llm or os.getenv("DEFAULT_QUICK_THINK_LLM", "ag/gemini-3.8-flash-high")
    debate_rounds = req.max_debate_rounds if req.max_debate_rounds is not None else 3
    risk_rounds = req.max_risk_discuss_rounds if req.max_risk_discuss_rounds is not None else 3
    language = req.output_language or "Vietnamese"

    logger.info(
        f"Granular analysis request: tickers={req.tickers}, date={today}, "
        f"force_reanalyze={req.force_reanalyze}, provider={provider}, deep={deep_model}, quick={quick_model}"
    )

    # 1. Inspect existing backend jobs for today
    existing_completed: dict[str, dict[str, Any]] = {}
    existing_running: dict[str, dict[str, Any]] = {}

    try:
        jobs_res = requests.get(f"{base_url}/api/v1/jobs?limit=100", timeout=15)
        if jobs_res.status_code == 200:
            all_jobs = jobs_res.json().get("jobs", [])
            for job in all_jobs:
                if job.get("trade_date") == today:
                    t = job.get("ticker")
                    st = job.get("status")
                    if st == "completed" and t not in existing_completed:
                        existing_completed[t] = job
                    elif st in ("running", "queued") and t not in existing_running:
                        existing_running[t] = job
    except Exception as e:
        logger.warning(f"Error querying existing jobs: {e}")

    saved_reports: dict[str, str] = {}
    reused_tickers: list[str] = []
    tickers_to_execute: dict[str, str | None] = {}

    # 2. Check each requested ticker
    for ticker in req.tickers:
        clean_t = _clean_ticker(ticker)
        md_path = REPORTS_DIR / f"TradingAgents_{clean_t}_{today}_Complete.md"

        # Check if we can reuse a completed job (strictly matching requested provider and models)
        if not req.force_reanalyze and ticker in existing_completed:
            candidate = existing_completed[ticker]
            cand_p = candidate.get("llm_provider")
            cand_deep = candidate.get("deep_think_llm")
            cand_lang = candidate.get("output_language")

            match_p = (not provider) or (cand_p == provider)
            match_deep = (not deep_model) or (cand_deep == deep_model)
            match_lang = (not language) or (cand_lang == language)

            if match_p and match_deep and match_lang:
                job_id = candidate["id"]
                logger.info(f"[{ticker}] Found matching completed job {job_id} for {today} (provider={cand_p}, deep={cand_deep}). Validating report...")
                content = _download_report_markdown(base_url, job_id)
                if content and len(content) > 1000:
                    md_path.write_text(content, encoding="utf-8")
                    saved_reports[ticker] = str(md_path.resolve())
                    reused_tickers.append(ticker)
                    logger.info(f"[{ticker}] Successfully reused completed report ({len(content)} chars)")
                    continue
                else:
                    logger.warning(f"[{ticker}] Existing completed job {job_id} had invalid/missing report. Will re-run.")
            else:
                logger.info(
                    f"[{ticker}] Existing completed job {candidate['id']} has different settings "
                    f"(provider={cand_p} vs {provider}, deep={cand_deep} vs {deep_model}). Re-analyzing with requested global settings."
                )

        # If not reusable, check if currently running with matching config
        if not req.force_reanalyze and ticker in existing_running:
            cand = existing_running[ticker]
            cand_p = cand.get("llm_provider")
            cand_deep = cand.get("deep_think_llm")
            if ((not provider) or (cand_p == provider)) and ((not deep_model) or (cand_deep == deep_model)):
                job_id = cand["id"]
                logger.info(f"[{ticker}] Adopting currently running job {job_id} (matching provider={cand_p})")
                tickers_to_execute[ticker] = job_id
            else:
                logger.info(f"[{ticker}] Running job {cand['id']} uses different provider ({cand_p} vs {provider}). Starting new job.")
                tickers_to_execute[ticker] = None
        else:
            tickers_to_execute[ticker] = None


    # 3. Concurrently execute/poll all remaining tickers
    if tickers_to_execute:
        logger.info(f"Executing/polling {len(tickers_to_execute)} tickers concurrently: {list(tickers_to_execute.keys())}")

        async def _run_one(t: str, jid: str | None):
            asset_type = "crypto" if "BTC" in t or "ETH" in t else "stock"
            payload = {
                "ticker": t,
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
            return await _execute_ticker_analysis(
                base_url=base_url,
                ticker=t,
                today=today,
                job_payload=payload,
                existing_job_id=jid,
                max_retries=2,
            )

        tasks = [_run_one(t, jid) for t, jid in tickers_to_execute.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failed_tickers = []
        for (t, _), res in zip(tickers_to_execute.items(), results):
            if isinstance(res, Exception):
                logger.error(f"[{t}] Execution failed with exception: {res}")
                failed_tickers.append({"ticker": t, "error": str(res)})
            else:
                ticker_name, file_path, size = res
                saved_reports[ticker_name] = file_path

        if failed_tickers:
            logger.error(f"Pipeline failed: {len(failed_tickers)} ticker(s) failed analysis: {failed_tickers}")
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "failed",
                    "message": f"Market analysis failed for {len(failed_tickers)} ticker(s). Aborting pipeline to prevent bad data in NotebookLM.",
                    "failed_tickers": failed_tickers,
                    "completed_tickers": list(saved_reports.keys()),
                },
            )

    # 4. Verify all tickers have valid report files
    ordered_report_files = [saved_reports[t] for t in req.tickers if t in saved_reports]
    if len(ordered_report_files) != len(req.tickers):
        missing = [t for t in req.tickers if t not in saved_reports]
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message": f"Incomplete reports: missing tickers {missing}",
                "missing": missing,
            },
        )

    logger.info(f"All {len(req.tickers)} market analysis reports verified and ready: {ordered_report_files}")
    return {
        "status": "success",
        "date": today,
        "tickers": req.tickers,
        "reports_count": len(ordered_report_files),
        "report_files": ordered_report_files,
        "reused_tickers": reused_tickers,
        "fresh_tickers": list(tickers_to_execute.keys()),
    }


@app.post("/api/pipeline/run-full-flow")
async def run_full_pipeline(req: FullPipelineRequest):
    """Complete end-to-end execution without fake dummy fallbacks:
    1. Triggers TradingAgents jobs for tickers & verifies real complete reports
    2. Captures TradingView charts for specified symbols & intervals
    3. Uploads verified sources to Google NotebookLM
    4. Triggers Vietnamese Studio Audio generation
    """
    today = req.date or datetime.datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Starting Full Trading Podcast Pipeline for date: {today}")

    # 1. Run rigorous market analysis
    analysis_res = await analyze_markets_endpoint(
        MarketAnalysisRequest(
            tickers=req.tickers,
            tradingagents_backend_url=req.tradingagents_backend_url,
            llm_provider=req.llm_provider,
            deep_think_llm=req.deep_think_llm,
            quick_think_llm=req.quick_think_llm,
            max_debate_rounds=req.max_debate_rounds,
            max_risk_discuss_rounds=req.max_risk_discuss_rounds,
            output_language=req.output_language,
            force_reanalyze=req.force_reanalyze,
            date=today,
        )
    )
    report_files = analysis_res["report_files"]

    # 2. Capture TradingView Charts
    chart_results = await capture_tradingview_charts(
        symbols=req.chart_symbols,
        intervals=req.chart_intervals,
        output_dir=CHARTS_DIR,
        force_recapture=req.force_recapture_charts,
    )
    chart_files = [c["filepath"] for c in chart_results if c.get("status") == "success"]

    # 3. Upload Completed Reports & Charts to NotebookLM
    upload_result = await notebooklm_client.upload_sources_to_notebooklm(
        report_md_paths=report_files,
        chart_image_paths=chart_files,
        date_str=today,
    )

    # 4. NotebookLM Studio Podcast Generation
    podcast_result = await notebooklm_client.generate_podcast_studio(
        notebook_id=upload_result.get("notebook_id"),
        chart_image_paths=chart_files,
        custom_prompt=req.custom_prompt,
        wait_for_completion=False,
        date_str=today,
        output_dir=PODCASTS_DIR,
    )

    return {
        "status": "success",
        "date": today,
        "tickers_analyzed": req.tickers,
        "reports_count": len(report_files),
        "report_files": report_files,
        "reused_tickers": analysis_res.get("reused_tickers", []),
        "fresh_tickers": analysis_res.get("fresh_tickers", []),
        "charts_captured": len(chart_files),
        "chart_files": chart_files,
        "notebooklm_upload": upload_result,
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

