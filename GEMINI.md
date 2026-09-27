# ANTIGRAVITY PROJECT MEMORY & SYSTEM RULES

Welcome to **trading-podcast** — an autonomous AI media production and quantitative market intelligence studio.

---

## 1. PROJECT ARCHITECTURE & PORTS

| Service | Port | Technology | Purpose |
| :--- | :--- | :--- | :--- |
| **Trading Podcast Bridge** | `:8010` | FastAPI, Python 3.11, FFmpeg 6.1.1, Google GenAI SDK | Central orchestration bridge for video rendering, TTS, Trend Radar, and AI clip generation |
| **n8n Automation Engine** | `:5678` | n8n (Community Edition), Docker | 23-node autonomous workflow (`YTUBEFaceless001`), mobile web form triggers, daily cron |
| **TradingAgents Backend** | `:8000` | FastAPI, LangGraph, LLM agents | Quantitative market research agents (Warren Buffett, Technical Analyst, Risk Manager) |
| **TradingAgents Frontend** | `:5173` | React, Vite | Dashboard UI for market analysis |

---

## 2. CORE CAPABILITIES (STUDIO V3.0 ULTRA)

1. **24h Trend Radar**:
   - Parses Google Trends US RSS (`https://trends.google.com/trending/rss?geo=US`) and Yahoo Finance RSS.
   - Synthesizes top 5 breakout video concepts with estimated RPM ($35 - $65), curiosity hooks, and content angles via Gemini 2.0 Flash.
2. **Dual AI Video Provider**:
   - `google_direct`: Native Google Imagen 3 and Google Veo 3 on Vertex AI.
   - `fal_ai`: Fal.ai Veo 3.1 (`fal-ai/veo3.1/reference-to-video`).
   - Zero-crash fallback: Automatic optical flow motion retiming when external AI provider fails or is unconfigured.
3. **Multi-Format Repurposing (1 Long -> 3 Shorts 9:16)**:
   - Slices master 16:9 video into 3 high-intensity vertical shorts (Hook, Climax, Twist).
   - Generates Alex Hormozi kinetic typography with neon gold highlights (`&H0000E5FF`).
   - Safe zone: `margin_v: 520` in $1080 \times 1920$ resolution to prevent mobile UI button occlusion on TikTok and YouTube Shorts.
4. **Mobile Web Form Trigger**:
   - Form URL: `http://localhost:5678/form/create-video` allows full studio dispatch directly from a smartphone.

---

## 3. STRICT SYSTEM INVARIANTS & GUIDELINES

1. **Zero Dummy Data**: Never return hardcoded mock data when live systems or fallback algorithms can produce real or genuine synthesized outputs.
2. **Backward Compatibility**: Any modification to `bridge/main.py` or `bridge/video_engine.py` must maintain 100% backward compatibility with existing NotebookLM and TradingAgents endpoints.
3. **Audio Mastering**: Voiceover audio must always duck background music by -22dB, and SFX (Whoosh, Ding, Pop) must be synced to scene transitions.
4. **Clean Code & Secrets**: Never commit `.env`, `storage_state.json`, or unredacted API keys.

---

## 4. RESUMING CHAT SESSIONS ON A NEW COMPUTER

If you clone this repository onto a new machine:
1. Run the one-command restore script:
   ```bash
   python3 scripts/restore_antigravity.py
   ```
2. Resume the primary Studio development session:
   ```bash
   agy --resume d7d40cd3-2a98-4270-99bf-102cbafd0350
   ```
3. Or resume the original Trading Podcast foundation session:
   ```bash
   agy --resume dc80f4a9-5ff0-4d5e-9a80-ffa4d985f271
   ```
4. Read the human-readable Markdown history in [docs/chat_history/](file:///home/popeye/projects/trading-podcast/docs/chat_history/README.md).
