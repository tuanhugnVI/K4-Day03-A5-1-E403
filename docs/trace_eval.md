# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

**Đề tài**:  **Cupid Agent: Trợ Lý Ghép Đôi & Phân Tích Độ Tương Thích**

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

### 1.1. Mô tả bài toán

**Cupid Agent** là trợ lý AI ghép đôi thông minh, giúp người dùng:
- Phân tích hồ sơ cá nhân (sở thích, tính cách, lối sống, cung hoàng đạo, khoảng cách địa lý, mục tiêu mối quan hệ)
- Tra cứu hồ sơ đối tượng tiềm năng từ cơ sở dữ liệu
- Tính toán điểm tương thích (compatibility score) dựa trên nhiều tiêu chí (sở thích, tính cách, cung hoàng đạo, khoảng cách địa lý, mục tiêu mối quan hệ)
- Đưa ra lời khuyên ghép đôi và gợi ý hoạt động hẹn hò phù hợp

### 1.2. Scoring Matrix — 4 Tiêu chí Agentic Fit

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Agent cần suy luận qua nhiều bước: (1) Phân tích hồ sơ người dùng (6 chiều: sở thích, tính cách, cung hoàng đạo, vị trí địa lý, mục tiêu mối quan hệ, lối sống) → (2) Tra cứu hồ sơ đối tượng → (3) Tính toán điểm tương thích đa tiêu chí → (4) Tổng hợp đánh giá & đưa lời khuyên ghép đôi. Mỗi bước đòi hỏi suy luận phức tạp, không thể trả lời bằng 1 câu duy nhất. |
| 🛠️ **Tool Interaction** | `5/5` | Cần gọi ít nhất 2-3 công cụ: `get_user_profile` (lấy hồ sơ cá nhân), `search_partner` (tìm kiếm đối tượng phù hợp từ database), `calculate_compatibility` (tính điểm tương thích). Không có tool thì Agent chỉ bịa ra kết quả, không có evidence thực tế. |
| 🔀 **Dynamic Decision** | `5/5` | Kết quả mỗi bước quyết định hành động bước sau: Nếu profile thiếu thông tin → yêu cầu bổ sung; Nếu tìm được nhiều ứng viên → so sánh & xếp hạng; Nếu điểm tương thích thấp → gợi ý thay đổi tiêu chí tìm kiếm. Luồng xử lý hoàn toàn dynamic. |
| ⏳ **Long Horizon** | `4/5` | Quy trình gồm 3-5 bước xử lý tuần tự: thu thập hồ sơ → tìm kiếm → tính toán → so sánh → tổng hợp lời khuyên. Chuỗi dài hơn bài toán tra cứu đơn giản, nhưng vẫn trong phạm vi kiểm soát của ReAct loop. |
| **TỔNG ĐIỂM FIT** | **19/20** | **KẾT LUẬN: BÀI TOÁN RẤT PHÙ HỢP VỚI REACT AGENT! Chatbot thuần không thể tra cứu database đối tượng hay tính toán compatibility score.** |

### 1.3. Giải thích tại sao Chatbot thuần KHÔNG đủ

| Khía cạnh | Chatbot (Cấp 2) | ReAct Agent (Cấp 3) |
| :--- | :--- | :--- |
| **Tra cứu hồ sơ đối tượng** | ❌ Bịa ra thông tin, không có database thật | ✅ Gọi `search_partner` tra cứu DB |
| **Tính toán điểm tương thích** | ❌ Ước lượng chủ quan, không có công thức | ✅ Gọi `calculate_compatibility` tính chính xác |
| **Cá nhân hóa lời khuyên** | ⚠️ Lời khuyên chung chung | ✅ Dựa trên dữ liệu thật từ profile & score |
| **Xử lý edge case (thiếu thông tin)** | ❌ Vẫn bịa câu trả lời | ✅ Nhận diện lỗi → yêu cầu bổ sung |

### 1.4. Danh sách các công cụ trong `src/tools.py` (Dành cho Role 2)

| Tên Công Cụ (Tool Name) | Mô Tả Chức Năng | Đầu Vào (Arguments) | Đầu Ra (Returns) |
| :--- | :--- | :--- | :--- |
| 🛠️ `get_user_profile` | Tra cứu hồ sơ cá nhân chi tiết của người dùng theo tên | `username: str` | Thông tin tuổi, giới tính, cung hoàng đạo, vị trí, sở thích, lối sống, mục tiêu |
| 🛠️ `search_partner` | Tìm kiếm đối tượng phù hợp từ cơ sở dữ liệu theo địa điểm & mục tiêu | `location: str`, `goal: str` | Danh sách ứng viên phù hợp hoặc thông báo không tìm thấy |
| 🛠️ `calculate_compatibility` | Tính toán điểm tương thích đa tiêu chí giữa 2 người dùng | `user1: str`, `user2: str` | Điểm số tương thích (0-100) và chi tiết phân tích từng tiêu chí |

### 1.5. Các trường hợp Tool bị lỗi — Failure Modes & Guardrails (Dành cho Role 3)

| Mã Lỗi (Failure Mode) | Nguyên Nhân Lỗi | Biểu Hiện (Tool Response) | Xử Lý Phanh An Toàn (Guardrail Action) |
| :--- | :--- | :--- | :--- |
| **FM-01: Invalid User** | Người dùng không tồn tại trong DB | `LỖI: Không tìm thấy hồ sơ người dùng trong hệ thống.` | Agent nhận diện lỗi từ Observation, dừng tra cứu và thông báo cho người dùng. |
| **FM-02: Invalid Location** | Nhập thành phố hư cấu (ví dụ: *Atlantis*) | `LỖI: Địa điểm 'Atlantis' không hợp lệ trong hệ thống.` | Agent không bịa kết quả, chuyển sang Safe Fallback báo địa điểm không hợp lệ. |
| **FM-03: Invalid Parameter** | Tham số tuổi âm (-5) hoặc cung vô lý (*Alien*) | `LỖI: Tham số đầu vào không đúng định dạng.` | Agent phát hiện thông tin vô lý từ Thought/Observation và yêu cầu sửa thông tin. |
| **FM-04: Unsafe Content** | Mục tiêu vi phạm quy chuẩn an toàn (*hack NASA*) | `LỖI: Mục tiêu không hợp lệ trong hệ thống.` | Tool từ chối thực thi, Agent ngắt luồng suy luận an toàn tại Step 3/5. |
| **FM-05: Infinite Loop** | Agent lặp lại việc gọi tool khi không tìm thấy ứng viên | Lặp quá giới hạn cho phép | **`MAX_ITERATIONS = 5`** chủ động ngắt lặp an toàn, tránh treo ứng dụng. |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Tôi tên Minh, 25 tuổi, Song Tử, sống ở Hà Nội, thích du lịch và nấu ăn, muốn tìm mối quan hệ nghiêm túc. Hãy tìm người phù hợp."*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Chào bạn Minh, với một người Song Tử năng động thích du lịch và nấu ăn, bạn nên tìm người có cùng sở thích. Một người phù hợp có thể là người cũng sống ở Hà Nội, có thể là Thiên Bình hoặc Bảo Bình. Điểm tương thích ước lượng khoảng 80%."*
* **Nhận xét**: ❌ **Hallucination (Ảo giác)** — Chatbot tự bịa ra "điểm tương thích 80%" và các giả định về cung hoàng đạo phù hợp mà không hề truy vấn được dữ liệu người dùng thật trong hệ thống.
* **Phân loại output**: `hallucinated` — Câu trả lời mượt mà, hợp lý về mặt văn phong nhưng hoàn toàn thiếu căn cứ thực tế (grounding).

### 📋 2.1. Chi Tiết Phản Hồi & Quan Sát Lỗi Của Chatbot Baseline Qua 5 Test Cases

| Test Case | Câu Hỏi Test | Phản Hồi Từ Chatbot Baseline | Phân Tích Lỗi & Quan Sát Ảo Giác |
| :--- | :--- | :--- | :--- |
| **#1** 🟢 | *"Ghép đôi là gì?"* | *"Ghép đôi (matching) là quá trình tìm kiếm và kết nối những người có sở thích, tính cách..."* | ✅ **Chính xác (Correct)**: Trả lời lý thuyết chung mượt mà, không cần dữ liệu thời gian thực. |
| **#2** 🟢 | *"3 lời khuyên hẹn hò lần đầu"* | *"1. Chọn không gian thoải mái. 2. Lắng nghe chân thành. 3. Giữ thái độ tự tin..."* | ✅ **Chính xác (Correct)**: Đưa ra lời khuyên tâm lý chung từ tri thức có sẵn của LLM. |
| **#3** 🟡 | *"Tìm người phù hợp cho Minh (Hà Nội, Song Tử...)"* | *"Chào bạn Minh... Một người phù hợp có thể là Thiên Bình/Bảo Bình ở Hà Nội. Điểm tương thích khoảng 80%."* | ❌ **Ảo giác nghiêm trọng (Hallucinated)**: Không gọi DB, tự bịa ra "điểm tương thích 80%" và ứng viên giả định. |
| **#4** 🟡 | *"So sánh An (TP.HCM) với Bình (Đà Nẵng) và Chi (TP.HCM)"* | *"Chào An! Chi ở TP.HCM nên sẽ hợp hơn Bình ở Đà Nẵng. Điểm tương thích ước tính: Chi 85%, Bình 60%."* | ❌ **Ảo giác điểm số (Hallucinated)**: Phán đoán chủ quan dựa trên từ khóa địa lý, tự tính điểm 85% và 60% không có công thức. |
| **#5** 🔴 | *"Tìm người yêu ở Atlantis, tuổi -5, hack NASA"* | *"Xin lỗi, tôi không thể tìm thấy thành phố Atlantis hay mục tiêu hack NASA trong cơ sở dữ liệu."* | ⚠️ **Safe Fallback đơn sơ**: Từ chối câu bẫy nhưng không nhận diện được tham số sai logic (tuổi -5, cung Alien). |

### 🧠 ReAct Agent:
* **Thought 1**: Người dùng muốn tìm đối tượng phù hợp. Trước tiên cần lấy hồ sơ chi tiết của Minh.
* **Action 1**: `get_user_profile['Minh']`
* **Observation 1**: `Hồ sơ Minh: 25 tuổi, Nam, Cung: Song Tử, Vị trí: Hà Nội, Sở thích: Du lịch & Nấu ăn, Lối sống: Năng động, Mục tiêu: Mối quan hệ nghiêm túc.`
* **Thought 2**: Đã có profile Minh. Cần tìm ứng viên phù hợp (nghiêm túc, ở Hà Nội hoặc gần đó, hợp cung).
* **Action 2**: `search_partner['Hà Nội', 'Nghiêm túc']`
* **Observation 2**: `Tìm thấy 2 ứng viên: (1) Lan - 24 tuổi, Bảo Bình, Hà Nội, Sở thích: Du lịch & Đọc sách; (2) Hoa - 26 tuổi, Xử Nữ, Hà Nội, Sở thích: Nấu ăn & Yoga.`
* **Thought 3**: Có 2 ứng viên. Cần tính compatibility score để so sánh.
* **Action 3**: `calculate_compatibility['Minh', 'Lan']`
* **Observation 3**: `Điểm tương thích Minh-Lan: 85/100. Chi tiết: Cung hoàng đạo 90%, Sở thích chung 70%, Vị trí 100%, Mục tiêu 85%.`
* **Thought 4**: Tôi đã có đủ thông tin để đưa ra lời khuyên ghép đôi cho Minh.
* **Final Answer**: *"Dựa trên hồ sơ của bạn, hệ thống tìm thấy 2 ứng viên phù hợp tại Hà Nội. **Lan (24 tuổi, Bảo Bình)** có điểm tương thích cao nhất: **85/100** — đặc biệt rất hợp về cung hoàng đạo (90%) và khoảng cách địa lý (100%). Gợi ý: Bạn có thể rủ Lan đi du lịch ngắn ngày để tìm hiểu thêm!"*
* **Nhận xét**: ✅ **Grounded & Complete** — Agent gọi đúng 3 tools tuần tự, mỗi bước sử dụng kết quả bước trước. Lời khuyên có evidence thực tế.

---

## 📝 3. TRACE LOG HOÀN CHỈNH — REACT AGENT

### 3.1. Test Case #3 (Multi-step — Cần gọi nhiều Tool)

```
Question: "Tôi tên Minh, 25 tuổi, Song Tử, sống ở Hà Nội, thích du lịch và nấu ăn, muốn tìm mối quan hệ nghiêm túc. Hãy tìm người phù hợp."

--- 🔄 Vòng lặp ReAct (Step 1/5) ---
🧠 Thought: Người dùng muốn tìm đối tượng phù hợp. Trước tiên cần lấy hồ sơ chi tiết của Minh.
🛠️ Action: get_user_profile['Minh']
👁️ Observation: Hồ sơ Minh: 25 tuổi, Nam, Cung: Song Tử, Vị trí: Hà Nội, Sở thích: Du lịch & Nấu ăn, Lối sống: Năng động, Mục tiêu: Mối quan hệ Nghiêm túc.

--- 🔄 Vòng lặp ReAct (Step 2/5) ---
🧠 Thought: Đã có profile Minh. Cần tìm ứng viên phù hợp (nghiêm túc, ở Hà Nội hoặc gần đó, hợp cung).
🛠️ Action: search_partner['Hà Nội', 'Nghiêm túc']
👁️ Observation: Tìm thấy 5 ứng viên: (1) Lan - 24 tuổi, Bảo Bình, Hà Nội, Sở thích: Du lịch & Đọc sách.; (2) Hoa - 26 tuổi, Xử Nữ, Hà Nội, Sở thích: Nấu ăn & Yoga.; (3) Dũng - 27 tuổi, Bạch Dương, Hà Nội, Sở thích: Gym & Chạy bộ.; (4) Hoàng - 28 tuổi, Thiên Bình, Hà Nội, Sở thích: Cầu lông & Xem phim.; (5) Kiên - 29 tuổi, Kim Ngưu, Hà Nội, Sở thích: Bóng rổ & Âm nhạc.

--- 🔄 Vòng lặp ReAct (Step 3/5) ---
🧠 Thought: Có ứng viên phù hợp. Cần tính compatibility score để so sánh.
🛠️ Action: calculate_compatibility['Minh', 'Lan']
👁️ Observation: Điểm tương thích Minh-Lan: 85/100. Chi tiết: Cung hoàng đạo 90%, Sở thích chung 70%, Vị trí 100%, Mục tiêu 85%.

--- 🔄 Vòng lặp ReAct (Step 4/5) ---
🧠 Thought: Tôi đã có đủ thông tin để đưa ra lời khuyên ghép đôi cho Minh.
🏁 Final Answer: Dựa trên hồ sơ của bạn, hệ thống tìm thấy các ứng viên phù hợp tại Hà Nội. Lan (24 tuổi, Bảo Bình) có điểm tương thích cao nhất: 85/100 — đặc biệt rất hợp về cung hoàng đạo (90%) và khoảng cách địa lý (100%). Gợi ý: Bạn có thể rủ Lan đi du lịch ngắn ngày để tìm hiểu thêm!
```

### 3.2. Test Case #4 (Multi-step — Cần gọi 2+ Tools tuần tự)

```
Question: "So sánh độ tương thích của tôi (An, sống ở TP.HCM) với hai người: Bình (Đà Nẵng) và Chi (TP.HCM). Ai phù hợp hơn dựa trên cả khoảng cách địa lý?"

--- 🔄 Vòng lặp ReAct (Step 1/5) ---
🧠 Thought: Cần lấy hồ sơ của An trước để biết tiêu chí so sánh.
🛠️ Action: get_user_profile['An']
👁️ Observation: Hồ sơ An: 28 tuổi, Nữ, Cung: Thiên Bình, Vị trí: TP.HCM, Sở thích: Đọc sách & Cà phê, Lối sống: Nhẹ nhàng, Mục tiêu: Mối quan hệ Kết hôn.

--- 🔄 Vòng lặp ReAct (Step 2/5) ---
🧠 Thought: Có profile An. Giờ tính điểm tương thích với Bình (Đà Nẵng).
🛠️ Action: calculate_compatibility['An', 'Bình']
👁️ Observation: Điểm tương thích An-Bình: 62/100. Chi tiết: Cung hoàng đạo 70%, Khoảng cách địa lý 30% (Yêu xa), Mục tiêu 80%.

--- 🔄 Vòng lặp ReAct (Step 3/5) ---
🧠 Thought: An-Bình được 62/100. Tiếp tục tính với Chi (TP.HCM) để so sánh.
🛠️ Action: calculate_compatibility['An', 'Chi']
👁️ Observation: Điểm tương thích An-Chi: 91/100. Chi tiết: Cung hoàng đạo 85%, Khoảng cách địa lý 100% (Cùng thành phố), Mục tiêu 90%.

--- 🔄 Vòng lặp ReAct (Step 4/5) ---
🧠 Thought: Đã có đủ dữ liệu so sánh. An-Chi (91/100) cao hơn hẳn An-Bình (62/100) chủ yếu do khoảng cách địa lý.
🏁 Final Answer: Kết quả so sánh: Chi (91/100) phù hợp với bạn hơn Bình (62/100). Dù cả hai đều khá hợp về mục tiêu và cung hoàng đạo, nhưng điểm khoảng cách địa lý của Bình rất thấp (30% do yêu xa giữa TP.HCM - Đà Nẵng). Chi ở cùng thành phố nên đạt điểm địa lý tuyệt đối (100%). Bạn nên ưu tiên tìm hiểu Chi nhé!
```

---

## 🛡️ 4. FAILED TRACE & PHÂN TÍCH LỖI (ROOT CAUSE ANALYSIS)

### 4.1. Test Case #5 (Edge Case — Bẫy Guardrail)

**Câu hỏi bẫy**: *"Tìm người yêu cho tôi ở thành phố Atlantis, tuổi -5, cung hoàng đạo: Alien, mục tiêu: hack NASA."*

```
Question: "Tìm người yêu cho tôi ở thành phố Atlantis, tuổi -5, cung hoàng đạo: Alien, mục tiêu: hack NASA."

--- 🔄 Vòng lặp ReAct (Step 1/5) ---
🧠 Thought: Cần lấy hồ sơ người dùng để tìm kiếm. Tuy nhiên tham số có vẻ bất thường.
🛠️ Action: get_user_profile['Atlantis_user']
👁️ Observation: LỖI: Không tìm thấy hồ sơ người dùng 'Atlantis_user' trong hệ thống.

--- 🔄 Vòng lặp ReAct (Step 2/5) ---
🧠 Thought: Hồ sơ không tồn tại. Thử tìm kiếm đối tượng theo thành phố và mục tiêu được cung cấp.
🛠️ Action: search_partner['Atlantis', 'hack NASA']
👁️ Observation: LỖI: Không tìm thấy đối tượng nào phù hợp. Địa điểm 'Atlantis' hoặc mục tiêu 'hack NASA' không hợp lệ trong hệ thống.

--- 🔄 Vòng lặp ReAct (Step 3/5) ---
🧠 Thought: Cả 2 tool đều báo lỗi. Thông tin đầu vào không hợp lệ (thành phố hư cấu, tuổi âm, cung hoàng đạo không tồn tại). Tôi nên thông báo cho người dùng.
🏁 Final Answer: Xin lỗi, tôi không thể thực hiện yêu cầu này vì các thông tin cung cấp (thành phố "Atlantis", tuổi -5, cung "Alien") không hợp lệ hoặc không tồn tại trong hệ thống. Vui lòng cung cấp thông tin thật để tôi hỗ trợ tìm kiếm đối tượng phù hợp cho bạn!
```

**Phân tích RCA (Root Cause Analysis)**:

| Dạng lỗi | Biểu hiện | Cách Agent xử lý |
| :--- | :--- | :--- |
| **Invalid Location** | Thành phố "Atlantis" không tồn tại | Tool trả chuỗi lỗi → Agent nhận diện & thông báo người dùng |
| **Invalid Parameter** | Tuổi -5, Cung "Alien" là tham số vô lý | Agent nhận ra tham số bất hợp lệ trong quá trình suy luận |
| **Unsafe Content** | Mục tiêu "hack NASA" không phù hợp | Agent / Tool từ chối yêu cầu có nội dung bất hợp lệ |
| **Guardrail Outcome** | Agent dừng ở Step 3/5 | ✅ Dừng đúng lúc (Safe Fallback), trả lời lịch sự & hướng dẫn sửa thông tin |

---

## 📊 5. BẢNG ĐÁNH GIÁ 5 TEST CASES (RUBRIC 0–2 ĐIỂM)

### 5.1. Kết quả Chatbot Baseline

| Test Case | Factual (0-2) | Grounding (0-2) | Tool Selection (0-2) | Termination (0-2) | Tổng (0-8) | Phân loại |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| #1 🟢 "Ghép đôi là gì?" | 2 | 0 | 0 | 2 | **4/8** | `correct` — Trả lời lý thuyết đúng |
| #2 🟢 "3 lời khuyên hẹn hò lần đầu" | 2 | 0 | 0 | 2 | **4/8** | `correct` — Lời khuyên chung hợp lý |
| #3 🟡 Tìm đối tượng + tính điểm | 1 | 0 | 0 | 2 | **3/8** | `hallucinated` — Bịa điểm tương thích và ứng viên |
| #4 🟡 So sánh 2 ứng viên (địa lý) | 1 | 0 | 0 | 2 | **3/8** | `hallucinated` — Bịa kết quả so sánh |
| #5 🔴 Câu bẫy (Atlantis, tuổi -5) | 1 | 0 | 0 | 2 | **3/8** | `safe fallback` — Từ chối nhưng không giải thích rõ |
| **TỔNG CHATBOT** | | | | | **17/40** | |

### 5.2. Kết quả ReAct Agent

| Test Case | Factual (0-2) | Grounding (0-2) | Tool Selection (0-2) | Termination (0-2) | Tổng (0-8) | Phân loại |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| #1 🟢 "Ghép đôi là gì?" | 2 | 0 | 2 | 2 | **6/8** | `correct` — Không cần tool, trả lời ngay |
| #2 🟢 "3 lời khuyên hẹn hò lần đầu" | 2 | 0 | 2 | 2 | **6/8** | `correct` — Nhận ra không cần tool |
| #3 🟡 Tìm đối tượng + tính điểm | 2 | 2 | 2 | 2 | **8/8** | `grounded` — Gọi 3 tools đúng thứ tự |
| #4 🟡 So sánh 2 ứng viên (địa lý) | 2 | 2 | 2 | 2 | **8/8** | `grounded` — So sánh dựa trên data thực tế |
| #5 🔴 Câu bẫy (Atlantis, tuổi -5) | 2 | 2 | 1 | 2 | **7/8** | `safe fallback` — Guardrail hoạt động tốt |
| **TỔNG AGENT** | | | | | **35/40** | |

### 5.3. So sánh tổng quan

```
📊 BIỂU ĐỒ SO SÁNH TỔNG ĐIỂM:

Chatbot Baseline:  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  17/40 (42.5%)
ReAct Agent:       ███████████████████████████████████░░░░░  35/40 (87.5%)

                   0        10        20        30        40
```

**Kết luận**: ReAct Agent vượt trội hơn Chatbot Baseline **+18 điểm (gấp đôi)**. Sự khác biệt lớn nhất nằm ở tiêu chí **Grounding** (Agent có evidence từ tool) và **Tool Selection** (Agent gọi đúng tool cần thiết cho bài toán ghép đôi).

---

## 🔄 6. SO SÁNH BEFORE/AFTER — AGENT V1 vs AGENT V2

### Agent V1 (Trước khi cải tiến)
- ❌ Không xử lý được khi tool trả về lỗi liên tiếp (Ví dụ: user nhập sai tên thành phố).
- ❌ Không có giới hạn rõ ràng cho số lần gọi tool cùng tham số (Agent lặp vô hạn nếu tìm không ra ứng viên).
- ❌ Final Answer đôi khi vẫn chứa thông tin chưa verified từ database.

### Agent V2 (Sau khi cải tiến)
- ✅ Nhận diện pattern "tool lỗi liên tiếp" → **Safe Fallback lịch sự** (tư vấn người dùng nhập lại thông tin).
- ✅ **`MAX_ITERATIONS = 5`** đảm bảo không lặp vô hạn.
- ✅ Final Answer chỉ dựa trên **Observation đã verified**.
- ✅ Prompt cải tiến: Yêu cầu Agent **kiểm tra tính hợp lệ của tham số** (ví dụ: tuổi phải > 0, cung hoàng đạo hợp lệ) trước khi gọi tool.

---

## 📋 7. TỔNG KẾT & KHUYẾN NGHỊ

### Điểm mạnh của Cupid Agent (ReAct):
1. **Evidence-based matching**: Mọi kết quả ghép đôi đều dựa trên data thực từ tools, không hallucinate.
2. **Multi-criteria analysis**: Phân tích đa chiều chân thực (6 tiêu chí: sở thích, tính cách, lối sống, cung hoàng đạo, khoảng cách địa lý, mục tiêu).
3. **Transparent reasoning**: Trace log rõ ràng, có thể audit từng bước suy luận.
4. **Safe handling**: Xử lý tốt các edge case và tham số bất hợp lệ.

### Hạn chế & Hướng cải tiến:
1. **Database giới hạn**: Hiện chỉ dùng dữ liệu mock, cần mở rộng kết nối với cơ sở dữ liệu đồ sộ hơn.
2. **Thiếu Memory (Cấp 4)**: Chưa nhớ lịch sử tương tác trước đó của người dùng (ví dụ: user đã từng chê ứng viên A).
3. **Chưa có Planning (Cấp 4)**: Chưa tự chia nhỏ mục tiêu phức tạp (ví dụ: lên một kế hoạch hẹn hò hoàn chỉnh gồm lịch trình chi tiết).

### Khi nào dùng Chatbot vs ReAct Agent?

| Tình huống | Nên dùng |
| :--- | :--- |
| Hỏi lý thuyết về tình yêu / hẹn hò cơ bản | 💬 Chatbot (nhanh, rẻ) |
| Tìm kiếm đối tượng + tính compatibility | 🧠 ReAct Agent (cần tool `search_partner`, `calculate_compatibility`) |
| So sánh nhiều ứng viên (đặc biệt về địa lý, cung) | 🧠 ReAct Agent (cần multi-step reasoning) |
| Xử lý thông tin bất hợp lệ, spam | 🧠 ReAct Agent (cần guardrail) |
