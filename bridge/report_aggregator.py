import datetime
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("report_aggregator")


def build_podcast_briefing_markdown(
    reports: list[dict[str, Any]],
    date_str: str | None = None,
    output_dir: str | Path = "/app/output/reports",
) -> dict[str, Any]:
    """Aggregate individual asset reports into a cohesive, structured podcast briefing document."""
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    filename = f"trading_podcast_briefing_{date_str}.md"
    filepath = out_path / filename

    # Index reports by ticker for easy lookup
    by_ticker = {r.get("ticker", "").upper(): r for r in reports}

    md_lines = [
        f"# BẢN TIN PODCAST TÀI CHÍNH & CHIẾN LƯỢC GIAO DỊCH THỰC CHIẾN - NGÀY {date_str}",
        "",
        "> **Tài liệu nguồn (Source Document) chuẩn bị cho NotebookLM Audio Overview (Podcast Studio)**",
        f"> **Thời gian lập:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> **Chủ đề chính:** Toàn cảnh thị trường Vàng (XAUUSD), Bạc (XAGUSD), Chứng khoán Mỹ (SPY) và Bitcoin (BTC-USD).",
        "",
        "---",
        "",
        "## 1. TỔNG QUAN VĨ MÔ & CHỈ SỐ CHỨNG KHOÁN MỸ (S&P 500 / SPY)",
        "",
    ]

    spy_rep = by_ticker.get("SPY")
    if spy_rep:
        md_lines.extend([
            f"- **Tín hiệu khuyến nghị:** `{spy_rep.get('recommendation', 'N/A')}`",
            f"- **Vùng giá vào lệnh (Entry):** `{spy_rep.get('entry_price') or 'Theo dõi thêm'}` | **Mục tiêu (Target):** `{spy_rep.get('target_price') or 'N/A'}` | **Dừng lỗ (Stop-loss):** `{spy_rep.get('stop_loss') or 'N/A'}`",
            "",
            "### Tóm tắt nhận định của Ban chuyên gia SPY:",
            spy_rep.get("executive_summary") or "Dữ liệu SPY cho thấy thị trường đang phân hóa giữa kỳ vọng lãi suất và thanh khoản thị trường.",
            "",
            "### Phân tích Tin tức & Vĩ mô (Macro & News):",
            (spy_rep.get("news_report_md") or spy_rep.get("market_report_md") or "")[:1500],
            "",
        ])
    else:
        md_lines.append("- Thị trường chứng khoán Mỹ ghi nhận trạng thái đi ngang chờ đợi các dữ liệu lạm phát và phát biểu từ Fed.\n")

    md_lines.extend([
        "---",
        "",
        "## 2. TÂM ĐIỂM KIM LOẠI QUÝ: VÀNG (XAUUSD) & BẠC (XAGUSD)",
        "",
        "> *Các biểu đồ kỹ thuật TradingView đính kèm: Khung 15m (Scalping), 1H (Intraday), 4H (Swing), 1D (Trend chính).*",
        "",
    ])

    xau_rep = by_ticker.get("XAUUSD")
    if xau_rep:
        md_lines.extend([
            "### Vàng Giao Ngay (XAUUSD):",
            f"- **Khuyến nghị chiến lược:** `{xau_rep.get('recommendation', 'Hold')}`",
            f"- **Entry dự kiến:** `{xau_rep.get('entry_price') or 'Quan sát vùng hỗ trợ'}`",
            f"- **Target ngắn hạn/trung hạn:** `{xau_rep.get('target_price') or 'Đỉnh cũ'}`",
            f"- **Stop Loss bảo vệ vốn:** `{xau_rep.get('stop_loss') or 'Dưới đáy gần nhất'}`",
            "",
            "#### Luận điểm Tranh luận Đa chiều (Bull vs Bear Debate):",
            xau_rep.get("executive_summary") or "",
            "",
            "#### Phân tích Kỹ thuật & Tâm lý Thị trường Vàng:",
            (xau_rep.get("market_report_md") or xau_rep.get("sentiment_report_md") or "")[:2000],
            "",
        ])
    else:
        md_lines.append("### Vàng Giao Ngay (XAUUSD):\n- Đang biến động trong biên độ tích lũy, theo sát các mốc hỗ trợ và kháng cự trên biểu đồ 4H và 1D.\n")

    md_lines.extend([
        "### Bạc Giao Ngay (XAGUSD):",
        "- Bạc thể hiện sự tương quan mật thiết với Vàng nhưng có biên độ đòn bẩy biến động mạnh hơn (High Beta).",
        "- Các nhà đầu tư chú ý tỷ lệ Gold/Silver Ratio và dòng tiền đổ vào tài sản kim loại công nghiệp quý.",
        "",
        "---",
        "",
        "## 3. THỊ TRƯỜNG TIỀN MÃ HÓA (BITCOIN / BTC-USD)",
        "",
    ])

    btc_rep = by_ticker.get("BTC-USD") or by_ticker.get("BTCUSD")
    if btc_rep:
        md_lines.extend([
            f"- **Tín hiệu khuyến nghị:** `{btc_rep.get('recommendation', 'N/A')}`",
            f"- **Mức giá định hướng (Entry):** `{btc_rep.get('entry_price') or 'Theo nhịp điều chỉnh'}` | **Target:** `{btc_rep.get('target_price') or 'Kháng cự then chốt'}` | **Stop Loss:** `{btc_rep.get('stop_loss') or 'Dưới ngưỡng hỗ trợ động'}`",
            "",
            "### Tóm lược phân tích Bitcoin:",
            btc_rep.get("executive_summary") or "",
            "",
            "### Tâm lý & Dòng tiền Crypto:",
            (btc_rep.get("sentiment_report_md") or btc_rep.get("market_report_md") or "")[:1500],
            "",
        ])
    else:
        md_lines.append("- Bitcoin tiếp tục phản ứng quanh các vùng thanh khoản lớn, nhà đầu tư cần thận trọng quản trị đòn bẩy.\n")

    md_lines.extend([
        "---",
        "",
        "## 4. CHIẾN LƯỢC THỰC CHIẾN & QUẢN TRỊ DANH MỤC (PORTFOLIO MANAGER ADVICE)",
        "",
        "1. **Tỷ lệ phân bổ vốn:** Duy trì lượng tiền mặt dự phòng, không all-in một chiều.",
        "2. **Kỷ luật Stop-loss:** Tuyệt đối gồng lỗ, luôn đặt dừng lỗ trước khi bấm lệnh giao dịch.",
        "3. **Đa khung thời gian:** Khung Ngày (1D) định vị xu hướng chủ đạo, khung Giờ (1H / 15m) tối ưu hóa điểm vào lệnh.",
        "",
        "---",
        "",
        "## 5. HƯỚNG DẪN DÀNH CHO HAI MC PODCAST (HOST DIRECTIVES)",
        "",
        "- **Phong cách dẫn:** Thân thiện, khách quan, giàu năng lượng, phân tích sắc bén nhưng dễ hiểu.",
        "- **Người dẫn 1 (Host A):** Đặt vấn đề, đưa ra góc nhìn lạc quan (Bullish), khai thác tiềm năng tăng giá của Vàng và Crypto.",
        "- **Người dẫn 2 (Host B):** Đóng vai phản biện thực tế (Bearish/Risk Manager), chỉ ra các rủi ro bẫy giá, các ngưỡng cản và tầm quan trọng của việc bảo vệ vốn.",
        "- **Kết luận:** Đồng thuận chiến lược hành động giá cụ thể trong ngày.",
        "",
    ])

    full_content = "\n".join(md_lines)
    filepath.write_text(full_content, encoding="utf-8")
    logger.info(f"Synthesized podcast briefing saved to {filepath} ({len(full_content)} chars)")

    return {
        "date": date_str,
        "filename": filename,
        "filepath": str(filepath.resolve()),
        "character_count": len(full_content),
        "content": full_content,
        "status": "success",
    }
