#!/usr/bin/env python3
import json
from pathlib import Path

extract_payload_js = """
const items = $input.all();
const firstItem = items[0] || {};
const json = firstItem.json || {};
const binary = firstItem.binary || {};

let rawText = '';

// 1. Check binary files
const binaryKeys = Object.keys(binary);
if (binaryKeys.length > 0) {
  for (const key of binaryKeys) {
    try {
      const buf = await this.helpers.getBinaryDataBuffer(0, key);
      if (buf && buf.length > 0) {
        rawText = buf.toString('utf-8').trim();
        if (rawText.length > 0) break;
      }
    } catch (e) {
      if (binary[key]?.data) {
        rawText = Buffer.from(binary[key].data, 'base64').toString('utf-8').trim();
        if (rawText.length > 0) break;
      }
    }
  }
}

// 2. Check JSON form fields
if (!rawText) {
  for (const key of Object.keys(json)) {
    const val = json[key];
    if (typeof val === 'string' && val.trim().length > 0) {
      if (val.includes('{') || val.includes('[') || val.includes('cookie') || val.includes('SID') || key.includes('field') || key.includes('Cookie') || key.includes('content')) {
        rawText = val.trim();
        break;
      }
    }
  }
}

if (!rawText) {
  throw new Error("Vui lòng tải lên file storage_state.json hoặc dán nội dung JSON cookies!");
}

return [{
  json: {
    content: rawText
  }
}];
"""

format_html_js = """
const items = $input.all();
const firstItem = items[0] || {};
const res = firstItem.json || {};
const isSuccess = res.status === 'success';
const verification = res.verification || {};
const isValid = verification.status === 'valid';
const email = verification.account_email || 'Chưa xác định';
const cookiesCount = res.imported_cookies_count || verification.cookies_count || 0;
const errMsg = res.detail || res.message || verification.error || '';

const statusColor = (isSuccess && isValid) ? '#10b981' : (isSuccess ? '#f59e0b' : '#ef4444');
const statusBadge = (isSuccess && isValid) ? '🟢 THÀNH CÔNG (TOKEN HỢP LỆ)' : (isSuccess ? '🟡 ĐÃ LƯU (TOKEN HẾT HẠN HOẶC CẦN REFRESH)' : '🔴 LỖI CẬP NHẬT');

const html = `
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kết quả cập nhật NotebookLM Auth</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
    .card { background: #1e293b; border-radius: 16px; padding: 32px; max-width: 540px; width: 100%; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5); border: 1px solid #334155; }
    .badge { display: inline-block; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 13px; margin-bottom: 20px; background: rgba(255, 255, 255, 0.08); color: ${statusColor}; border: 1px solid ${statusColor}; }
    h1 { font-size: 22px; margin: 0 0 12px 0; font-weight: 700; color: #fff; }
    p { color: #94a3b8; font-size: 14px; line-height: 1.5; margin: 0 0 20px 0; }
    .info-box { background: #0f172a; border-radius: 12px; padding: 16px; margin-bottom: 24px; border: 1px solid #334155; }
    .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 14px; }
    .info-row:last-child { border-bottom: none; }
    .info-label { color: #64748b; }
    .info-value { font-weight: 600; color: #f1f5f9; }
    .btn { display: block; text-align: center; background: #3b82f6; color: white; padding: 12px 20px; border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 14px; transition: background 0.2s; }
    .btn:hover { background: #2563eb; }
    .alert { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 12px; font-size: 13px; color: #fca5a5; margin-bottom: 20px; word-break: break-word; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">${statusBadge}</div>
    <h1>Kết Quả Cập Nhật Storage State</h1>
    <p>Hệ thống đã xử lý và nạp dữ liệu phiên đăng nhập Google NotebookLM.</p>
    
    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Tài khoản Google:</span>
        <span class="info-value">${email}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Số cookies đã nạp:</span>
        <span class="info-value">${cookiesCount}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Trạng thái Token:</span>
        <span class="info-value" style="color: ${statusColor}; text-transform: uppercase;">${verification.status || (isSuccess ? 'READY' : 'FAILED')}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Thời gian cập nhật:</span>
        <span class="info-value">${new Date().toLocaleString('vi-VN')}</span>
      </div>
    </div>

    ${errMsg ? `<div class="alert"><strong>Thông báo:</strong> ${errMsg}</div>` : ''}

    <a href="/form/update-storage-state" class="btn">Quay lại Form cập nhật</a>
  </div>
</body>
</html>
`;

return [{
  json: {
    html: html
  }
}];
"""

workflow = {
    "id": "NLMAuth0001",
    "name": "NotebookLM Auth - Storage State & Cookie Manager",
    "active": True,
    "nodes": [
        {
            "parameters": {
                "path": "update-storage-state",
                "formTitle": "NotebookLM Auth - Storage State & Cookie Manager",
                "formDescription": "Tải lên file storage_state.json HOẶC dán nội dung JSON Cookies để cập nhật phiên Google NotebookLM.",
                "formFields": {
                    "values": [
                        {
                            "fieldLabel": "Tải lên file storage_state.json",
                            "fieldType": "file",
                            "requiredField": False
                        },
                        {
                            "fieldLabel": "Hoặc dán nội dung JSON / Cookies",
                            "fieldType": "textarea",
                            "requiredField": False
                        }
                    ]
                },
                "options": {}
            },
            "id": "form-trigger-auth",
            "name": "n8n Form Trigger (Web UI)",
            "type": "n8n-nodes-base.formTrigger",
            "typeVersion": 2.2,
            "position": [208, 380],
            "webhookId": "update-storage-state"
        },
        {
            "parameters": {
                "jsCode": extract_payload_js
            },
            "id": "code-extract-payload",
            "name": "Extract & Validate Input (File or Text)",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [560, 380]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "http://trading-podcast-bridge:8010/api/notebooklm/auth/storage-state",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({ content: $json.content }) }}",
                "options": {
                    "neverError": True
                }
            },
            "id": "http-bridge-update",
            "name": "Send Update to Bridge Service",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [920, 380]
        },
        {
            "parameters": {
                "jsCode": format_html_js
            },
            "id": "code-format-html",
            "name": "Build Responsive HTML Dashboard",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1280, 380]
        },
        {
            "parameters": {
                "operation": "completion",
                "respondWith": "showText",
                "responseText": "={{ $json.html }}"
            },
            "id": "form-completion",
            "name": "Form Ending (Show Result Page)",
            "type": "n8n-nodes-base.form",
            "typeVersion": 1,
            "position": [1640, 380]
        }
    ],
    "connections": {
        "n8n Form Trigger (Web UI)": {
            "main": [
                [
                    {
                        "node": "Extract & Validate Input (File or Text)",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Extract & Validate Input (File or Text)": {
            "main": [
                [
                    {
                        "node": "Send Update to Bridge Service",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Send Update to Bridge Service": {
            "main": [
                [
                    {
                        "node": "Build Responsive HTML Dashboard",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Build Responsive HTML Dashboard": {
            "main": [
                [
                    {
                        "node": "Form Ending (Show Result Page)",
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


def build():
    out_path = Path(__file__).resolve().parent / "workflows" / "notebooklm_auth_workflow.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Successfully generated {out_path} with {len(workflow['nodes'])} nodes.")


if __name__ == "__main__":
    build()
