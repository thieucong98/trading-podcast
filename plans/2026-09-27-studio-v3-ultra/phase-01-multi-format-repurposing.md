---
phase: 1
title: "Multi-Format Repurposing Engine (1 Long -> 3 Shorts 9:16)"
status: pending
priority: P1
effort: "2h"
dependencies: []
---

# Phase 1: Multi-Format Repurposing Engine (1 Long -> 3 Shorts 9:16)

## Overview
Develop an autonomous content repurposing engine inside `bridge/video_engine.py` that takes an assembled 16:9 Long-Form Video (or scene cutlist) and programmatically extracts 3 standalone high-retention Vertical Shorts (9:16, 1080x1920) formatted for YouTube Shorts, TikTok, and Instagram Reels, complete with vertical Alex Hormozi kinetic typography.

## Requirements
- **Functional Requirements:**
  - `extract_vertical_shorts(source_video_path, scenes_data, output_dir, num_shorts=3, target_duration=30-50s)`:
    - Automatically select 3 distinct narrative arcs:
      1. Short 1 (The Hook): First 30–45s containing the visceral hook and counterintuitive revelation.
      2. Short 2 (The Climax / Case Study): The peak conflict scene in the middle of the video.
      3. Short 3 (The Core Twist / Moral): The final paradigm shift or warning.
    - Transform 16:9 landscape video into 9:16 vertical video using dynamic FFmpeg filter chains:
      - Primary mode (Center punch-crop): `crop=ih*(9/16):ih:(iw-ow)/2:0,scale=1080:1920`.
      - Blurred aesthetic mode (for wide infographics): Blurred background + centered landscape video.
    - Vertical Kinetic Subtitle Styling:
      - Dedicated ASS subtitle script generator `generate_vertical_kinetic_ass_subtitles()` with larger font (44pt), centered alignment (`Alignment=2` or `10`), high vertical margin (`MarginV=520`), bold yellow/cyan keyword highlights, and 4px black drop shadow.
  - FastAPI Endpoint:
    - Expose `POST /api/youtube/studio/extract-shorts`: Accepts `video_path`, `scenes_data`, `style` ("crop" | "blurred_pad"), returns metadata and download URLs for each short.
- **Non-Functional Requirements:**
  - Fast execution: use stream copying or fast x264 encoding preset (`fast` / `crf 19`).
  - Audio continuity: ensure no clipping or audio pop at boundary cuts by adding a 0.05s micro-fade in/out.

## Architecture
```
Long Video MP4 (16:9 1920x1080)
       │
       ▼
Beat / Scene Intensity Slicer (Timestamp & Cue Analysis)
       ├── Slice 1: Hook Arc (0:00 -> 0:35)
       ├── Slice 2: Climax Arc (e.g. 3:20 -> 4:00)
       └── Slice 3: Twist Arc (e.g. 7:15 -> 7:55)
       │
       ▼
FFmpeg 9:16 Conversion (Center Crop + Scaler to 1080x1920)
       │
       ▼
Vertical ASS Subtitle Burn-In (Font size 44, MarginV 520, Neon Highlights)
       │
       ▼
3x Vertical Short MP4s (9:16 1080x1920) Ready for YouTube Shorts / TikTok / Reels
```

## Related Code Files
- Modify: `bridge/video_engine.py` (add `extract_vertical_shorts`, `generate_vertical_kinetic_ass_subtitles`).
- Modify: `bridge/main.py` (add `StudioExtractShortsRequest`, endpoint `POST /api/youtube/studio/extract-shorts`, and update `StudioFullPipelineRequest` with `generate_shorts: bool = True`).

## Implementation Steps
1. Add `generate_vertical_kinetic_ass_subtitles()` in `bridge/video_engine.py` configuring ASS script header for `PlayResX: 1080`, `PlayResY: 1920`, `FontSize: 46`, `MarginV: 520`.
2. Add `extract_vertical_shorts()` in `bridge/video_engine.py`:
   - Parse `scenes_data` or timeline duration to determine start/end timestamps for 3 high-energy segments.
   - Build FFmpeg command slicing audio/video, applying vertical crop filter and burning vertical subtitles.
   - Save output as `short_01_hook.mp4`, `short_02_climax.mp4`, `short_03_twist.mp4`.
3. Add Pydantic model `StudioExtractShortsRequest` and endpoint `POST /api/youtube/studio/extract-shorts` in `bridge/main.py`.
4. Update `POST /api/youtube/studio/full-pipeline` to optionally trigger shorts extraction if `generate_shorts` is enabled.
5. Unit test and verify vertical MP4 outputs with `ffprobe` (confirm 1080x1920 resolution, 9:16 aspect ratio).

## Success Criteria
- [ ] Endpoint `POST /api/youtube/studio/extract-shorts` generates 3 valid MP4 files.
- [ ] Video resolution verified as 1080x1920 (9:16) at 30 fps.
- [ ] Subtitles are legible, vertically centered above TikTok/Reels UI overlay, and synchronized with audio.
- [ ] File size is optimized (< 25 MB per short) with H.264 / AAC codecs.

## Risk Assessment
- **Risk:** Center-cropping might cut off important text or graphic elements on the far left/right of a 16:9 frame.
- **Mitigation:** Provide an optional `crop_mode="blurred_background"` fallback where the original 16:9 frame is fitted centered over a Gaussian-blurred vertical background.
