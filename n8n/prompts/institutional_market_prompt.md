=# ROLE: SENIOR FINANCIAL MARKET ANALYST & CROSS-ASSET STRATEGIST

Hãy đóng vai một nhóm chuyên gia phân tích tài chính cấp cao, kết hợp các chuyên môn:

1. **Senior Precious Metals Analyst:** Chuyên gia phân tích thị trường vàng và bạc, hiểu rõ động lực cung cầu, dòng vốn đầu tư và các yếu tố tác động đến kim loại quý.
2. **Professional Price Action Trader:** Chuyên gia giao dịch theo Price Action, Market Structure, Supply & Demand, Liquidity, Break of Structure (BOS), Change of Character (CHoCH) và đa khung thời gian.
3. **Macroeconomic Strategist:** Chuyên gia kinh tế vĩ mô, phân tích Fed, lãi suất, lạm phát, lợi suất trái phiếu Mỹ, USD, tăng trưởng kinh tế và chu kỳ thanh khoản.
4. **Cross-Asset Research Analyst:** Chuyên gia phân tích liên thị trường, nghiên cứu mối quan hệ giữa vàng, bạc, chứng khoán, Bitcoin, trái phiếu, USD và dầu thô.
5. **Quantitative & Risk Analyst:** Chuyên gia phân tích dữ liệu, xác suất, tương quan, biến động, xây dựng kịch bản và quản trị rủi ro.

Nhiệm vụ của bạn là phân tích toàn diện tất cả nguồn dữ liệu được cung cấp, xây dựng một báo cáo nghiên cứu chiến lược thị trường chuyên nghiệp, tập trung vào **Gold (XAU/USD) và Silver (XAG/USD)**.

Báo cáo phải kết hợp phân tích vĩ mô, vi mô, Price Action, liên thị trường, dữ liệu định lượng và dự báo theo kịch bản.

Không chỉ mô tả thị trường đang diễn biến như thế nào, mà phải giải thích **tại sao thị trường diễn biến như vậy, điều gì có thể xảy ra tiếp theo, điều kiện nào xác nhận dự báo và những rủi ro nào có thể khiến nhận định sai lệch**.

---

# I. DATA UNIVERSE – PHẠM VI DỮ LIỆU PHÂN TÍCH

Tôi đã tổng hợp dữ liệu từ 9 nguồn sau:

| Mã dữ liệu | Tài sản / Chỉ báo | Vai trò trong phân tích |
|---|---|---|
| XAUUSD | Vàng giao ngay so với USD | Tài sản trọng tâm số 1 |
| SPY | ETF theo dõi S&P 500 | Đại diện cho thị trường cổ phiếu Mỹ và tâm lý rủi ro |
| BTC-USD | Bitcoin so với USD | Tham chiếu tài sản số và khẩu vị rủi ro |
| XAGUSD | Bạc giao ngay so với USD | Tài sản trọng tâm số 2 |
| ^TNX | Lợi suất trái phiếu Chính phủ Mỹ kỳ hạn 10 năm theo quy ước dữ liệu của nguồn | Phân tích lợi suất danh nghĩa |
| DX-Y.NYB | Chỉ số USD/DXY | Đánh giá sức mạnh tương đối của USD |
| CL=F | Hợp đồng tương lai dầu thô WTI | Tham chiếu năng lượng, lạm phát và chu kỳ kinh tế |
| MGC=F | Hợp đồng tương lai Micro Gold | Tham chiếu thị trường hợp đồng tương lai vàng |
| ZQ=F | Hợp đồng tương lai 30-Day Fed Funds theo mã dữ liệu | Tham chiếu kỳ vọng lãi suất Fed, cần xác minh đặc tả hợp đồng |

Hãy sử dụng đủ 9 nguồn trên khi dữ liệu có sẵn và phù hợp. Không bắt buộc mọi nguồn đều phải có ảnh hưởng trực tiếp đến kết luận về vàng và bạc.

**Nguyên tắc quan trọng:** XAUUSD và XAGUSD là trọng tâm chính. Các nguồn còn lại đóng vai trò xác định bối cảnh, kiểm chứng giả thuyết, đánh giá tâm lý thị trường và phát hiện rủi ro liên thị trường.

Không xem các tài sản này là những chỉ báo thay thế hoàn hảo cho nhau. Mỗi tài sản phản ánh một nhóm động lực riêng.

## 1.1. Kiểm tra dữ liệu trước khi phân tích

Trước tiên, hãy kiểm tra:

- Thời điểm bắt đầu và kết thúc của dữ liệu.
- Tần suất dữ liệu: intraday, hourly, daily, weekly hay monthly.
- Múi giờ, đơn vị giá và loại giá được cung cấp.
- Các khoảng dữ liệu bị thiếu, dữ liệu trùng lặp và điểm bất thường.
- Dữ liệu lịch sử hay dữ liệu gần thời gian thực.
- Khả năng đồng bộ ngày giao dịch giữa các thị trường.
- Sự khác biệt giữa giá giao ngay và giá hợp đồng tương lai.
- Khả năng sai lệch do rollover hợp đồng tương lai hoặc điều chỉnh dữ liệu.

Không mặc định dữ liệu mới nhất trong file chính là giá thị trường hiện tại.

Đối với ^TNX, hãy xác minh quy ước đơn vị của nguồn. Nếu được cung cấp theo quy ước thông thường của Yahoo Finance, chỉ số được biểu diễn theo đơn vị phần trăm lợi suất, không phải giá trái phiếu.

Đối với ZQ=F, hãy xác minh đặc tả hợp đồng, quy ước giá và thời điểm đáo hạn trước khi suy luận kỳ vọng lãi suất. Không diễn giải giá hợp đồng như lãi suất Fed trực tiếp nếu chưa xác minh công thức chuyển đổi và kỳ hạn.

Đối với MGC=F, phân biệt rõ diễn biến của hợp đồng tương lai Micro Gold với XAUUSD giao ngay.

Nếu thiếu thông tin cần thiết, hãy nêu rõ giới hạn và tiếp tục phân tích trong phạm vi dữ liệu có thể kiểm chứng.

---

# II. EXECUTIVE SUMMARY – TÓM TẮT ĐIỀU HÀNH

Mở đầu báo cáo bằng phần tóm tắt dành cho nhà đầu tư, trader và người nghiên cứu thị trường.

Trình bày:

1. Toàn cảnh thị trường tài chính tại thời điểm chốt dữ liệu.
2. Trạng thái hiện tại của vàng và bạc.
3. Các động lực vĩ mô quan trọng nhất.
4. Tín hiệu từ USD, lợi suất Mỹ, SPY, Bitcoin và dầu thô.
5. Các điểm đồng thuận hoặc mâu thuẫn giữa phân tích cơ bản và Price Action.
6. Kịch bản cơ sở, kịch bản tăng và kịch bản giảm.
7. Các vùng giá quan trọng nếu dữ liệu cho phép.
8. Những sự kiện và rủi ro cần theo dõi.

Tạo bảng tổng hợp:

| Tiêu chí | Gold | Silver |
|---|---|---|
| Trạng thái xu hướng | | |
| Động lực cơ bản | | |
| Tín hiệu Price Action | | |
| Yếu tố liên thị trường | | |
| Kịch bản cơ sở | | |
| Rủi ro lớn nhất | | |
| Điều kiện xác nhận | | |

Phân biệt rõ dữ kiện, nhận định và dự báo. Không khẳng định hướng đi tiếp theo nếu bằng chứng chưa đủ mạnh.

---

# III. GLOBAL MARKET REGIME – TOÀN CẢNH THỊ TRƯỜNG

Phân tích bức tranh tổng thể trước khi đi sâu vào vàng và bạc.

Mục tiêu là xác định thị trường đang ở trạng thái nào:

- Risk-on: nhà đầu tư có xu hướng chấp nhận rủi ro.
- Risk-off: nhà đầu tư có xu hướng giảm rủi ro.
- Inflationary regime: thị trường nhạy cảm với áp lực lạm phát.
- Disinflationary regime: áp lực lạm phát có xu hướng giảm.
- Tightening hoặc easing expectations: kỳ vọng chính sách tiền tệ thắt chặt hoặc nới lỏng.
- Growth slowdown hoặc expansion: tăng trưởng kinh tế chậm lại hoặc mở rộng.

Không phân loại trạng thái thị trường chỉ từ một chỉ báo.

Hãy kết hợp các dữ liệu có sẵn để trả lời:

1. Thị trường cổ phiếu Mỹ đang thể hiện điều gì thông qua SPY?
2. Bitcoin đang phản ánh khẩu vị rủi ro như thế nào, nếu có bằng chứng?
3. DXY đang hỗ trợ hay gây áp lực lên các tài sản định giá bằng USD?
4. Lợi suất Mỹ đang phản ánh thay đổi kỳ vọng tăng trưởng, lạm phát hay chính sách tiền tệ?
5. Giá dầu cho thấy tín hiệu gì về năng lượng, lạm phát và nhu cầu kinh tế?
6. Các tín hiệu này đang đồng thuận hay mâu thuẫn?
7. Bối cảnh tổng thể có thuận lợi cho vàng và bạc hay không, và trong điều kiện nào?

Hãy xây dựng một Market Regime Dashboard với các cột:

| Biến số | Trạng thái quan sát được | Hàm ý thị trường | Tác động tiềm năng đến Gold | Tác động tiềm năng đến Silver | Độ tin cậy |
|---|---|---|---|---|---|

Không áp đặt quy luật rằng cổ phiếu tăng thì vàng phải giảm, Bitcoin tăng thì vàng phải giảm, hoặc lợi suất tăng thì vàng luôn giảm. Hãy phân tích cơ chế tác động và bối cảnh cụ thể.

---

# IV. MACROECONOMIC ANALYSIS – PHÂN TÍCH VĨ MÔ

Phân tích những yếu tố có thể quyết định xu hướng vàng và bạc.

## 4.1. Federal Reserve và kỳ vọng lãi suất

Sử dụng ZQ=F khi dữ liệu và đặc tả hợp đồng phù hợp. Kết hợp thêm nguồn dữ liệu chính thức nếu được phép.

Phân tích:

- Định hướng chính sách của Fed.
- Kỳ vọng lãi suất hiện tại.
- Sự khác biệt giữa kỳ vọng thị trường và quyết định thực tế.
- Những dữ liệu có thể khiến kỳ vọng lãi suất thay đổi.
- Cách thay đổi kỳ vọng chính sách có thể tác động đến USD, lợi suất và vàng.

Phân biệt lãi suất chính sách thực tế, lãi suất kỳ vọng và lợi suất thị trường.

## 4.2. US Treasury Yield – Lợi suất trái phiếu Mỹ

Sử dụng ^TNX để phân tích lợi suất danh nghĩa kỳ hạn 10 năm.

Phân tích:

- Xu hướng lợi suất.
- Tốc độ và biên độ thay đổi.
- Mối quan hệ giữa lợi suất và giá vàng.
- Tác động tiềm năng đến bạc.
- Khả năng thay đổi kỳ vọng lạm phát và tăng trưởng.

Nếu có dữ liệu, bổ sung lợi suất thực TIPS và lợi suất kỳ hạn 2 năm. Nếu không có, hãy nói rõ rằng chỉ phân tích ^TNX không đủ để xác định chính xác biến động của lợi suất thực.

## 4.3. US Dollar – DXY

Sử dụng DX-Y.NYB để phân tích:

- Xu hướng USD.
- Cấu trúc giá và các vùng kỹ thuật quan trọng.
- Mối quan hệ giữa DXY và XAUUSD/XAGUSD.
- Những giai đoạn vàng hoặc bạc không đi theo tương quan thông thường với USD.
- Các điều kiện có thể làm tương quan thay đổi.

## 4.4. Crude Oil – CL=F

Phân tích:

- Xu hướng giá dầu.
- Các yếu tố cung cầu năng lượng.
- Tín hiệu về áp lực lạm phát và chu kỳ kinh tế.
- Tác động gián tiếp thông qua kỳ vọng lạm phát và chính sách Fed.
- Khả năng giá dầu tăng do cú sốc nguồn cung thay vì tăng trưởng nhu cầu.

Không mặc định dầu tăng luôn có lợi cho vàng hoặc bạc.

## 4.5. Kết luận vĩ mô

Tổng hợp chuỗi tác động:

**Dữ liệu kinh tế → Kỳ vọng Fed → Lợi suất và USD → Dòng vốn và tâm lý → Gold/Silver.**

Xác định những biến số có ảnh hưởng trực tiếp, những biến số có ảnh hưởng gián tiếp và các giả định chưa được kiểm chứng.

---

# V. GOLD DEEP DIVE – PHÂN TÍCH CHUYÊN SÂU VÀNG

Đây là một trong hai phần trọng tâm nhất của báo cáo.

## 5.1. Fundamental Analysis

Phân tích các yếu tố cơ bản:

- Chính sách tiền tệ và nhu cầu nắm giữ tài sản không sinh lãi.
- Nhu cầu ngân hàng trung ương.
- Dòng vốn ETF vàng.
- Nhu cầu vàng vật chất và trang sức.
- Nguồn cung khai thác và tái chế.
- Địa chính trị và nhu cầu trú ẩn.
- Dòng vốn toàn cầu và nhu cầu đa dạng hóa tài sản.

Chỉ đưa ra kết luận về cung cầu khi có dữ liệu phù hợp. Không suy luận trực tiếp nhu cầu vàng vật chất từ biến động giá XAUUSD.

## 5.2. Price Action Analysis

Phân tích XAUUSD theo các khung thời gian phù hợp với dữ liệu:

- Monthly/Weekly: xu hướng dài hạn và cấu trúc lớn.
- Daily: xu hướng trung hạn và vùng giá chiến lược.
- H4/H1: cấu trúc ngắn hạn và tín hiệu xác nhận.
- M15: chỉ sử dụng nếu có dữ liệu đủ chi tiết và cần đánh giá giao dịch ngắn hạn.

Xác định:

- Market Structure.
- Higher High, Higher Low, Lower High và Lower Low.
- Break of Structure (BOS).
- Change of Character (CHoCH).
- Support và Resistance.
- Supply và Demand.
- Liquidity pools và vùng có khả năng quét thanh khoản.
- Breakout, false breakout và vùng retest.
- Momentum và phản ứng giá tại các vùng quan trọng.

Không đánh dấu vùng giá chỉ dựa trên cảm tính. Mỗi vùng phải có cơ sở từ dữ liệu giá và được phân biệt thành vùng đã xác nhận hoặc vùng giả thuyết.

## 5.3. Futures Confirmation

Sử dụng MGC=F để tham chiếu thị trường hợp đồng tương lai vàng.

So sánh với XAUUSD trong phạm vi dữ liệu cho phép:

- Xu hướng giá.
- Động lượng.
- Các vùng kỹ thuật.
- Sự khác biệt về phiên giao dịch và cấu trúc dữ liệu.
- Tín hiệu xác nhận hoặc mâu thuẫn.

Không xem MGC=F là bằng chứng độc lập hoàn toàn với XAUUSD vì hai chuỗi dữ liệu cùng phản ánh thị trường vàng và có liên hệ chặt chẽ.

## 5.4. Gold Outlook

Kết luận:

- Xu hướng chủ đạo.
- Động lực mạnh nhất hỗ trợ giá.
- Động lực mạnh nhất gây áp lực.
- Những vùng giá quan trọng.
- Điều kiện xác nhận tiếp diễn xu hướng.
- Điều kiện cảnh báo đảo chiều.
- Các yếu tố có thể làm thay đổi nhận định.

---

# VI. SILVER DEEP DIVE – PHÂN TÍCH CHUYÊN SÂU BẠC

Đây là phần trọng tâm thứ hai.

## 6.1. Fundamental Analysis

Phân tích:

- Nhu cầu bạc trong công nghiệp.
- Ứng dụng trong năng lượng mặt trời, điện tử và các ngành công nghệ.
- Nguồn cung khai thác và tái chế.
- Cán cân cung cầu nếu có số liệu đáng tin cậy.
- Tác động của chu kỳ kinh tế toàn cầu.
- Vai trò kép của bạc: kim loại quý và kim loại công nghiệp.

## 6.2. Price Action Analysis

Áp dụng quy trình phân tích tương tự XAUUSD cho XAGUSD.

Xác định:

- Cấu trúc xu hướng.
- Vùng hỗ trợ và kháng cự.
- Supply/Demand.
- BOS, CHoCH.
- Thanh khoản và các vùng breakout.
- Động lượng, biến động và rủi ro phá vỡ giả.

Đặc biệt đánh giá liệu tín hiệu kỹ thuật của bạc có được hỗ trợ bởi bối cảnh vĩ mô và nhu cầu công nghiệp hay không.

## 6.3. Gold/Silver Ratio

Nếu có dữ liệu đồng bộ, tính:

Gold/Silver Ratio = Giá vàng giao ngay / Giá bạc giao ngay.

Phân tích:

- Xu hướng tỷ lệ vàng/bạc.
- Bạc đang tăng hoặc giảm tương đối so với vàng.
- Những thay đổi có thể phản ánh khẩu vị rủi ro hoặc triển vọng tăng trưởng.
- Những giới hạn khi sử dụng tỷ lệ này để dự báo.

Không kết luận bạc chắc chắn sẽ tăng chỉ vì tỷ lệ vàng/bạc đang cao, hoặc ngược lại.

## 6.4. Silver Outlook

Kết luận:

- Xu hướng chủ đạo.
- Động lực cơ bản.
- Tín hiệu Price Action.
- Mối liên hệ với vàng.
- Những điều kiện có thể giúp bạc vượt trội hoặc suy yếu tương đối.
- Các vùng giá quan trọng và điều kiện vô hiệu hóa nếu dữ liệu cho phép.

---

# VII. CROSS-ASSET ANALYSIS – PHÂN TÍCH LIÊN THỊ TRƯỜNG

Sử dụng tất cả các nguồn dữ liệu có liên quan để kiểm tra các giả thuyết về vàng và bạc.

## 7.1. XAUUSD và DXY

Đánh giá tương quan và sự thay đổi tương quan giữa vàng và USD.

## 7.2. XAUUSD và ^TNX

Đánh giá mối liên hệ với lợi suất danh nghĩa, đồng thời nêu rõ giới hạn khi chưa có lợi suất thực.

## 7.3. XAUUSD và MGC=F

Đối chiếu giao ngay với hợp đồng tương lai, kiểm tra độ nhất quán của tín hiệu và sự khác biệt về dữ liệu.

## 7.4. XAGUSD và CL=F

Đánh giá các kênh tác động thông qua tăng trưởng, lạm phát, năng lượng và chu kỳ công nghiệp.

## 7.5. Gold/Silver so với SPY

Đánh giá liệu thị trường đang ưu tiên tài sản trú ẩn hay tài sản rủi ro, đồng thời tránh coi sự đồng biến hoặc nghịch biến trong một giai đoạn ngắn là quy luật lâu dài.

## 7.6. Gold/Silver so với BTC-USD

Phân tích Bitcoin như một tài sản số có biến động cao và động lực riêng. Không mặc định Bitcoin là tài sản trú ẩn tương đương vàng.

## 7.7. Quantitative Cross-Asset Dashboard

Nếu dữ liệu đủ điều kiện, tính toán:

- Returns theo ngày, tuần và tháng.
- Rolling correlation giữa XAUUSD và các biến liên quan.
- Rolling volatility.
- Drawdown.
- Relative performance.
- Gold/Silver Ratio.
- Các giai đoạn tương quan thay đổi đáng kể.

Đảm bảo các chuỗi dữ liệu được đồng bộ thời gian, xử lý ngày thiếu và dùng cùng quy ước lợi suất.

Phân biệt tương quan với quan hệ nhân quả. Không suy luận rằng một tài sản gây ra biến động của tài sản khác chỉ vì chúng tương quan.

---

# VIII. SCENARIO ANALYSIS – PHÂN TÍCH KỊCH BẢN

Xây dựng ba kịch bản riêng cho vàng và bạc.

## Scenario A – Bullish

Xác định:

- Các điều kiện vĩ mô hỗ trợ.
- Tín hiệu xác nhận từ USD và lợi suất.
- Cấu trúc Price Action cần xuất hiện.
- Vùng giá có thể hướng tới nếu đủ dữ liệu.
- Điều kiện khiến kịch bản thất bại.

## Scenario B – Bearish

Xác định:

- Những điều kiện có thể gây áp lực.
- Các tín hiệu từ USD, lợi suất và tài sản liên quan.
- Vùng hỗ trợ có nguy cơ bị phá vỡ.
- Điều kiện xác nhận xu hướng giảm.
- Điều kiện khiến kịch bản thất bại.

## Scenario C – Neutral / Consolidation

Xác định:

- Điều kiện thị trường đi ngang.
- Các vùng biên độ nếu dữ liệu cho phép.
- Những tín hiệu xác nhận breakout.
- Các điều kiện cần chờ trước khi kết luận xu hướng.

Tạo bảng tổng hợp:

| Tài sản | Kịch bản | Điều kiện kích hoạt | Vùng mục tiêu | Điều kiện vô hiệu hóa | Độ tin cậy |
|---|---|---|---|---|---|

Nếu đưa ra xác suất, hãy giải thích phương pháp ước lượng và dữ liệu hỗ trợ. Không tạo xác suất chính xác giả tạo.

---

# IX. FORECAST HORIZONS – DỰ BÁO THEO THỜI GIAN

Đưa ra triển vọng cho từng tài sản theo các khung:

- Ngắn hạn: 1–5 phiên giao dịch.
- Trung hạn: 1–4 tuần.
- Dài hơn: 1–3 tháng.
- Dài hạn: 6–12 tháng nếu dữ liệu cơ bản đủ cơ sở.

Đối với mỗi giai đoạn, trình bày:

1. Xu hướng cơ sở.
2. Các kịch bản thay thế.
3. Những vùng giá quan trọng.
4. Các động lực chính.
5. Những yếu tố có thể làm dự báo sai.
6. Dữ liệu cần theo dõi để cập nhật.
7. Điều kiện xác nhận hoặc vô hiệu hóa.

Không ngoại suy tuyến tính từ dữ liệu quá khứ để tạo mục tiêu giá. Không đưa ra mức giá cụ thể nếu không có dữ liệu giá đáng tin cậy.

---

# X. RISK MANAGEMENT – QUẢN TRỊ RỦI RO

Đánh giá:

- Rủi ro sự kiện kinh tế.
- Rủi ro biến động lãi suất và USD.
- Rủi ro địa chính trị.
- Rủi ro thanh khoản.
- Rủi ro phá vỡ giả.
- Rủi ro đòn bẩy.
- Rủi ro tương quan thay đổi.
- Rủi ro từ chất lượng và độ trễ của dữ liệu.

Đề xuất một khung quản trị rủi ro dựa trên nguyên tắc:

- Xác định điều kiện vô hiệu hóa trước khi giao dịch.
- Đặt mức rủi ro phù hợp với mức biến động.
- Tính toán vị thế từ khoảng cách đến điểm vô hiệu hóa và mức rủi ro cho phép.
- Đánh giá tổng rủi ro khi nắm giữ đồng thời vàng và bạc.
- Hạn chế giao dịch khi dữ liệu hoặc cấu trúc thị trường chưa rõ ràng.

Không đưa ra khuyến nghị mua bán chắc chắn hoặc cam kết lợi nhuận.

---

# XI. EVENT RISK & MONITORING PLAN

Tạo danh sách các dữ liệu và sự kiện cần theo dõi:

- Quyết định lãi suất và phát biểu của Fed.
- CPI, PCE và dữ liệu việc làm Mỹ.
- GDP, PMI và các chỉ báo tăng trưởng.
- Biến động DXY.
- ^TNX và lợi suất thực nếu có.
- Diễn biến SPY, Bitcoin và dầu thô.
- Dữ liệu cung cầu vàng, bạc.
- Các sự kiện địa chính trị quan trọng.

Phân loại mỗi yếu tố theo:

- Mức độ quan trọng.
- Tác động tiềm năng.
- Tần suất cập nhật.
- Điều kiện có thể khiến nhận định thị trường thay đổi.

Chỉ đưa ngày và số liệu kỳ vọng nếu có nguồn đáng tin cậy. Ghi rõ thời điểm cập nhật và múi giờ.

---

# XII. FINAL INVESTMENT RESEARCH REPORT – CẤU TRÚC ĐẦU RA

Hãy xuất bản báo cáo theo cấu trúc nghiên cứu chuyên nghiệp sau:

1. Cover Page – Tiêu đề, thời điểm chốt dữ liệu và phạm vi phân tích.
2. Executive Summary – Các kết luận quan trọng.
3. Global Market Overview – Toàn cảnh thị trường.
4. Macroeconomic Analysis – Phân tích vĩ mô.
5. Gold Deep Dive – Phân tích chuyên sâu vàng.
6. Silver Deep Dive – Phân tích chuyên sâu bạc.
7. Cross-Asset Analysis – Phân tích liên thị trường.
8. Quantitative Analysis – Thống kê, tương quan và biến động nếu có dữ liệu.
9. Scenario Analysis – Các kịch bản thị trường.
10. Forecast – Dự báo theo thời gian.
11. Risk Management – Quản trị rủi ro.
12. Event Risk & Monitoring Plan – Kế hoạch theo dõi.
13. Final Strategic Conclusions – Kết luận chiến lược.
14. Data Sources & Methodology – Nguồn dữ liệu, phương pháp và giới hạn.

Sử dụng bảng biểu, biểu đồ và các chỉ số định lượng khi có dữ liệu hỗ trợ. Mỗi biểu đồ phải có tiêu đề, đơn vị, khung thời gian và nguồn.

Trình bày báo cáo bằng tiếng Việt chuyên nghiệp, có chiều sâu, lập luận logic và tránh lặp lại nội dung.

Mọi kết luận quan trọng phải theo chuỗi:

**Dữ liệu → Quan sát → Phân tích → Hàm ý đối với Gold/Silver → Kịch bản → Rủi ro → Điều kiện xác nhận.**

# XIII. QUALITY CONTROL – KIỂM SOÁT CHẤT LƯỢNG

Trước khi hoàn tất, hãy tự kiểm tra:

- Đã đánh giá đủ 9 nguồn dữ liệu hay chưa?
- Đã xác định rõ thời điểm chốt dữ liệu hay chưa?
- Đã phân biệt giá giao ngay và hợp đồng tương lai hay chưa?
- Đã phân biệt lợi suất danh nghĩa và lợi suất thực hay chưa?
- Đã kiểm tra tính đồng bộ của dữ liệu khi tính tương quan hay chưa?
- Đã phân biệt dữ kiện với giả thuyết và dự báo hay chưa?
- Đã đánh giá cả kịch bản tăng và giảm hay chưa?
- Các vùng giá và mục tiêu dự báo có cơ sở từ dữ liệu hay không?
- Các rủi ro và điều kiện vô hiệu hóa đã được nêu rõ chưa?
- Những hạn chế của nguồn dữ liệu đã được công khai chưa?

Nếu chưa đủ dữ liệu để kết luận, hãy nêu rõ điều gì còn thiếu thay vì bịa đặt hoặc tạo ra sự chính xác giả tạo.

# FINAL OBJECTIVE

Tạo một báo cáo **Institutional-Style Gold & Silver Market Strategy Report** có chất lượng chuyên nghiệp, kết hợp phân tích định tính và định lượng, lấy XAUUSD và XAGUSD làm trọng tâm, đồng thời sử dụng SPY, BTC-USD, ^TNX, DX-Y.NYB, CL=F, MGC=F và ZQ=F làm các nguồn tham chiếu liên thị trường phù hợp.

Báo cáo phải giúp người đọc hiểu được trạng thái thị trường, động lực giá, sự liên kết giữa các tài sản, những kịch bản có thể xảy ra và cách đánh giá rủi ro một cách có hệ thống.

Ưu tiên tính chính xác, khả năng kiểm chứng, chiều sâu phân tích và tính hữu ích trong việc ra quyết định hơn độ dài của báo cáo.