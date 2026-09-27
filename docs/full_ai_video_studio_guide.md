# 100% Full-AI Long Video Studio Architecture & Operation Manual

## 1. Executive Overview
This studio provides an autonomous end-to-end pipeline that transforms YouTube video ideas into high-retention, broadcast-ready 1080p long-form videos (8–12+ minutes). The entire video is composed **100% of AI-generated video clips** using the **Google Ecosystem** (Gemini 2.5 Pro, Imagen 3, Veo 3 / Flow, Google Cloud TTS) orchestrated seamlessly through **n8n** and a Python **FastAPI Video Engine Bridge**.

---

## 2. Core Architecture & Innovation: Keyframe-Seeded I2V (Image-to-Video)

### The Problem with Long-Form AI Video:
Foundation video models (such as Google Veo 3, Runway, Sora) generate clips of only 4–8 seconds. If you generate a 10-minute video using pure Text-to-Video (T2V) across 80+ clips, characters and art styles drastically mutate from shot to shot ("character drift").

### The Solution:
1. **Character & Environment Anchor Keyframes (Imagen 3)**:
   - Gemini decomposes the script into narrative beats and generates master character/setting seed anchors.
   - Google Imagen 3 renders high-resolution 16:9 master anchor keyframes (e.g. `trader_hero`, `ancestor_hunter`, `algo_server_room`).
2. **Camera-Choreographed Veo 3 Motion (Image-to-Video)**:
   - For every 4–6 second sentence, Google Veo 3 takes the anchor image as an input seed and animates it with specific camera motion choreography (`slow push-in`, `tracking pan left`, `low-angle tilt-up`, `macro focus pull`).
3. **Dynamic Optical Flow Retiming (FFmpeg Engine)**:
   - Spoken sentences vary in length (e.g. 3.8s, 5.7s, 6.4s).
   - The video engine retimes the Veo clip using FFmpeg optical flow motion compensation (`minterpolate` + `setpts`), stretching or compressing the clip smoothly without stutter or black frames.
4. **Studio-Grade Multi-Track Sound Design**:
   - Mastered voiceover stem.
   - Millisecond-accurate SFX foley:
     - `Whoosh`: placed automatically on all scene transitions.
     - `Pop`: text overlays and keyword appearances.
     - `Ding`: financial profits, positive breakthroughs.
     - `Impact`: market crashes, shock revelations.
     - `Riser`: builds suspense leading up to climactic reveals.
   - Ambient background score with automatic ducking down to -22dB during speech.
5. **Kinetic Typography Subtitles (Alex Hormozi & Vox Aesthetic)**:
   - Heavy 4px black border, 2px drop shadow, bottom-centered ASS subtitles.
   - Neon yellow/gold dynamic highlighting on numbers (`$10,000`, `95%`), shock words (`VANISHES`, `TRAP`, `CRASH`), and psychological triggers.

---

## 3. Centralized Settings Hub (Single Node Configuration)

All channel, video, and AI generation parameters are centralized in the `Global YouTube Channel Settings` node in n8n or passed via REST API payload:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `niche` | String | `Trading Psychology & Market Mysteries` | Target niche (optimized for high-RPM Tier 1 US/UK viewers) |
| `topic` | String | `""` (Auto-Ideate) | Custom topic or leave blank for Gemini viral brainstorm |
| `target_duration_mins` | Number | `10` | Video length target (8–12 mins) |
| `voice_name` | String | `en-US-Journey-D` | Natural Google Cloud Journey conversational voice |
| `visual_style` | String | `Keyframe-Seeded Veo 3 I2V Cinematic` | Visual aesthetic directive |
| `veo_mode` | String | `full_ai_video` | 100% AI video clip generation mode |
| `auto_upload_youtube`| Boolean| `false` | When true, publishes directly; when false, holds in Approval Station |
| `youtube_privacy` | String | `unlisted` | `draft` \| `unlisted` \| `public` |

---

## 4. API Endpoints Reference (`http://localhost:8010`)

### Studio Endpoints:
- `POST /api/youtube/studio/storyboard`: Breaks topic and script into keyframe anchors and 4–6s beats.
- `POST /api/youtube/studio/generate-anchor`: Generates character/scene master image with Imagen 3.
- `POST /api/youtube/studio/generate-clip-i2v`: Generates motion clip from anchor frame + camera prompt.
- `POST /api/youtube/studio/generate-clips-batch`: Concurrently generates batch of Veo clips with semaphore limit.
- `POST /api/youtube/studio/generate-anchors-and-clips`: Orchestrated node generating all anchors and Veo clips.
- `POST /api/youtube/studio/retime-clip`: Retimes any clip to exact seconds using optical flow (`minterpolate`).
- `POST /api/youtube/studio/assemble-video`: Assembles all AI clips with multi-track audio and burns kinetic subtitles.
- `POST /api/youtube/studio/full-pipeline`: End-to-end execution of the complete pipeline.
- `POST /api/youtube/upload`: Prepares and dispatches YouTube video with privacy status and metadata.
- `GET /api/download/video/{filename}`: Direct browser download link for generated video.
- `GET /api/download/thumbnail/{filename}`: Direct browser download link for generated thumbnail.

---

## 5. Live n8n Studio Workflow Integration

- **Workflow Name**: `YouTube Faceless Full-AI Video Studio (Google Veo 3 / Flow + n8n)`
- **Workflow ID**: `YTUBEFaceless001`
- **Webhook Endpoint**: `POST http://localhost:5678/webhook/run-youtube-faceless`
- **Schedule**: Cron trigger set to Mon, Wed, Fri at 8:00 AM (customizable in UI).

### Triggering via cURL:
```bash
curl -X POST http://localhost:5678/webhook/run-youtube-faceless \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Why 95% of Traders Lose Money (The Dopamine Trap)",
    "target_duration_mins": 10,
    "privacy": "unlisted"
  }'
```
