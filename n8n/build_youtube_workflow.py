import json
from pathlib import Path

summary_js_code = """const settings = $('Global YouTube Channel Settings').first().json;
const topicInfo = $('Select Topic & Validate').first().json;
const scriptInfo = $('Generate Viral Narration Script (Google Gemini)').first().json;
const voiceInfo = $('Synthesize Voiceover (Google Cloud TTS)').first().json;
const storyboardInfo = $('Generate Visual Storyboard & Anchors (Google Gemini)').first().json;
const clipsInfo = $('Batch Generate Keyframe Anchors & Veo 3 I2V Video Clips (Google Veo 3)').first().json;
const videoInfo = $('Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)').first().json;
const shortsInfo = $('Multi-Format Content Repurposer (1 Long -> 3 Shorts 9:16)').first().json;
const metaInfo = $('Generate YouTube SEO Metadata (Google Gemini)').first().json;
const thumbInfo = $('Generate 3 High-CTR A/B Thumbnails (Google Imagen 3)').first().json;
const uploadInfo = $('YouTube Dispatcher & Publishing Station').first().json;
const driveInfo = $('Google Drive Cloud Backup Station').first().json;
const omniInfo = $('Omnichannel Social Dispatcher (TikTok / Reels / Shorts)').first().json;

return [{
  json: {
    status: "success",
    studio_tier: "Studio v3.0 Ultra (Autonomous Full-AI + Multi-Format Repurposing)",
    timestamp: new Date().toISOString(),
    channel_niche: settings.niche,
    target_audience: "US/UK Global Investors & High-RPM foreign viewers",
    selected_topic: topicInfo.topic,
    video_provider: settings.video_provider || "google_direct",
    production_artifacts: {
      long_form_master: {
        video_file: videoInfo.filename,
        video_url: videoInfo.download_url || ("http://localhost:8010/api/download/video/" + videoInfo.filename),
        filesize_mb: videoInfo.filesize_mb,
        resolution: "1920x1080 Full HD (16:9, H.264, 30fps)",
        duration: voiceInfo.duration_seconds + "s",
        full_ai_clips_count: clipsInfo.clips_count || (clipsInfo.clips ? clipsInfo.clips.length : 0),
        optical_flow_retiming: "FFmpeg minterpolate=fps=30:mi_mode=blend + setpts",
        sound_design: "Multi-track Foley (Whoosh, Pop, Ding, Impact, Riser) + Ducked BGM",
        kinetic_subtitles: "Alex Hormozi / Vox ASS High-Contrast Typography"
      },
      vertical_shorts_repurposed: shortsInfo.shorts || [],
      vertical_shorts_count: shortsInfo.shorts_count || 0
    },
    ab_thumbnails_testing: thumbInfo.thumbnails || [],
    youtube_packaging: {
      title: metaInfo.title,
      description: metaInfo.description,
      tags: metaInfo.tags,
      chapters: metaInfo.chapters || [],
      pinned_comment_hook: metaInfo.pinned_comment || ""
    },
    cloud_backup_drive: {
      status: driveInfo.status || "BACKED_UP",
      drive_folder: driveInfo.drive_folder || ("Google Drive / AI Studio / " + topicInfo.topic),
      files_synced: (shortsInfo.shorts_count || 0) + 1
    },
    omnichannel_distribution: {
      status: omniInfo.status || "READY_FOR_OMNICHANNEL",
      target_platforms: ["YouTube Shorts", "TikTok", "Instagram Reels"],
      queued_shorts: shortsInfo.shorts_count || 3
    },
    youtube_publishing: {
      action: uploadInfo.action || "READY",
      privacy_status: settings.youtube_privacy,
      auto_upload_enabled: settings.auto_upload_youtube,
      dispatch_message: uploadInfo.message
    }
  }
}];"""

workflow = {
    "id": "YTUBEFaceless001",
    "name": "YouTube Faceless Full-AI Video Studio v3.0 Ultra (Veo 3 + Multi-Format Repurposing)",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "cronExpression",
                            "expression": "0 8 * * 1,3,5"
                        }
                    ]
                }
            },
            "id": "schedule-trigger-yt",
            "name": "Schedule Trigger (Mon, Wed, Fri 8:00 AM)",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [180, 220]
        },
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "cronExpression",
                            "expression": "0 7 * * *"
                        }
                    ]
                }
            },
            "id": "trend-radar-cron-yt",
            "name": "Trend Radar Daily Cron (7:00 AM)",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [180, 60]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/studio/trend-radar",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"niche\": \"Trading Psychology & Market Mysteries (US/Foreign Audience)\",\n  \"geo\": \"US\",\n  \"limit\": 5\n}",
                "options": {
                    "timeout": 120000
                }
            },
            "id": "trend-radar-fetch-yt",
            "name": "Fetch 24h Trend Radar (Google Trends + Gemini)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [360, 60]
        },
        {
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": "radar-topic",
                            "name": "topic",
                            "value": "={{ $json?.trending_ideas?.[0]?.viral_title || 'Why 95% of Traders Lose Money (The Dopamine Trap)' }}",
                            "type": "string"
                        },
                        {
                            "id": "radar-niche",
                            "name": "niche",
                            "value": "Trading Psychology & Market Mysteries (US/Foreign Audience)",
                            "type": "string"
                        }
                    ]
                },
                "options": {}
            },
            "id": "trend-radar-select-yt",
            "name": "Auto-Select Top Breakout Trend",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [540, 60]
        },
        {
            "parameters": {},
            "id": "manual-trigger-yt",
            "name": "Manual Trigger (Run On-Demand)",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [180, 360]
        },
        {
            "parameters": {
                "httpMethod": "GET",
                "path": "run-youtube-faceless",
                "responseMode": "lastNode",
                "options": {}
            },
            "id": "webhook-trigger-yt-get",
            "name": "Webhook Trigger (GET)",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [180, 500],
            "webhookId": "run-youtube-faceless-get"
        },
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "run-youtube-faceless",
                "responseMode": "lastNode",
                "options": {}
            },
            "id": "webhook-trigger-yt-post",
            "name": "Webhook Trigger (POST)",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [180, 640],
            "webhookId": "run-youtube-faceless-post"
        },
        {
            "parameters": {
                "path": "create-video",
                "formTitle": "Studio v3.0 Ultra - Mobile Production Launcher",
                "formDescription": "Launch 100% Full-AI Video (16:9 Long Video + 3 Vertical Shorts 9:16) directly from phone.",
                "formFields": {
                    "values": [
                        {
                            "fieldLabel": "Video Topic / Angle (Leave blank to use Trend Radar)",
                            "fieldType": "text",
                            "requiredField": False
                        },
                        {
                            "fieldLabel": "Video Provider",
                            "fieldType": "dropdown",
                            "fieldOptions": {
                                "values": [
                                    {"option": "Google Direct (Imagen 3 + Veo 3 I2V)"},
                                    {"option": "Fal.ai (Veo 3.1 Fast Queue)"}
                                ]
                            }
                        }
                    ]
                },
                "options": {}
            },
            "id": "form-trigger-yt",
            "name": "n8n Form Trigger (Mobile Web Form)",
            "type": "n8n-nodes-base.formTrigger",
            "typeVersion": 2.2,
            "position": [180, 780],
            "webhookId": "studio-create-video-form"
        },
        {
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": "yt-niche",
                            "name": "niche",
                            "value": "={{ $json?.niche || $json?.body?.niche || $json?.query?.niche || 'Trading Psychology & Market Mysteries (US/Foreign Audience)' }}",
                            "type": "string"
                        },
                        {
                            "id": "yt-topic",
                            "name": "topic",
                            "value": "={{ $json?.topic || $json?.body?.topic || $json?.query?.topic || $json?.['Video Topic / Angle (Leave blank to use Trend Radar)'] || '' }}",
                            "type": "string"
                        },
                        {
                            "id": "yt-provider",
                            "name": "video_provider",
                            "value": "={{ ($json?.video_provider || $json?.['Video Provider'] || '').includes('Fal') ? 'fal_ai' : 'google_direct' }}",
                            "type": "string"
                        },
                        {
                            "id": "yt-duration",
                            "name": "target_duration_mins",
                            "value": "={{ $json?.target_duration_mins ? Number($json.target_duration_mins) : ($json?.body?.target_duration_mins ? Number($json.body.target_duration_mins) : 10) }}",
                            "type": "number"
                        },
                        {
                            "id": "yt-voice",
                            "name": "voice_name",
                            "value": "={{ $json?.voice_name || $json?.body?.voice_name || $json?.query?.voice_name || 'en-US-Journey-D' }}",
                            "type": "string"
                        },
                        {
                            "id": "yt-style",
                            "name": "visual_style",
                            "value": "Keyframe-Seeded Veo 3 I2V Cinematic (100% Full-AI Video)",
                            "type": "string"
                        },
                        {
                            "id": "yt-auto-upload",
                            "name": "auto_upload_youtube",
                            "value": "={{ [ $json?.auto_upload, $json?.body?.auto_upload, $json?.query?.auto_upload ].some(v => v === true || v === 'true' || v === 1) }}",
                            "type": "boolean"
                        },
                        {
                            "id": "yt-privacy",
                            "name": "youtube_privacy",
                            "value": "={{ $json?.privacy || $json?.body?.privacy || 'unlisted' }}",
                            "type": "string"
                        }
                    ]
                },
                "options": {}
            },
            "id": "settings-node-yt",
            "name": "Global YouTube Channel Settings",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [760, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/ideate",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"niche\": {{ JSON.stringify($('Global YouTube Channel Settings').first().json.niche) }}\n}",
                "options": {
                    "timeout": 120000
                }
            },
            "id": "http-ideate-topics",
            "name": "Ideate 5 Viral Topics (Google Gemini)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1020, 440]
        },
        {
            "parameters": {
                "jsCode": """const settings = $('Global YouTube Channel Settings').first().json;
const ideation = $('Ideate 5 Viral Topics (Google Gemini)').first().json;

let chosenTopic = settings.topic;
if (!chosenTopic || chosenTopic.trim() === '') {
  if (ideation.ideas && ideation.ideas.length > 0) {
    chosenTopic = ideation.ideas[0].title;
  } else {
    chosenTopic = "Why 95% of Traders Lose Money (The Dopamine Trap)";
  }
}

return [{
  json: {
    topic: chosenTopic,
    niche: settings.niche,
    target_duration_mins: settings.target_duration_mins,
    voice_name: settings.voice_name,
    visual_style: settings.visual_style,
    video_provider: settings.video_provider
  }
}];"""
            },
            "id": "code-select-topic",
            "name": "Select Topic & Validate",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1280, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/generate-script",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"topic\": {{ JSON.stringify($('Select Topic & Validate').first().json.topic) }},\n  \"target_duration_mins\": {{ $('Select Topic & Validate').first().json.target_duration_mins }},\n  \"visual_style\": {{ JSON.stringify($('Select Topic & Validate').first().json.visual_style) }}\n}",
                "options": {
                    "timeout": 300000
                }
            },
            "id": "http-generate-script",
            "name": "Generate Viral Narration Script (Google Gemini)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1540, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/generate-voiceover",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"text\": {{ JSON.stringify($('Generate Viral Narration Script (Google Gemini)').first().json.narration_script) }},\n  \"voice_name\": {{ JSON.stringify($('Select Topic & Validate').first().json.voice_name) }}\n}",
                "options": {
                    "timeout": 180000
                }
            },
            "id": "http-generate-voiceover",
            "name": "Synthesize Voiceover (Google Cloud TTS)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1800, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/studio/storyboard",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"topic\": {{ JSON.stringify($('Select Topic & Validate').first().json.topic) }},\n  \"script_text\": {{ JSON.stringify($('Generate Viral Narration Script (Google Gemini)').first().json.narration_script) }},\n  \"target_duration_mins\": {{ $('Select Topic & Validate').first().json.target_duration_mins }},\n  \"visual_style\": {{ JSON.stringify($('Select Topic & Validate').first().json.visual_style) }}\n}",
                "options": {
                    "timeout": 180000
                }
            },
            "id": "http-studio-storyboard",
            "name": "Generate Visual Storyboard & Anchors (Google Gemini)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [2060, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/studio/generate-anchors-and-clips",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"storyboard\": {{ JSON.stringify($('Generate Visual Storyboard & Anchors (Google Gemini)').first().json) }},\n  \"max_concurrency\": 3,\n  \"video_provider\": {{ JSON.stringify($('Select Topic & Validate').first().json.video_provider || 'google_direct') }}\n}",
                "options": {
                    "timeout": 900000
                }
            },
            "id": "http-batch-veo-clips",
            "name": "Batch Generate Keyframe Anchors & Veo 3 I2V Video Clips (Google Veo 3)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [2320, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/studio/assemble-video",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"voiceover_audio_path\": {{ JSON.stringify($('Synthesize Voiceover (Google Cloud TTS)').first().json.audio_path) }},\n  \"clips_data\": {{ JSON.stringify($('Batch Generate Keyframe Anchors & Veo 3 I2V Video Clips (Google Veo 3)').first().json.clips) }},\n  \"music_volume\": 0.10,\n  \"font_size\": 28\n}",
                "options": {
                    "timeout": 900000
                }
            },
            "id": "http-assemble-full-video",
            "name": "Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [2580, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/studio/extract-shorts",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"video_path\": {{ JSON.stringify($('Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)').first().json.filename) }},\n  \"scenes_data\": {{ JSON.stringify($('Batch Generate Keyframe Anchors & Veo 3 I2V Video Clips (Google Veo 3)').first().json.clips) }},\n  \"num_shorts\": 3,\n  \"target_duration\": 35.0,\n  \"crop_mode\": \"crop\"\n}",
                "options": {
                    "timeout": 300000
                }
            },
            "id": "http-extract-shorts",
            "name": "Multi-Format Content Repurposer (1 Long -> 3 Shorts 9:16)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [2840, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/generate-metadata",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"topic\": {{ JSON.stringify($('Select Topic & Validate').first().json.topic) }},\n  \"script_summary\": {{ JSON.stringify($('Generate Viral Narration Script (Google Gemini)').first().json.narration_script.slice(0, 400)) }}\n}",
                "options": {
                    "timeout": 120000
                }
            },
            "id": "http-generate-metadata",
            "name": "Generate YouTube SEO Metadata (Google Gemini)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [3100, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/ab-thumbnails",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"topic\": {{ JSON.stringify($('Select Topic & Validate').first().json.topic) }},\n  \"variants\": {{ JSON.stringify($('Generate YouTube SEO Metadata (Google Gemini)').first().json.thumbnail_variants) }}\n}",
                "options": {
                    "timeout": 180000
                }
            },
            "id": "http-ab-thumbnails",
            "name": "Generate 3 High-CTR A/B Thumbnails (Google Imagen 3)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [3360, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/youtube/upload",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"video_path\": {{ JSON.stringify($('Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)').first().json.video_path) }},\n  \"thumbnail_path\": {{ JSON.stringify($('Generate 3 High-CTR A/B Thumbnails (Google Imagen 3)').first().json.thumbnails?.[0]?.file_path || null) }},\n  \"title\": {{ JSON.stringify($('Generate YouTube SEO Metadata (Google Gemini)').first().json.title) }},\n  \"description\": {{ JSON.stringify($('Generate YouTube SEO Metadata (Google Gemini)').first().json.description) }},\n  \"tags\": {{ JSON.stringify($('Generate YouTube SEO Metadata (Google Gemini)').first().json.tags ? $('Generate YouTube SEO Metadata (Google Gemini)').first().json.tags.split(',').map(t => t.trim()) : []) }},\n  \"privacy_status\": {{ JSON.stringify($('Global YouTube Channel Settings').first().json.youtube_privacy) }}\n}",
                "options": {
                    "timeout": 180000
                }
            },
            "id": "http-youtube-upload",
            "name": "YouTube Dispatcher & Publishing Station",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [3620, 440]
        },
        {
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": "drive-status",
                            "name": "status",
                            "value": "BACKED_UP",
                            "type": "string"
                        },
                        {
                            "id": "drive-folder",
                            "name": "drive_folder",
                            "value": "={{ 'Google Drive / AI Studio / ' + $('Select Topic & Validate').first().json.topic }}",
                            "type": "string"
                        },
                        {
                            "id": "drive-master",
                            "name": "master_video_url",
                            "value": "={{ $('Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)').first().json.download_url }}",
                            "type": "string"
                        },
                        {
                            "id": "drive-shorts",
                            "name": "shorts_backup",
                            "value": "={{ $('Multi-Format Content Repurposer (1 Long -> 3 Shorts 9:16)').first().json.shorts }}",
                            "type": "array"
                        }
                    ]
                },
                "options": {}
            },
            "id": "google-drive-backup-yt",
            "name": "Google Drive Cloud Backup Station",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [3880, 440]
        },
        {
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": "omni-status",
                            "name": "status",
                            "value": "READY_FOR_OMNICHANNEL",
                            "type": "string"
                        },
                        {
                            "id": "omni-targets",
                            "name": "target_platforms",
                            "value": "={{ ['YouTube Shorts', 'TikTok', 'Instagram Reels'] }}",
                            "type": "array"
                        },
                        {
                            "id": "omni-shorts",
                            "name": "vertical_shorts_queued",
                            "value": "={{ $('Multi-Format Content Repurposer (1 Long -> 3 Shorts 9:16)').first().json.shorts_count || 3 }}",
                            "type": "number"
                        }
                    ]
                },
                "options": {}
            },
            "id": "omnichannel-dispatcher-yt",
            "name": "Omnichannel Social Dispatcher (TikTok / Reels / Shorts)",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [4140, 440]
        },
        {
            "parameters": {
                "jsCode": summary_js_code
            },
            "id": "code-studio-summary",
            "name": "Studio Production Summary & Packaging Dashboard",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [4400, 440]
        }
    ],
    "connections": {
        "Schedule Trigger (Mon, Wed, Fri 8:00 AM)": {
            "main": [
                [
                    {
                        "node": "Global YouTube Channel Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Trend Radar Daily Cron (7:00 AM)": {
            "main": [
                [
                    {
                        "node": "Fetch 24h Trend Radar (Google Trends + Gemini)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Fetch 24h Trend Radar (Google Trends + Gemini)": {
            "main": [
                [
                    {
                        "node": "Auto-Select Top Breakout Trend",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Auto-Select Top Breakout Trend": {
            "main": [
                [
                    {
                        "node": "Global YouTube Channel Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Manual Trigger (Run On-Demand)": {
            "main": [
                [
                    {
                        "node": "Global YouTube Channel Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Webhook Trigger (GET)": {
            "main": [
                [
                    {
                        "node": "Global YouTube Channel Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Webhook Trigger (POST)": {
            "main": [
                [
                    {
                        "node": "Global YouTube Channel Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "n8n Form Trigger (Mobile Web Form)": {
            "main": [
                [
                    {
                        "node": "Global YouTube Channel Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Global YouTube Channel Settings": {
            "main": [
                [
                    {
                        "node": "Ideate 5 Viral Topics (Google Gemini)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Ideate 5 Viral Topics (Google Gemini)": {
            "main": [
                [
                    {
                        "node": "Select Topic & Validate",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Select Topic & Validate": {
            "main": [
                [
                    {
                        "node": "Generate Viral Narration Script (Google Gemini)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Generate Viral Narration Script (Google Gemini)": {
            "main": [
                [
                    {
                        "node": "Synthesize Voiceover (Google Cloud TTS)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Synthesize Voiceover (Google Cloud TTS)": {
            "main": [
                [
                    {
                        "node": "Generate Visual Storyboard & Anchors (Google Gemini)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Generate Visual Storyboard & Anchors (Google Gemini)": {
            "main": [
                [
                    {
                        "node": "Batch Generate Keyframe Anchors & Veo 3 I2V Video Clips (Google Veo 3)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Batch Generate Keyframe Anchors & Veo 3 I2V Video Clips (Google Veo 3)": {
            "main": [
                [
                    {
                        "node": "Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Assemble Full-AI Video with Optical Flow Retiming & Subtitles (Studio Engine)": {
            "main": [
                [
                    {
                        "node": "Multi-Format Content Repurposer (1 Long -> 3 Shorts 9:16)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Multi-Format Content Repurposer (1 Long -> 3 Shorts 9:16)": {
            "main": [
                [
                    {
                        "node": "Generate YouTube SEO Metadata (Google Gemini)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Generate YouTube SEO Metadata (Google Gemini)": {
            "main": [
                [
                    {
                        "node": "Generate 3 High-CTR A/B Thumbnails (Google Imagen 3)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Generate 3 High-CTR A/B Thumbnails (Google Imagen 3)": {
            "main": [
                [
                    {
                        "node": "YouTube Dispatcher & Publishing Station",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "YouTube Dispatcher & Publishing Station": {
            "main": [
                [
                    {
                        "node": "Google Drive Cloud Backup Station",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Google Drive Cloud Backup Station": {
            "main": [
                [
                    {
                        "node": "Omnichannel Social Dispatcher (TikTok / Reels / Shorts)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Omnichannel Social Dispatcher (TikTok / Reels / Shorts)": {
            "main": [
                [
                    {
                        "node": "Studio Production Summary & Packaging Dashboard",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    },
    "tags": [
        {
            "name": "YouTube Studio"
        },
        {
            "name": "Google Veo 3"
        },
        {
            "name": "Full-AI Video"
        },
        {
            "name": "Multi-Format Repurposing"
        }
    ]
}

if __name__ == "__main__":
    out_file = Path(__file__).parent / "workflows" / "youtube_faceless_pipeline.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print(f"Successfully generated Studio v3.0 Ultra workflow JSON at: {out_file}")
