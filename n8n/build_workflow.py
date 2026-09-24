import json
from pathlib import Path

podcast_prompt_text = (
    "1. The Main Event: Gold & Silver (GC=F & SI=F):\n\n"
    "This episode is exclusively about Precious Metals. Gold (GC=F) and Silver (SI=F) are the absolute core focus.\n\n"
    "Synthesize the reports to break down current price action, momentum, and structural trends for both metals.\n\n"
    "Discuss if Silver is leading or lagging Gold in the current cycle.\n\n"
    "2. The Macro Web (Using ^TNX & DX-Y.NYB as drivers):\n\n"
    "Do NOT analyze the US Dollar (DX-Y.NYB) or 10-Year Yields (^TNX) as standalone trades.\n\n"
    "Instead, analyze them strictly as macro tailwinds or headwinds for the metals. "
    "Explain how the current trend in the 10-Year Yield and the Dollar is directly impacting the pricing of GC=F and SI=F "
    '(e.g., "Are rising yields crushing gold, or is gold ignoring the strong dollar?").\n\n'
    "3. Risk Sentiment Rotation (Using SPY & BTC-USD):\n\n"
    "Use the SPY (Equities) and BTC-USD (Crypto) data purely as risk-appetite barometers.\n\n"
    'Evaluate the capital flow: Are we seeing a "risk-on" environment where capital flows to SPY/BTC, '
    'or a "risk-off" environment where traders are seeking safe-haven rotation into Gold and Silver?\n\n'
    "4. The 'Trade Desk' Action Plan (Crucial Segment):\n\n"
    "Dedicate the final 3-4 minutes to actionable trade setups.\n\n"
    "Extract and clearly announce the specific potential entry zones, key support/resistance levels, "
    "and invalidation points (stop losses) for GC=F and SI=F based EXACTLY on the provided reports.\n\n"
    "Frame these levels confidently, like a senior trader giving a playbook to their desk. "
    '(e.g., "For Gold, the desk is looking at a high-probability entry around [Price]...").'
)

summary_js_code = """const settings = $('Global Pipeline Settings').first().json;
const analysis = $('Analyze & Download Completed Reports (TradingAgents AI)').first().json;
const charts = $('Capture Multi-Timeframe Charts (TradingView)').first().json;
const upload = $('Upload Completed Reports & Charts to NotebookLM').first().json;
const podcast = $('Generate Vietnamese Studio Audio (NotebookLM)').first().json;

return [{
  json: {
    pipeline_status: "success",
    execution_time: new Date().toISOString(),
    caching_mode: {
      force_reanalyze: settings.force_reanalyze,
      force_recapture_charts: settings.force_recapture_charts
    },
    notebooklm: {
      notebook_id: upload.notebook_id,
      notebook_title: upload.notebook_title,
      notebook_url: upload.notebook_url,
      sources_total_count: upload.sources_count,
      completed_reports_count: upload.report_sources_count || (analysis.report_files ? analysis.report_files.length : 0),
      chart_images_count: upload.chart_sources_count || (charts.charts ? charts.charts.length : 0),
      sources: upload.sources,
      studio_generation_status: podcast.status,
      studio_task_id: podcast.task_id
    },
    llm_config: {
      provider: settings.llm_provider,
      deep_think_llm: settings.deep_think_llm,
      quick_think_llm: settings.quick_think_llm,
      debate_rounds: settings.max_debate_rounds,
      risk_rounds: settings.max_risk_discuss_rounds,
      language: settings.output_language
    },
    completed_reports_downloaded: analysis.report_files || [],
    charts_captured: charts.charts ? charts.charts.map(c => c.filename) : []
  }
}];"""

workflow = {
    "id": "TDGPodcast0001",
    "name": "Trading Podcast AI Pipeline - Daily Studio Audio",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "cronExpression",
                            "expression": "0 7 * * 1-5"
                        }
                    ]
                }
            },
            "id": "schedule-trigger-1",
            "name": "Schedule Trigger (7:00 AM Weekdays)",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [200, 200]
        },
        {
            "parameters": {},
            "id": "manual-trigger-1",
            "name": "Manual Trigger (Run On-Demand)",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [200, 360]
        },
        {
            "parameters": {
                "httpMethod": "GET",
                "path": "run-trading-podcast",
                "responseMode": "lastNode",
                "options": {}
            },
            "id": "webhook-trigger-get",
            "name": "Webhook Trigger (GET)",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [200, 520],
            "webhookId": "run-trading-podcast"
        },
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "run-trading-podcast",
                "responseMode": "lastNode",
                "options": {}
            },
            "id": "webhook-trigger-post",
            "name": "Webhook Trigger (POST)",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [200, 680],
            "webhookId": "run-trading-podcast-post"
        },
        {
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": "setting-force-reanalyze",
                            "name": "force_reanalyze",
                            "value": "={{ [ $json?.force_reanalyze, $json?.force_analysis, $json?.forceReanalyze, $json?.reanalyze, $json?.body?.force_reanalyze, $json?.body?.force_analysis, $json?.body?.forceReanalyze, $json?.body?.reanalyze, $json?.query?.force_reanalyze, $json?.query?.force_analysis, $json?.query?.forceReanalyze, $json?.query?.reanalyze ].some(v => v === true || v === 'true' || v === 1 || v === '1') }}",
                            "type": "boolean"
                        },
                        {
                            "id": "setting-force-recapture",
                            "name": "force_recapture_charts",
                            "value": "={{ [ $json?.force_recapture_charts, $json?.force_recapture, $json?.force_capture, $json?.forceRecapture, $json?.forceCapture, $json?.recapture, $json?.body?.force_recapture_charts, $json?.body?.force_recapture, $json?.body?.force_capture, $json?.body?.forceRecapture, $json?.body?.forceCapture, $json?.body?.recapture, $json?.query?.force_recapture_charts, $json?.query?.force_recapture, $json?.query?.force_capture, $json?.query?.forceRecapture, $json?.query?.forceCapture, $json?.query?.recapture ].some(v => v === true || v === 'true' || v === 1 || v === '1') }}",
                            "type": "boolean"
                        },
                        {
                            "id": "setting-provider",
                            "name": "llm_provider",
                            "value": "={{ $json?.llm_provider || $json?.body?.llm_provider || $json?.query?.llm_provider || 'openai_compatible' }}",
                            "type": "string"
                        },
                        {
                            "id": "setting-deep-think",
                            "name": "deep_think_llm",
                            "value": "={{ $json?.deep_think_llm || $json?.body?.deep_think_llm || $json?.query?.deep_think_llm || 'ag/gemini-3.8-flash-high' }}",
                            "type": "string"
                        },
                        {
                            "id": "setting-quick-think",
                            "name": "quick_think_llm",
                            "value": "={{ $json?.quick_think_llm || $json?.body?.quick_think_llm || $json?.query?.quick_think_llm || 'ag/gemini-3.8-flash-high' }}",
                            "type": "string"
                        },
                        {
                            "id": "setting-debate-rounds",
                            "name": "max_debate_rounds",
                            "value": "={{ $json?.max_debate_rounds ? Number($json.max_debate_rounds) : ($json?.body?.max_debate_rounds ? Number($json.body.max_debate_rounds) : ($json?.query?.max_debate_rounds ? Number($json.query.max_debate_rounds) : 3)) }}",
                            "type": "number"
                        },
                        {
                            "id": "setting-risk-rounds",
                            "name": "max_risk_discuss_rounds",
                            "value": "={{ $json?.max_risk_discuss_rounds ? Number($json.max_risk_discuss_rounds) : ($json?.body?.max_risk_discuss_rounds ? Number($json.body.max_risk_discuss_rounds) : ($json?.query?.max_risk_discuss_rounds ? Number($json.query.max_risk_discuss_rounds) : 3)) }}",
                            "type": "number"
                        },
                        {
                            "id": "setting-language",
                            "name": "output_language",
                            "value": "={{ $json?.output_language || $json?.body?.output_language || $json?.query?.output_language || 'Vietnamese' }}",
                            "type": "string"
                        },
                        {
                            "id": "setting-tickers",
                            "name": "tickers",
                            "value": '={{ $json?.tickers || $json?.body?.tickers || ($json?.query?.tickers ? (typeof $json.query.tickers === "string" ? $json.query.tickers.split(",").map(s => s.trim()) : $json.query.tickers) : ["XAUUSD", "SPY", "BTC-USD", "XAGUSD", "^TNX", "DX-Y.NYB"]) }}',
                            "type": "array"
                        },
                        {
                            "id": "setting-chart-symbols",
                            "name": "chart_symbols",
                            "value": '={{ $json?.chart_symbols || $json?.body?.chart_symbols || ($json?.query?.chart_symbols ? (typeof $json.query.chart_symbols === "string" ? $json.query.chart_symbols.split(",").map(s => s.trim()) : $json.query.chart_symbols) : ["XAUUSD", "XAGUSD"]) }}',
                            "type": "array"
                        },
                        {
                            "id": "setting-chart-intervals",
                            "name": "chart_intervals",
                            "value": '={{ $json?.chart_intervals || $json?.body?.chart_intervals || ($json?.query?.chart_intervals ? (typeof $json.query.chart_intervals === "string" ? $json.query.chart_intervals.split(",").map(s => s.trim()) : $json.query.chart_intervals) : ["5", "15", "60", "240", "D", "W"]) }}',
                            "type": "array"
                        },
                        {
                            "id": "setting-podcast-prompt",
                            "name": "podcast_prompt",
                            "value": podcast_prompt_text,
                            "type": "string"
                        }
                    ]
                },
                "options": {}
            },
            "id": "global-pipeline-settings",
            "name": "Global Pipeline Settings",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [520, 440]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/pipeline/analyze-markets",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"tickers\": {{ JSON.stringify($('Global Pipeline Settings').first().json.tickers) }},\n  \"tradingagents_backend_url\": \"http://tradingagents-backend:8000\",\n  \"llm_provider\": {{ JSON.stringify($('Global Pipeline Settings').first().json.llm_provider) }},\n  \"deep_think_llm\": {{ JSON.stringify($('Global Pipeline Settings').first().json.deep_think_llm) }},\n  \"quick_think_llm\": {{ JSON.stringify($('Global Pipeline Settings').first().json.quick_think_llm) }},\n  \"max_debate_rounds\": {{ $('Global Pipeline Settings').first().json.max_debate_rounds }},\n  \"max_risk_discuss_rounds\": {{ $('Global Pipeline Settings').first().json.max_risk_discuss_rounds }},\n  \"output_language\": {{ JSON.stringify($('Global Pipeline Settings').first().json.output_language) }},\n  \"force_reanalyze\": {{ $('Global Pipeline Settings').first().json.force_reanalyze }}\n}",
                "options": {
                    "timeout": 1800000
                }

            },
            "id": "http-analyze-markets",
            "name": "Analyze & Download Completed Reports (TradingAgents AI)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [800, 280]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/charts/capture",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"symbols\": {{ JSON.stringify($('Global Pipeline Settings').first().json.chart_symbols) }},\n  \"intervals\": {{ JSON.stringify($('Global Pipeline Settings').first().json.chart_intervals) }},\n  \"force_recapture\": {{ $('Global Pipeline Settings').first().json.force_recapture_charts }}\n}",
                "options": {
                    "timeout": 300000
                }
            },
            "id": "http-capture-charts",
            "name": "Capture Multi-Timeframe Charts (TradingView)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [800, 560]
        },
        {
            "parameters": {
                "mode": "chooseBranch",
                "output": "specifiedInput",
                "useDataOfInput": 1
            },
            "id": "merge-analysis-charts",
            "name": "Sync Reports & Charts Data",
            "type": "n8n-nodes-base.merge",
            "typeVersion": 3,
            "position": [1150, 420]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/notebooklm/upload-sources",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"report_md_paths\": {{ JSON.stringify($('Analyze & Download Completed Reports (TradingAgents AI)').first().json.report_files) }},\n  \"chart_image_paths\": {{ JSON.stringify($('Capture Multi-Timeframe Charts (TradingView)').first().json.charts.map(c => c.filepath)) }}\n}",
                "options": {
                    "timeout": 600000
                }
            },
            "id": "http-upload-sources",
            "name": "Upload Completed Reports & Charts to NotebookLM",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1500, 420]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/notebooklm/generate-podcast",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"notebook_id\": {{ JSON.stringify($('Upload Completed Reports & Charts to NotebookLM').first().json.notebook_id) }},\n  \"custom_prompt\": {{ JSON.stringify($('Global Pipeline Settings').first().json.podcast_prompt) }},\n  \"wait_for_completion\": false\n}",
                "options": {
                    "timeout": 600000
                }
            },
            "id": "http-generate-podcast",
            "name": "Generate Vietnamese Studio Audio (NotebookLM)",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1850, 420]
        },
        {
            "parameters": {
                "jsCode": summary_js_code
            },
            "id": "summary-node-1",
            "name": "Pipeline Summary & Artifacts",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [2200, 420]
        }
    ],
    "connections": {
        "Schedule Trigger (7:00 AM Weekdays)": {
            "main": [
                [
                    {
                        "node": "Global Pipeline Settings",
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
                        "node": "Global Pipeline Settings",
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
                        "node": "Global Pipeline Settings",
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
                        "node": "Global Pipeline Settings",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Global Pipeline Settings": {
            "main": [
                [
                    {
                        "node": "Analyze & Download Completed Reports (TradingAgents AI)",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Capture Multi-Timeframe Charts (TradingView)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Analyze & Download Completed Reports (TradingAgents AI)": {
            "main": [
                [
                    {
                        "node": "Sync Reports & Charts Data",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Capture Multi-Timeframe Charts (TradingView)": {
            "main": [
                [
                    {
                        "node": "Sync Reports & Charts Data",
                        "type": "main",
                        "index": 1
                    }
                ]
            ]
        },
        "Sync Reports & Charts Data": {
            "main": [
                [
                    {
                        "node": "Upload Completed Reports & Charts to NotebookLM",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Upload Completed Reports & Charts to NotebookLM": {
            "main": [
                [
                    {
                        "node": "Generate Vietnamese Studio Audio (NotebookLM)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Generate Vietnamese Studio Audio (NotebookLM)": {
            "main": [
                [
                    {
                        "node": "Pipeline Summary & Artifacts",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

target_file = Path("/home/popeye/projects/trading-podcast/n8n/workflows/trading_podcast_workflow.json")
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {target_file} with {len(workflow['nodes'])} nodes.")
