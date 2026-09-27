# AGENTS.md — Global Multi-Agent System Rules

This file defines the operational guidelines for all AI agents working on the **trading-podcast** repository.

---

## 1. PROJECT SPECIFICATION
- **Repository**: `trading-podcast`
- **Primary Domain**: Autonomous Quantitative Financial Market Intelligence + AI-Powered Faceless YouTube & Shorts Video Studio.
- **Key Modules**:
  - `bridge/`: FastAPI orchestration service for FFmpeg assembly, Gemini 2.0, Google Veo 3 / Fal.ai Veo 3.1, and TTS.
  - `n8n/`: Low-code orchestration pipeline (Workflow ID `YTUBEFaceless001`, 23 active nodes).
  - `scripts/`: Operational utilities (session restore, data export).
  - `docs/`: Comprehensive architecture and configuration guides.

---

## 2. AGENT OPERATING INVARIANTS
1. **FFmpeg Video Precision**: Video clips must be rendered in 1080p ($1920 \times 1080$ for long video, $1080 \times 1920$ for shorts) at 30 fps, with proper SAR/DAR and audio crossfading (`afade`).
2. **Subtitles Safe Zone**: Vertical kinetic ASS subtitles must have `PlayResX: 1080`, `PlayResY: 1920`, font size 44–48pt, and `margin_v: 520` to guarantee visibility above mobile UI overlays.
3. **No Breaking Changes**: Preserve existing API endpoints (`/api/charts/capture`, `/api/notebooklm/*`, `/api/pipeline/*`).
4. **Security Integrity**: Keep all API keys and OAuth tokens strictly in environment variables.

---

## 3. SESSION RESTORATION & CONTEXT
- To resume the exact conversational context of this project on a new workstation:
  ```bash
  python3 scripts/restore_antigravity.py
  agy --resume d7d40cd3-2a98-4270-99bf-102cbafd0350
  ```
- Detailed turn-by-turn logs: See `docs/chat_history/`.
