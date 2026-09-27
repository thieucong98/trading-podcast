---
phase: 3
title: "n8n Workflow Expansion (Google Sheets, Form, Drive & Omnichannel)"
status: pending
priority: P1
effort: "2.5h"
dependencies: ["1", "2"]
---

# Phase 3: n8n Workflow Expansion (Google Sheets, Form, Drive & Omnichannel)

## Overview
Re-architect the n8n studio workflow builder (`n8n/build_youtube_workflow.py`) to build **Studio v3.0 Ultra** (`YTUBEFaceless001`). This introduces a mobile-first 2-Way Google Sheets Queue, a no-code n8n Web Form trigger, a Daily Trend Radar cron, Google Drive cloud backup, and an Omnichannel Social Dispatcher (Blotato / Upload-Post integration).

## Requirements
- **Functional Requirements:**
  - **Intake Expansion (4 Trigger Modes):**
    1. `Google Sheets Trigger`: Polls a spreadsheet queue for rows with `Status = 'PENDING'`.
    2. `n8n Form Trigger`: A sleek mobile-responsive web form at `/form/create-video` for on-the-go video creation from any smartphone.
    3. `24h Trend Radar Cron`: Scheduled trigger running daily at 7:00 AM to fetch trending topics and auto-produce videos.
    4. `Webhook & Manual Triggers`: Retained for API integration and developer testing.
  - **Expanded Centralized Settings Hub (`Global Studio v3.0 Settings`):**
    - Channel Niche, Target Audience, Visual Style.
    - `video_provider`: `"google_direct"` or `"fal_ai"`.
    - `enable_shorts_generation`: boolean (default `true`).
    - `enable_google_drive_backup`: boolean (default `true`).
    - `enable_omnichannel_dispatch`: boolean (default `false`).
    - `omnichannel_provider`: `"blotato"` or `"upload_post"`.
    - `google_sheet_id`: Target spreadsheet ID for 2-way sync.
  - **Repurposing & Backup Nodes:**
    - Node `Multi-Format Content Repurposer`: Calls `/api/youtube/studio/extract-shorts` after long video assembly.
    - Node `Google Drive Backup Station`: Uploads master video and 3 vertical shorts to Google Drive.
    - Node `Omnichannel Social Dispatcher`: Posts vertical shorts to TikTok, Reels, and YouTube Shorts via Blotato/Upload-Post webhook.
    - Node `Google Sheets 2-Way Sync Writeback`: Writes back live video links, drive links, and status to the spreadsheet row.
  - **Workflow Compilation & Deployment:**
    - Script `n8n/build_youtube_workflow.py` compiles the complete workflow JSON into `n8n/workflows/youtube_faceless_pipeline.json`.
    - Automatically update the live n8n Docker instance via n8n REST API (`http://localhost:5678/api/v1/workflows/YTUBEFaceless001`).

- **Non-Functional Requirements:**
  - Clean visual layout in n8n canvas (proper `[x, y]` coordinate spacing).
  - Robust error handling: if Google Drive or Blotato keys are not configured, the workflow logs a warning and proceeds without breaking the core video generation pipeline.

## Architecture & Node Diagram
```
[Google Sheets Trigger] ─┐
[n8n Form Trigger]       ─┼─► [Global Settings Hub] ─► [Script & Voiceover] ─► [Batch Veo Clips]
[Trend Radar Cron]       ─┤
[Manual / Webhook]       ─┘
                                                                           │
                                                                           ▼
[Google Sheets Sync] ◄─ [Drive Backup] ◄─ [Shorts Repurposer] ◄─ [Long Video Assembly]
                                                  │
                                                  ▼
                                       [Omnichannel Dispatch]
                                        (TikTok / Reels / Shorts)
```

## Related Code Files
- Modify: `n8n/build_youtube_workflow.py` (add new triggers, settings, repurposer node, drive backup node, omnichannel node, writeback node).
- Overwrite: `n8n/workflows/youtube_faceless_pipeline.json` (compiled workflow definition).

## Implementation Steps
1. Update `n8n/build_youtube_workflow.py` with the expanded 18-node topology.
2. Configure parameter mappings and JSON schema expressions for each new node.
3. Run python compiler script to generate `n8n/workflows/youtube_faceless_pipeline.json`.
4. Deploy and activate the workflow in the live n8n container (`http://localhost:5678`).
5. Validate node execution connections and JSON payload schemas.

## Success Criteria
- [ ] Workflow contains all 18 nodes properly connected with clean layout coordinates.
- [ ] Form trigger accessible at `http://localhost:5678/form/create-video`.
- [ ] Workflow executes end-to-end via Webhook / Form / Manual trigger without schema errors.
- [ ] Google Drive and Omnichannel nodes gracefully bypass when API keys are not supplied.

## Risk Assessment
- **Risk:** n8n Form trigger node requires specific form parameters schema in newer n8n versions.
- **Mitigation:** Use standard `n8n-nodes-base.formTrigger` structure with basic text/dropdown fields compatible with n8n v1.x+.
