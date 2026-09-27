---
title: "Studio v3.0 Ultra: Mobile-First, Trend-Aware, Multi-Format Autonomous Video Studio"
description: "Expand the Full-AI Video Studio with 2-Way Google Sheets/Web Form triggers, 24h Trend Radar, Dual AI Provider (Google Direct + Fal.ai Veo 3.1), Multi-Format Content Repurposing (1 Long -> 3 Shorts 9:16), Google Drive backup, and Omnichannel Dispatch."
status: completed
priority: P1
effort: "8h"
branch: "main"
tags: [youtube, veo3, fal-ai, n8n, shorts, trend-radar, google-sheets, optical-flow]
blockedBy: []
blocks: []
created: "2026-09-27"
---

# Studio v3.0 Ultra: Autonomous Multi-Format AI Video Studio

## Overview
Studio v3.0 Ultra bridges the remaining gap between our professional long-form AI rendering engine and international top-tier workflows (such as Dr. Firas's Blotato/Veo templates and Davide Boizza's Google Drive pipeline). It adds phone-based 2-Way Google Sheets & Web Form triggers, a 24-hour Trend Radar for automated viral topic discovery, a Dual AI Video Provider (Google Direct + Fal.ai Veo 3.1 & First-Last-Frame), a 1 Long Video -> 3 Vertical Shorts (9:16) Repurposing Engine, and automated Google Drive backup with optional omnichannel social dispatch.

## Cross-Plan Dependencies
- Preceded by: `plans/plan-full-ai-video-studio.md` (Completed & Verified 100%).
- All existing endpoints (`/api/podcast/*`, `/api/youtube/*`, `/api/youtube/studio/*`) remain 100% backward compatible.

## Phases

| Phase | Name | Priority | Status | Effort |
|-------|------|----------|--------|--------|
| 1 | [Multi-Format Repurposing Engine (1 Long -> 3 Shorts 9:16)](./phase-01-multi-format-repurposing.md) | P1 | Completed | 2h |
| 2 | [24h Trend Radar & Dual AI Video Provider (Google + Fal.ai)](./phase-02-trend-radar-and-dual-provider.md) | P1 | Completed | 2h |
| 3 | [n8n Workflow Expansion (Google Sheets, Form, Drive & Omnichannel)](./phase-03-n8n-workflow-expansion.md) | P1 | Completed | 2.5h |
| 4 | [End-to-End Verification, QA Review & Master Docs Update](./phase-04-verification-and-docs.md) | P1 | Completed | 1.5h |

## Key Architecture & Integration Points

```mermaid
flowchart TD
    subgraph INTAKE["1. Mobile & Multi-Channel Intake"]
        A1["📱 Google Sheets 2-Way Queue<br/>(Phone / Mobile Access)"] --> HUB["Global Channel Settings Hub"]
        A2["🌐 n8n Web Form Trigger<br/>(One-Click Submit)"] --> HUB
        A3["📡 24h Trend Radar Cron<br/>(Google Trends RSS + Gemini)"] --> HUB
        A4["⚡ Manual / Webhook API"] --> HUB
    end

    subgraph ENGINE["2. Production & Dual AI Engine"]
        HUB --> SCR["Script & Voiceover<br/>(Gemini 2.0 + Cloud TTS)"]
        SCR --> DUAL{"Dual Video Provider<br/>Toggle"}
        DUAL -->|Google Direct| G_VEO["Google Imagen 3 Anchors<br/>+ Veo 3 I2V"]
        DUAL -->|Fal.ai Veo 3.1| F_VEO["Fal.ai Veo 3.1 /<br/>First-Last-Frame"]
        G_VEO --> RETIME["Optical Flow Retiming<br/>(minterpolate + setpts)"]
        F_VEO --> RETIME
        RETIME --> LONG["Long Video Assembly (16:9)<br/>Multi-track Foley + Hormozi ASS"]
    end

    subgraph REPURPOSE["3. Content Repurposing Engine"]
        LONG --> SHORTS["Multi-Format Slicer<br/>(1 Long -> 3 Shorts 9:16)<br/>Crop + Vertical ASS Subtitles"]
        SHORTS --> S1["Short 1: The 3s Hook"]
        SHORTS --> S2["Short 2: The Climax Beat"]
        SHORTS --> S3["Short 3: The Mind-Bending Twist"]
    end

    subgraph DISPATCH["4. Cloud Backup & Omnichannel Dispatch"]
        LONG --> DRIVE["Google Drive Cloud Backup"]
        S1 --> DRIVE
        S2 --> DRIVE
        S3 --> DRIVE
        LONG --> YT["YouTube Data API v3<br/>(Long Video + 3 A/B Thumbnails)"]
        S1 --> OMNI["Omnichannel Dispatcher<br/>(Blotato / Upload-Post)"]
        S2 --> OMNI
        S3 --> OMNI
        DRIVE --> SYNC["Google Sheets Writeback<br/>(Update Status='COMPLETED' + URLs)"]
        YT --> SYNC
    end
```

## Dependencies
- FastAP/Uvicorn bridge running in `trading-podcast-bridge` container (port 8010).
- n8n instance running in `trading-podcast-n8n` container (port 5678).
- FFmpeg with `minterpolate`, `zoompan`, `crop`, `boxblur`, `ass/subtitles` filters.
- Optional external credentials: `FAL_KEY` (Fal.ai), `BLOTATO_API_KEY` or `UPLOAD_POST_API_KEY`, `GOOGLE_DRIVE_CREDENTIALS`.
