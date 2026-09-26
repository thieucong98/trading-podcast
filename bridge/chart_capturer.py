import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

logger = logging.getLogger("chart_capturer")

TIMEFRAME_LABELS = {
    "5": "5m",
    "15": "15m",
    "60": "1H",
    "240": "4H",
    "D": "1D",
    "1D": "1D",
    "W": "1W",
    "1W": "1W",
}

SYMBOL_MAP = {
    "XAUUSD": "OANDA:XAUUSD",
    "XAGUSD": "OANDA:XAGUSD",
    "BTC-USD": "BINANCE:BTCUSDT",
    "BTCUSD": "BINANCE:BTCUSDT",
    "SPY": "AMEX:SPY",
    "^TNX": "TVC:US10Y",
    "TNX": "TVC:US10Y",
    "DX-Y.NYB": "TVC:DXY",
    "DXY": "TVC:DXY",
}


def sanitize_filename(name: str) -> str:
    return name.replace(":", "_").replace("/", "_").replace("-", "_")


async def capture_single_chart(
    browser_context,
    symbol: str,
    interval: str,
    output_dir: Path,
    width: int = 1920,
    height: int = 1080,
    timeout_ms: int = 30000,
    max_retries: int = 2,
) -> dict[str, Any]:
    """Capture a single TradingView chart using the embed widget with retry resilience."""
    clean_symbol = SYMBOL_MAP.get(symbol.upper(), symbol)
    tf_label = TIMEFRAME_LABELS.get(str(interval), str(interval))
    filename = f"{sanitize_filename(symbol)}_{tf_label}.png"
    filepath = output_dir / filename

    widget_url = (
        f"https://s.tradingview.com/widgetembed/?"
        f"symbol={clean_symbol}&interval={interval}&theme=dark&style=1"
        f"&timezone=Etc%2FUTC&locale=en"
    )

    last_error = None
    for attempt in range(max_retries + 1):
        page = None
        try:
            page = await browser_context.new_page()
            await page.set_viewport_size({"width": width, "height": height})
            logger.info(
                f"Capturing {symbol} ({interval}) via {widget_url} (attempt {attempt + 1}/{max_retries + 1})"
            )

            # Use domcontentloaded for fast, reliable load without hanging on continuous WebSocket tickers
            await page.goto(widget_url, wait_until="domcontentloaded", timeout=timeout_ms)

            # Wait for chart widget container or canvas to appear
            try:
                await page.wait_for_selector(
                    "div.chart-container, div.tv-embed-widget-wrapper, canvas, #tv_chart_container",
                    timeout=12000,
                )
            except Exception as wait_err:
                logger.warning(f"Timeout waiting for chart selector on {symbol} ({interval}): {wait_err}")

            # Sleep 3.0s to allow candlesticks and volume indicators to finish rendering
            await asyncio.sleep(3.0)

            # Query chart container or take full page screenshot
            chart_element = await page.query_selector("div.chart-container, div.tv-embed-widget-wrapper, body")
            if chart_element:
                await chart_element.screenshot(path=str(filepath))
            else:
                await page.screenshot(path=str(filepath))

            file_size = os.path.getsize(filepath) if filepath.exists() else 0
            if file_size < 5000:
                raise ValueError(f"Captured chart is abnormally small or empty ({file_size} bytes)")

            logger.info(f"Saved chart: {filepath} ({file_size} bytes)")
            return {
                "symbol": symbol,
                "tradingview_symbol": clean_symbol,
                "interval": interval,
                "timeframe": tf_label,
                "filepath": str(filepath.resolve()),
                "filename": filename,
                "size_bytes": file_size,
                "status": "success",
            }
        except Exception as e:
            last_error = e
            logger.warning(f"Error capturing {symbol} ({interval}) on attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                await asyncio.sleep(2)
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass

    # Graceful fallback: If all retries failed but an earlier valid chart exists on disk, reuse it
    if filepath.exists() and filepath.stat().st_size > 5000:
        logger.warning(
            f"Capture failed after {max_retries + 1} attempts ({last_error}). Falling back to existing valid chart: {filepath}"
        )
        return {
            "symbol": symbol,
            "tradingview_symbol": clean_symbol,
            "interval": interval,
            "timeframe": tf_label,
            "filepath": str(filepath.resolve()),
            "filename": filename,
            "size_bytes": filepath.stat().st_size,
            "status": "fallback_cached",
            "warning": f"Capture failed ({last_error}), retained existing valid chart.",
        }

    logger.error(f"Permanent failure capturing {symbol} ({interval}): {last_error}")
    return {
        "symbol": symbol,
        "tradingview_symbol": clean_symbol,
        "interval": interval,
        "timeframe": tf_label,
        "filepath": str(filepath.resolve()) if filepath.exists() else None,
        "filename": filename,
        "error": str(last_error),
        "status": "error",
    }


async def capture_tradingview_charts(
    symbols: list[str],
    intervals: list[str] | None = None,
    output_dir: str | Path = "/app/output/charts",
    force_recapture: bool = False,
) -> list[dict[str, Any]]:
    """Capture multiple symbols across multiple intervals with optional caching."""
    if intervals is None:
        intervals = ["15", "60", "240", "D"]

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results = []
    missing_targets = []

    # Check if files already exist on disk
    for sym in symbols:
        for interval in intervals:
            tf_label = TIMEFRAME_LABELS.get(str(interval), str(interval))
            filename = f"{sanitize_filename(sym)}_{tf_label}.png"
            filepath = out_path / filename
            if not force_recapture and filepath.exists() and filepath.stat().st_size > 5000:
                logger.info(f"Using cached chart: {filename} ({filepath.stat().st_size} bytes)")
                results.append({
                    "symbol": sym,
                    "tradingview_symbol": SYMBOL_MAP.get(sym.upper(), sym),
                    "interval": interval,
                    "timeframe": tf_label,
                    "filename": filename,
                    "filepath": str(filepath.resolve()),
                    "size_bytes": filepath.stat().st_size,
                    "status": "cached",
                })
            else:
                missing_targets.append((sym, interval))

    if not missing_targets:
        logger.info(f"All {len(results)} charts found in cache (force_recapture=False). Skipping browser capture.")
        return results

    logger.info(f"Capturing {len(missing_targets)} charts using Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )

        try:
            for sym, interval in missing_targets:
                res = await capture_single_chart(context, sym, interval, out_path)
                results.append(res)
        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Quick standalone test for XAUUSD and XAGUSD
    asyncio.run(
        capture_tradingview_charts(
            symbols=["XAUUSD", "XAGUSD"],
            intervals=["60", "D"],
            output_dir="./output/charts",
        )
    )
