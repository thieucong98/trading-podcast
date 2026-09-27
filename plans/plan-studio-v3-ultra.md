# Implementation Plan: Studio v3.0 Ultra (Autonomous Multi-Format AI Video Studio)

## Status: COMPLETED & VERIFIED (100%)
**Location:** [plans/2026-09-27-studio-v3-ultra/plan.md](file:///home/popeye/projects/trading-podcast/plans/2026-09-27-studio-v3-ultra/plan.md)

---

## 1. Overview & System Mission
Following the in-depth comparative benchmark against top international n8n video studios (`10358`, `12462`, `4846`), **Studio v3.0 Ultra** bridges the final UX, distribution, and automation gaps to make our studio truly world-class, autonomous, and mobile-friendly.

### Core Upgrades in v3.0 Ultra:
1. **📱 Mobile 2-Way Google Sheets & Web Form Interface:** Trigger video generation directly from a smartphone spreadsheet or no-code web form; automatically sync live links (MP4, YouTube, Drive) back upon completion.
2. **📡 24h Trend Radar (Auto Trend Scout):** Algorithmic radar scraping Google Trends RSS & financial feeds; Gemini 2.0 Flash synthesizes top 5 breakout angles with psychological hooks.
3. **⚡ Dual AI Video Provider (Google Direct + Fal.ai Veo 3.1):** Flexible provider switching (`google_direct` vs `fal_ai` Veo 3.1 `reference-to-video` / `first-last-frame-to-video`) with automated optical flow fallback.
4. **✂️ Multi-Format Content Repurposing (1 Long -> 3 Vertical Shorts 9:16):** Programmatically extract 3 high-intensity beats into 1080x1920 vertical shorts with Alex Hormozi kinetic typography for TikTok, Reels, and YouTube Shorts.
5. **☁️ Cloud Backup & Omnichannel Dispatch:** Automated backup to Google Drive; modular integration for Blotato / Upload-Post to blast across all platforms.

---

## 2. Phase Breakdown

### [Phase 1: Multi-Format Repurposing Engine (1 Long -> 3 Shorts 9:16)](file:///home/popeye/projects/trading-podcast/plans/2026-09-27-studio-v3-ultra/phase-01-multi-format-repurposing.md)
- **Objective:** Add smart slicer in `bridge/video_engine.py` to produce 3 vertical 9:16 (1080x1920) clips with punch zoom and vertical Hormozi subtitles.
- **Key Files:** `bridge/video_engine.py`, `bridge/main.py`.
- **Endpoints:** `POST /api/youtube/studio/extract-shorts`.

### [Phase 2: 24h Trend Radar & Dual AI Video Provider](file:///home/popeye/projects/trading-podcast/plans/2026-09-27-studio-v3-ultra/phase-02-trend-radar-and-dual-provider.md)
- **Objective:** Build Trend Radar engine (Google Trends RSS + Gemini) and Fal.ai Veo 3.1 adapter.
- **Key Files:** `bridge/google_ai_service.py`, `bridge/main.py`.
- **Endpoints:** `POST /api/youtube/studio/trend-radar`, provider toggle parameter across all video generation calls.

### [Phase 3: n8n Workflow Expansion](file:///home/popeye/projects/trading-podcast/plans/2026-09-27-studio-v3-ultra/phase-03-n8n-workflow-expansion.md)
- **Objective:** Upgrade `n8n/build_youtube_workflow.py` to 18-node topology with Google Sheets, Form Trigger, Google Drive Backup, and Omnichannel Dispatcher.
- **Key Files:** `n8n/build_youtube_workflow.py`, `n8n/workflows/youtube_faceless_pipeline.json`.
- **Container Target:** Deploy into `trading-podcast-n8n` (`http://localhost:5678`).

### [Phase 4: End-to-End Verification, QA Review & Master Docs](file:///home/popeye/projects/trading-podcast/plans/2026-09-27-studio-v3-ultra/phase-04-verification-and-docs.md)
- **Objective:** Verify live container execution, test media artifacts with `ffprobe`, perform subagent QA code review, and update `docs/OPERATIONS_AND_CONFIGURATION_GUIDE.md`.

---

## 3. Backward Compatibility & Safety Guarantees
- 100% backward compatible with existing Trading Podcast (NotebookLM) and YouTube Studio v2.5 pipelines.
- Modular toggles: Google Drive, Blotato, and Fal.ai can be enabled/disabled independently without disrupting the primary engine.
