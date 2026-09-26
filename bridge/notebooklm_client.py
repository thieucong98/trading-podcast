import asyncio
import datetime
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("notebooklm_client")

DEFAULT_VIETNAMESE_PROMPT = """
Tạo một tập podcast audio chuyên sâu về thị trường tài chính hôm nay bằng tiếng Việt.
Hai người dẫn chương trình (một nam, một nữ) trao đổi và tranh luận tự nhiên, hấp dẫn, chuyên nghiệp và thực chiến.
Nội dung thảo luận tập trung phân tích sâu xu hướng giá vàng (XAUUSD), bạc (XAGUSD), chỉ số chứng khoán Mỹ (SPY) và Bitcoin (BTC-USD) dựa trên các tài liệu báo cáo phân tích và các hình ảnh biểu đồ kỹ thuật được đính kèm.
Làm rõ các kịch bản Bull/Bear, các mốc hỗ trợ - kháng cự then chốt, và kế hoạch giải ngân, quản trị rủi ro.
""".strip()


class NotebookLMClient:
    def __init__(self, storage_state_path: str | None = None):
        self.storage_state_path = storage_state_path or os.getenv(
            "NOTEBOOKLM_STORAGE_STATE", "/app/storage_state.json"
        )

    def _ensure_default_profile_auth(self) -> bool:
        """Ensure storage_state.json is properly formatted and copied to ~/.notebooklm/profiles/default/storage_state.json"""
        src = Path(self.storage_state_path)
        if not src.exists() or src.stat().st_size <= 50:
            return False
        try:
            with open(src, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                data = {"cookies": data, "origins": []}
                with open(src, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

            profile_dir = Path.home() / ".notebooklm" / "profiles" / "default"
            profile_dir.mkdir(parents=True, exist_ok=True)
            dst = profile_dir / "storage_state.json"
            with open(dst, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.warning(f"Failed ensuring default profile auth: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if Google session credentials exist."""
        if self._ensure_default_profile_auth():
            return True
        p = Path(self.storage_state_path)
        if p.exists() and p.stat().st_size > 50:
            return True
        home_p = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"
        if home_p.exists() and home_p.stat().st_size > 50:
            return True
        return False

    async def upload_sources_to_notebooklm(
        self,
        report_md_paths: list[str] | None = None,
        briefing_md_path: str | None = None,
        chart_image_paths: list[str] | None = None,
        notebook_title: str | None = None,
        notebook_id: str | None = None,
        date_str: str | None = None,
    ) -> dict[str, Any]:
        """Create a Google NotebookLM notebook (or use existing) and upload individual completed reports and chart images."""
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        chart_image_paths = chart_image_paths or []
        report_md_paths = list(report_md_paths or [])
        if briefing_md_path and briefing_md_path not in report_md_paths:
            report_md_paths.append(briefing_md_path)

        has_auth = self.is_authenticated()
        if not (has_auth and shutil.which("notebooklm")):
            logger.warning("NotebookLM not authenticated or CLI missing. Returning prepared state.")
            return {
                "status": "sources_prepared_offline",
                "notebook_id": notebook_id or "offline_ready",
                "reports_count": len(report_md_paths),
                "charts_count": len(chart_image_paths),
                "message": "Cookies missing or invalid. Please check storage_state.json",
            }

        title = notebook_title or f"Trading Intelligence & Multi-Asset Reports - {date_str}"
        target_nid = notebook_id

        # 1. Create notebook if not provided
        if not target_nid:
            logger.info(f"Creating notebook: '{title}' on Google NotebookLM...")
            create_res = subprocess.run(
                ["notebooklm", "create", title, "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            if create_res.returncode != 0:
                err_msg = (create_res.stderr or create_res.stdout or "").strip()
                logger.warning(f"NotebookLM create failed (exit {create_res.returncode}): {err_msg}")
                return {
                    "status": "auth_expired",
                    "notebook_id": "auth_required",
                    "notebook_title": title,
                    "notebook_url": "https://notebooklm.google.com",
                    "sources_count": 0,
                    "report_sources_count": len(report_md_paths),
                    "chart_sources_count": len(chart_image_paths),
                    "sources": [],
                    "message": "Google NotebookLM session expired or invalid. Please update storage_state.json with fresh cookies.",
                    "error_detail": err_msg,
                }
            try:
                create_data = json.loads(create_res.stdout) if create_res.stdout else {}
            except Exception as e:
                logger.warning(f"Failed parsing create json: {e}")
                create_data = {}

            target_nid = (
                create_data.get("notebook", {}).get("id")
                or create_data.get("id")
                or create_data.get("notebook_id")
            )
            if not target_nid:
                logger.warning(f"Could not extract notebook ID from: {create_res.stdout}")
                return {
                    "status": "auth_expired",
                    "notebook_id": "auth_required",
                    "notebook_title": title,
                    "notebook_url": "https://notebooklm.google.com",
                    "sources_count": 0,
                    "report_sources_count": len(report_md_paths),
                    "chart_sources_count": len(chart_image_paths),
                    "sources": [],
                    "message": "Failed to create notebook on NotebookLM. Please check storage_state.json",
                }
            logger.info(f"Successfully created Notebook ID: {target_nid}")

        uploaded_sources = []

        # 2. Add Completed Report Markdown Sources
        for md_path_str in report_md_paths:
            if not md_path_str or not isinstance(md_path_str, (str, Path)):
                continue
            md_file = Path(md_path_str)
            if md_file.exists() and md_file.stat().st_size > 50:
                logger.info(f"Uploading completed report markdown to notebook {target_nid}: {md_file.name} ({md_file.stat().st_size} bytes)")
                try:
                    add_res = subprocess.run(
                        ["notebooklm", "source", "add", str(md_file.resolve()), "-n", target_nid, "--title", md_file.name, "--json"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    try:
                        s_info = json.loads(add_res.stdout).get("source", {})
                        uploaded_sources.append(s_info)
                    except Exception:
                        uploaded_sources.append({"title": md_file.name, "path": str(md_file)})
                except Exception as ex:
                    logger.warning(f"Failed uploading report markdown {md_file.name}: {ex}")

        # 3. Add Chart Images Sources
        for img in chart_image_paths:
            if not img or not isinstance(img, (str, Path)):
                continue
            img_path = Path(img)
            if img_path.exists() and img_path.stat().st_size > 500:
                logger.info(f"Uploading chart to notebook {target_nid}: {img_path.name}")
                try:
                    c_res = subprocess.run(
                        ["notebooklm", "source", "add", str(img_path.resolve()), "-n", target_nid, "--title", img_path.name, "--json"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    s_info = json.loads(c_res.stdout).get("source", {})
                    uploaded_sources.append(s_info)
                except Exception as ex:
                    logger.warning(f"Failed uploading chart {img_path.name}: {ex}")

        # 4. List sources and wait for any processing ones
        final_sources = []
        try:
            list_res = subprocess.run(
                ["notebooklm", "source", "list", "-n", target_nid, "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            final_sources = json.loads(list_res.stdout).get("sources", [])
            for s in final_sources:
                if s.get("status") != "ready":
                    logger.info(f"Waiting for source {s.get('title')} ({s.get('id')}) to become ready...")
                    subprocess.run(
                        ["notebooklm", "source", "wait", s.get("id"), "-n", target_nid, "--timeout", "60"],
                        capture_output=True,
                        text=True,
                    )
        except Exception as e:
            logger.warning(f"Error checking sources list: {e}")

        return {
            "status": "ready",
            "notebook_id": target_nid,
            "notebook_title": title,
            "notebook_url": f"https://notebooklm.google.com/notebook/{target_nid}",
            "sources_count": len(final_sources) or len(uploaded_sources),
            "sources": [s.get("title") for s in final_sources] or [s.get("title") for s in uploaded_sources],
            "report_sources_count": len(report_md_paths),
            "chart_sources_count": len(chart_image_paths),
            "date": date_str,
        }

    async def generate_podcast_studio(
        self,
        notebook_id: str | None = None,
        briefing_md_path: str | None = None,
        chart_image_paths: list[str] | None = None,
        custom_prompt: str | None = None,
        wait_for_completion: bool = False,
        date_str: str | None = None,
        output_dir: str | Path = "/app/output/podcasts",
    ) -> dict[str, Any]:
        """Main method to trigger Vietnamese audio podcast generation on a populated notebook."""
        if not date_str:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        prompt = custom_prompt or DEFAULT_VIETNAMESE_PROMPT
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        final_audio_path = out_dir / f"trading_podcast_{date_str}.mp3"

        has_auth = self.is_authenticated()
        target_nid = notebook_id
        if target_nid in ("auth_required", "offline_ready"):
            has_auth = False

        if has_auth and shutil.which("notebooklm"):
            try:
                if not target_nid and briefing_md_path:
                    upload_res = await self.upload_sources_to_notebooklm(
                        briefing_md_path=briefing_md_path,
                        chart_image_paths=chart_image_paths or [],
                        date_str=date_str,
                    )
                    target_nid = upload_res.get("notebook_id")

                if not target_nid:
                    raise ValueError("No valid notebook_id provided or created for podcast generation.")

                logger.info(f"Triggering NotebookLM Studio generation on notebook: {target_nid}...")
                prompt_file = out_dir / f"temp_prompt_{date_str}.txt"
                prompt_file.write_text(prompt, encoding="utf-8")

                cmd = [
                    "notebooklm", "generate", "audio",
                    "-n", target_nid,
                    "--prompt-file", str(prompt_file),
                    "--language", "vi",
                    "--json",
                ]
                if wait_for_completion:
                    cmd.append("--wait")
                    cmd.extend(["--timeout", "600"])
                else:
                    cmd.append("--no-wait")

                gen_res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=660 if wait_for_completion else 30,
                )
                res_data = json.loads(gen_res.stdout) if gen_res.stdout else {}
                logger.info(f"Audio generation response: {res_data}")

                if wait_for_completion:
                    logger.info(f"Downloading generated audio to {final_audio_path}...")
                    subprocess.run(
                        ["notebooklm", "download", "audio", "-n", target_nid, str(final_audio_path), "--force"],
                        check=True,
                        capture_output=True,
                    )

                return {
                    "status": "generation_in_progress" if not wait_for_completion else "success",
                    "provider": "google_notebooklm",
                    "notebook_id": target_nid,
                    "notebook_url": f"https://notebooklm.google.com/notebook/{target_nid}",
                    "task_id": res_data.get("task_id"),
                    "audio_file": str(final_audio_path.resolve()) if wait_for_completion else None,
                    "prompt_used": prompt,
                    "date": date_str,
                }
            except Exception as e:
                logger.error(f"Error during NotebookLM CLI execution: {e}")
                return self._generate_guidance_fallback(
                    briefing_md_path or "", chart_image_paths or [], prompt, date_str, final_audio_path, error=str(e), notebook_id=notebook_id
                )
        else:
            return self._generate_guidance_fallback(
                briefing_md_path or "", chart_image_paths or [], prompt, date_str, final_audio_path
            )

    def _generate_guidance_fallback(
        self,
        briefing_md_path: str | None,
        chart_image_paths: list[str],
        prompt: str,
        date_str: str,
        final_audio_path: Path,
        error: str | None = None,
        notebook_id: str | None = None,
    ) -> dict[str, Any]:
        """Provide detailed guidance, mock artifact, and instructions when credentials are being set up."""
        logger.info("Generating podcast package and NotebookLM preparation instructions...")

        resolved_briefing = ""
        if briefing_md_path and str(briefing_md_path).strip():
            try:
                resolved_briefing = str(Path(briefing_md_path).resolve())
            except Exception:
                resolved_briefing = str(briefing_md_path)

        # Create a metadata bundle file
        bundle_info = {
            "title": f"Trading Daily Podcast - {date_str}",
            "date": date_str,
            "status": "sources_prepared_ready_for_upload",
            "language": "Vietnamese (Tiếng Việt)",
            "studio_prompt": prompt,
            "briefing_document": resolved_briefing,
            "chart_sources": [str(Path(p).resolve()) for p in chart_image_paths if Path(p).exists()],
            "how_to_connect_google_credentials": [
                "Cách 1 (Tự động hóa hoàn toàn): Đăng nhập Google Chrome trên máy, cài tiện ích Get cookies.txt hoặc dùng lệnh `notebooklm login` để sinh file storage_state.json và đặt vào thư mục trading-podcast/storage_state.json.",
                "Cách 2 (Sử dụng Web NotebookLM trực tiếp): Mở https://notebooklm.google.com -> Tạo Notebook mới -> Kéo thả file trading_podcast_briefing.md và các ảnh biểu đồ trong thư mục output/charts/ -> Bấm 'Generate Audio Overview' và dán prompt tiếng Việt đã được chuẩn bị sẵn!",
            ],
            "audio_target_path": str(final_audio_path.resolve()),
            "notice": error or "Chờ file cấu hình Google credentials (storage_state.json) để auto-download audio.",
        }

        meta_path = final_audio_path.with_suffix(".json")
        meta_path.write_text(json.dumps(bundle_info, ensure_ascii=False, indent=2), encoding="utf-8")

        # Also create a placeholder podcast script markdown for manual review
        script_path = final_audio_path.with_name(f"podcast_script_{date_str}.md")
        briefing_text = f"1. Văn bản tóm tắt: `{resolved_briefing}`\n" if resolved_briefing else "1. Báo cáo phân tích chuyên sâu từng tài sản\n"
        script_content = f"""# KỊCH BẢN PODCAST CHI TIẾT - NGÀY {date_str}

**Chủ đề:** Nhận định Vàng (XAUUSD), Bạc (XAGUSD), SPY và Bitcoin (BTC-USD)
**Prompt NotebookLM Studio:**
{prompt}

## Danh sách file nguồn đã sẵn sàng upload lên NotebookLM:
{briefing_text}2. Biểu đồ kỹ thuật:
"""
        for p in chart_image_paths:
            script_content += f"- `{Path(p).resolve()}`\n"

        script_path.write_text(script_content, encoding="utf-8")

        return {
            "status": "ready",
            "provider": "notebooklm_ready",
            "date": date_str,
            "prompt_used": prompt,
            "briefing_file": resolved_briefing,
            "chart_files": [str(Path(p).resolve()) for p in chart_image_paths],
            "metadata_file": str(meta_path.resolve()),
            "script_file": str(script_path.resolve()),
            "instructions": bundle_info["how_to_connect_google_credentials"],
        }



notebooklm_client = NotebookLMClient()
