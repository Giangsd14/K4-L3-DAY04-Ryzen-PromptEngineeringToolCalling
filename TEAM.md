# TEAM — Ryzen, Day 04 K4-L3B

## Thông tin bài nộp

- Tên nhóm: Ryzen
- Đại diện / MSSV: Nguyễn Thanh Giang / 2A202602576
- Repository: `K4-L3-DAY04-Ryzen-PromptEngineeringToolCalling`
- URL repository, nhánh nộp, commit chốt: **Điền trước khi nộp**
- Deadline/link thông báo đổi hạn (nếu có): **Điền nếu có**

## Phân công

| Thành viên | MSSV | Vai trò và đầu ra chịu trách nhiệm | Evidence cần điền |
|---|---|---|---|
| Nguyễn Tất Đạt | 2A202602578 | Prompt/tool contract; phân tích failure và v0–v3 | commit/PR cho `artifacts/`, `runs/` |
| Nguyễn Thị Bảo Trang | 2A202602580 | Streamlit UI, tool trace, transcript/redaction | commit/PR cho `starter_v0/app.py`, README, transcript demo |
| Nguyễn Hồng Cường | 2A202602415 | Thiết kế 10 group cases, chạy eval và safety review | commit/PR cho `data/eval_group.json`, `runs/` |
| Đặng Thế Vinh | 2A202602587 | Report, demo script, integration/final checkout | commit/PR cho `REPORT.md`, README, review checklist |

> Phân công là kế hoạch bàn giao. Mỗi người cần thay “commit/PR” bằng hash/link thật và điều chỉnh nếu phần việc thực tế khác kế hoạch.

## Nhận xét chung của nhóm

- Evidence hiện có: base benchmark v0, v1, v2 trong `starter_v0/runs/`; transcript UI v3 trong `starter_v0/transcripts/`; prompt/tool declarations và code tool trong `starter_v0/`.
- Kết quả đáng chú ý: v2 đạt 24/30 base cases (80.00%) với provider error bằng 0; v3 cần được đo lại bằng cùng provider/model trước khi kết luận cải thiện.
- Giới hạn: thiếu run v3 và group run được commit; GitHub username, URL repo và reflection cá nhân chưa được điền.
- Cách tích hợp: mọi PR phải giữ `tools.yaml` khớp tool registry, không commit `.env`, và reviewer mở transcript để kiểm tra result/error đã redacted.

## INDIVIDUAL

Mỗi thành viên tự hoàn thành và commit phần của mình; không thay bằng xác nhận chung của nhóm.

### Nguyễn Tất Đạt — 2A202602578

- Phần việc và file/commit/PR: **Điền commit/PR thật.**
- Quyết định, khó khăn và cách xử lý: **Điền reflection cá nhân.**
- Điều đã học: **Điền reflection cá nhân.**
- AI/công cụ đã dùng và cách kiểm tra: **Điền công cụ và evidence kiểm tra.**
- Thời điểm tự nộp URL repo chung trên VLearn: **Điền thời gian.**

### Nguyễn Thị Bảo Trang — 2A202602580

- Phần việc và file/commit/PR: **Điền commit/PR thật.**
- Quyết định, khó khăn và cách xử lý: **Điền reflection cá nhân.**
- Điều đã học: **Điền reflection cá nhân.**
- AI/công cụ đã dùng và cách kiểm tra: **Điền công cụ và evidence kiểm tra.**
- Thời điểm tự nộp URL repo chung trên VLearn: **Điền thời gian.**

### Nguyễn Hồng Cường — 2A202602415

- Phần việc và file/commit/PR: **Điền commit/PR thật.**
- Quyết định, khó khăn và cách xử lý: **Điền reflection cá nhân.**
- Điều đã học: **Điền reflection cá nhân.**
- AI/công cụ đã dùng và cách kiểm tra: **Điền công cụ và evidence kiểm tra.**
- Thời điểm tự nộp URL repo chung trên VLearn: **Điền thời gian.**

### Đặng Thế Vinh — 2A202602587

- Phần việc và file/commit/PR: **Điền commit/PR thật.**
- Quyết định, khó khăn và cách xử lý: **Điền reflection cá nhân.**
- Điều đã học: **Điền reflection cá nhân.**
- AI/công cụ đã dùng và cách kiểm tra: **Điền công cụ và evidence kiểm tra.**
- Thời điểm tự nộp URL repo chung trên VLearn: **Điền thời gian.**

## Final checkout

- [ ] Điền URL repo, branch, commit chốt và GitHub username.
- [ ] Mỗi thành viên có commit thật và mục INDIVIDUAL đã tự viết.
- [ ] Chạy/commit v3 base, group và adversarial evidence; cập nhật report/version log.
- [ ] Rehearse bốn luồng UI, review tool trace và transcript redact.
- [ ] Xác nhận không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket trong repository.
