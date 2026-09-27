---
phase: 2
title: "24h Trend Radar & Dual AI Video Provider (Google + Fal.ai)"
status: pending
priority: P1
effort: "2h"
dependencies: []
---

# Phase 2: 24h Trend Radar & Dual AI Video Provider (Google + Fal.ai)

## Overview
Equip the studio with a 24-hour algorithmic Trend Radar to discover viral high-RPM topics in real-time before competitors, and add a Dual AI Video Provider architecture supporting both Google Direct (Vertex AI / Gemini / Veo I2V) and Fal.ai (Veo 3.1 `reference-to-video` and `first-last-frame-to-video`).

## Requirements
- **Functional Requirements:**
  - **24h Trend Radar Engine (`TrendRadarService` in `bridge/google_ai_service.py`):**
    - Connects to public trending feeds: Google Trends RSS (`https://trends.google.com/trending/rss?geo=US`), Yahoo Finance / Reuters RSS, or CoinDesk breakout feeds.
    - Employs `GEMINI_TREND_ANALYSIS_PROMPT` to analyze raw headlines, filter noise, and synthesize 5 high-converting video topics tailored for US/foreign tier-1 audiences.
    - Output includes: `trending_headline`, `viral_video_title`, `psychological_hook`, `search_volume_indicator`, `estimated_rpm_usd`, and `urgency_level` ("BREAKING", "RISING", "EVERGREEN").
    - Exposed via `POST /api/youtube/studio/trend-radar` (params: `niche`, `geo="US"`, `limit=5`).
  - **Dual AI Video Provider (Google Direct + Fal.ai Veo 3.1):**
    - Provide a unified parameter `video_provider: "google_direct" | "fal_ai"` across all studio endpoints.
    - If `video_provider == "fal_ai"`:
      - Support Fal.ai Veo 3.1 model: `fal-ai/veo3.1/reference-to-video` (Image-to-Video from anchor image) and `fal-ai/veo3.1/first-last-frame-to-video` (Interpolated motion between two keyframes).
      - Check `FAL_KEY` environment variable. If present, dispatch asynchronous HTTP request to Fal queue, poll or await result, download rendered MP4.
      - If `FAL_KEY` is missing or API errors, gracefully fall back to Google Direct / Optical Flow animation with clear log warning.
- **Non-Functional Requirements:**
  - Zero disruption to existing workflow: `video_provider` defaults to `google_direct`.
  - Resilience: RSS network timeouts or parsing errors must gracefully fall back to curated high-RPM evergreen trends.

## Architecture
```
[ Google Trends RSS / Financial Feeds ]
                 │
                 ▼
[ Gemini 2.0 Trend Radar Analyzer ]
                 │
                 ▼
         Top 5 Viral Angles
                 │
                 ▼
      [ User Selection / Auto-Queue ]
                 │
                 ▼
    ┌───────────────────────────┐
    │  Dual Provider Selector   │
    └─────────────┬─────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 [ Google Direct ]     [ Fal.ai Veo 3.1 ]
 Imagen 3 Anchors      reference-to-video
 + Veo I2V Engine      + first-last-frame
        │                   │
        └─────────┬─────────┘
                  ▼
   Optical Flow Retiming Engine
```

## Related Code Files
- Modify: `bridge/google_ai_service.py`:
  - Add `GEMINI_TREND_ANALYSIS_PROMPT`.
  - Add `fetch_trending_rss_feed()`.
  - Add `analyze_trends_with_gemini()`.
  - Add `generate_fal_ai_veo_clip()`.
  - Update `generate_i2v_veo_clip()` to route based on `provider`.
- Modify: `bridge/main.py`:
  - Add `StudioTrendRadarRequest`, endpoint `POST /api/youtube/studio/trend-radar`.
  - Add `video_provider` field to `StudioClipI2VRequest`, `StudioBatchClipsRequest`, and `StudioFullPipelineRequest`.

## Implementation Steps
1. Implement `fetch_trending_rss_feed()` in `bridge/google_ai_service.py` to retrieve trending XML items from Google Trends or Yahoo Finance.
2. Implement `analyze_trends_with_gemini()` using Gemini 2.0 Flash to transform raw news items into YouTube-ready concepts.
3. Implement `generate_fal_ai_veo_clip()` supporting Fal.ai Veo 3.1 API with base64/URL image upload and queue status polling.
4. Update `generate_i2v_veo_clip()` with `provider` parameter routing between Google Direct and Fal.ai.
5. Expose `POST /api/youtube/studio/trend-radar` in `bridge/main.py` and test with real/mock requests.

## Success Criteria
- [ ] `POST /api/youtube/studio/trend-radar` returns 5 curated viral angles with psychological hooks and estimated RPM.
- [ ] Dual provider toggle successfully routes to Fal.ai when selected and falls back gracefully when `FAL_KEY` is omitted.
- [ ] No regression on existing Google Veo / Imagen 3 generation pipeline.

## Risk Assessment
- **Risk:** Fal.ai API response time for Veo 3.1 can range from 30s to 120s per clip.
- **Mitigation:** Implement batch queueing with a timeout ceiling and automatic retry/fallback to Google Direct optical flow retiming if Fal queue exceeds threshold.
