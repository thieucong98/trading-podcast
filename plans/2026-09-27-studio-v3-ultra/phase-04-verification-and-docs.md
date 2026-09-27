---
phase: 4
title: "End-to-End Verification, QA Review & Master Docs Update"
status: pending
priority: P1
effort: "1.5h"
dependencies: ["1", "2", "3"]
---

# Phase 4: End-to-End Verification, QA Review & Master Docs Update

## Overview
Perform end-to-end integration testing in live Docker containers, run adversarial QA code review via subagent, verify generated media outputs (1 Long Video + 3 Vertical Shorts), and update the master operations documentation (`docs/OPERATIONS_AND_CONFIGURATION_GUIDE.md`).

## Requirements
- **Functional Requirements:**
  - **Live Endpoint Verification:**
    - Test `POST /api/youtube/studio/trend-radar` (verify trending topics extracted with hooks and RPM).
    - Test `POST /api/youtube/studio/extract-shorts` using existing master video (verify 3x 1080x1920 MP4 files produced).
    - Test `POST /api/youtube/studio/full-pipeline` with `generate_shorts=True` (verify long video + shorts generated in single run).
    - Test live n8n workflow execution (`POST http://localhost:5678/webhook/run-youtube-faceless`).
  - **Artifact Media Inspection:**
    - Use `ffprobe` to verify video dimensions, frame rates, audio channels, and duration accuracy.
    - Confirm visual quality of vertical kinetic subtitles (centered, high-contrast, no overflow).
  - **QA Code Review Subagent:**
    - Delegate code review to a subagent to check for type hints, edge cases, exception handling, and backward compatibility.
  - **Documentation Overhaul:**
    - Update `docs/OPERATIONS_AND_CONFIGURATION_GUIDE.md` with full Studio v3.0 Ultra configuration steps:
      - Mobile 2-Way Google Sheets Queue setup.
      - Mobile n8n Form Trigger setup.
      - 24h Trend Radar automated operation.
      - Dual Provider (Fal.ai + Google Direct) configuration.
      - Multi-Format Repurposing specs and social media distribution playbooks.
- **Non-Functional Requirements:**
  - Zero downtime of running services.
  - Zero regression on TradingAgents and NotebookLM podcast endpoints.

## Implementation Steps
1. Run automated test suite against FastAPI bridge:
   - Curl `/api/youtube/studio/trend-radar`.
   - Curl `/api/youtube/studio/extract-shorts`.
   - Curl `/api/youtube/studio/full-pipeline`.
2. Inspect generated MP4 files with `ffprobe` to confirm 1080x1920 (9:16) resolution.
3. Test n8n workflow execution in container `trading-podcast-n8n`.
4. Spawn QA subagent to conduct rigorous review.
5. Update `docs/OPERATIONS_AND_CONFIGURATION_GUIDE.md` with complete v3.0 operational guide.
6. Summarize results and present final verification report to user.

## Success Criteria
- [ ] Trend Radar returns live/mock trends with valid JSON schema.
- [ ] 3 Vertical Shorts successfully extracted with verified 1080x1920 resolution.
- [ ] n8n workflow active and responsive on port 5678.
- [ ] Subagent review passes with 0 critical issues.
- [ ] Master documentation fully reflects Studio v3.0 Ultra features.
