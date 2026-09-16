# TEAM — Day04, K4-L3B

**Làm nhóm.** Mỗi người tự viết và commit phần INDIVIDUAL của mình.

## Thông tin bài nộp

- Tên nhóm: Ryzen
- Người đại diện / MSSV: Nguyễn Thanh Giang / 2A202602576
- Tên repo: `K4-L3-DAY04-Ryzen-PromptEngineeringToolCalling`
- URL repo, nhánh nộp, commit chốt: `https://github.com/Giangsd14/K4-L3-DAY04-Ryzen-PromptEngineeringToolCalling` — `main`
- Deadline áp dụng và link thông báo đổi hạn nếu có:

## Thành viên

| Họ và tên | MSSV | GitHub | Vai trò và công việc | File/commit/PR |
|---|---|---|---|---|
| Nguyễn Thanh Giang | 2A202602576 | [Giangsd14](https://github.com/Giangsd14) | Đại diện nhóm; làm rõ contract identifier và thiếu thông tin cho v1; chạy và ghi evidence v1. | `b918532`, `f4c238d`; [`v1 run`](starter_v0/runs/v1_B_base_openai_20260915T203436781619.json); [`version_log.csv`](starter_v0/artifacts/version_log.csv) |
| Nguyễn Tất Đạt | 2A202602578 | [Nguyen Dat/ Gaohonggg](https://github.com/Gaohonggg) | Thiết lập baseline v0, ghi evidence v2; đánh giá v3 trên bộ adversarial và 10 case nhóm; chốt version log. | `73c2c5e`, `833f776`, `8750748`, `c320435`; [`v0 run`](starter_v0/runs/v0_B_base_openai_20260915T201815100931.json), [`v2 run`](starter_v0/runs/v2_B_base_openai_20260915T225924746964.json), [`v3 adversarial`](starter_v0/runs/v3_B_adversarial_openai_20260916T081224410943.json), [`v3 group`](starter_v0/runs/v3_B_group_openai_20260916T081245553232.json) |
| Nguyễn Thị Bảo Trang | 2A202602580 | [ntbtrangforwork-fintech](https://github.com/ntbtrangforwork-fintech) | Xây giao diện demo helpdesk độc lập. | `1ca56fd` (`feat(ui): add standalone helpdesk demo interface`) |
| Nguyễn Hồng Cường | 2A202602415 | [hongcuong26-debug](https://github.com/hongcuong26-debug) | Ràng buộc xác nhận tạo ticket với payload hiện hành cho v2. | `ab4335f`; [`v2 run`](starter_v0/runs/v2_B_base_openai_20260915T225924746964.json); [`version_log.csv`](starter_v0/artifacts/version_log.csv) |
| Đặng Thế Vinh | 2A202602587 | [HinvGnad](https://github.com/HinvGnad) | Hoàn thiện safety gate, routing/scope/context và schema tool cho v3; cập nhật bộ eval nhóm. | `55e53b6`, `60c6f2e`, `b638c29`, `c6d5567`; [`v3 base`](starter_v0/runs/v3_B_base_openai_20260916T081150078420.json); [`version_log.csv`](starter_v0/artifacts/version_log.csv) |
## Nhận xét chung

- Kết quả và bằng chứng: Tất cả 6 run được dùng làm evidence đều hợp lệ theo rubric (`provider_error_cases = 0`, `measured_cases = total_cases`). Base tăng từ v0 `21/30` (70.00%), qua v1 `20/30` (66.67%) và v2 `24/30` (80.00%), đến v3 `30/30` (100.00%). v3 cũng đạt `12/12` ở adversarial và `10/10` ở bộ case nhóm. Evidence: [`version_log.csv`](starter_v0/artifacts/version_log.csv), [`runs/`](starter_v0/runs/).
- Thay đổi hiệu quả nhất: Safety gate cùng quy tắc routing, scope, context và schema tool ở v3 đưa đầy đủ các metric của base từ v2 (`case_accuracy` 0.8000; `tool_routing_accuracy` 0.9333; `argument_accuracy` 0.8000; `multiturn_accuracy` 1.0000) lên 1.0000; đồng thời không có lỗi trong 12 case adversarial.
- Giới hạn còn lại: v1 giảm accuracy từ 70.00% xuống 66.67%, cho thấy việc chỉ làm rõ mô tả tool chưa đủ. Kết quả 100% chỉ chứng minh trên các bộ 30 base, 12 adversarial và 10 group đã chạy; không thay thế kiểm thử trên dữ liệu thực hay các tình huống ngoài phạm vi. Ngoài ra, GitHub username của Nguyễn Tất Đạt và deadline chưa có evidence đáng tin cậy trong repository.
- Cách phân công và tích hợp: Nhóm dùng baseline v0 làm mốc, sau đó tách các vòng cải tiến v1 (tool contract), v2 (xác nhận payload) và v3 (safety/routing) trong `version_log.csv`. Các run tương ứng được lưu tại [`starter_v0/runs/`](starter_v0/runs/); v3 được kiểm tra thêm bằng adversarial và 10 case nhóm trước khi chốt log. UI được tích hợp qua commit `1ca56fd`.

## INDIVIDUAL

Mỗi thành viên sao chép mẫu bên dưới và tự viết, tự commit phần của mình.

### Nguyễn Tất Đạt — 2A202602578

- Phần việc và file/commit/PR: Thiết lập baseline và workflow đánh giá v0 (`73c2c5e`); ghi evidence run v2 (`833f776`); hoàn thiện routing/xác nhận ticket để chạy v3 base, adversarial và group (`8750748`); chốt [`version_log.csv`](starter_v0/artifacts/version_log.csv) (`c320435`) và tổng hợp phần chung TEAM (`b083b58`). Evidence run: [`v0 base`](starter_v0/runs/v0_B_base_openai_20260915T201815100931.json), [`v2 base`](starter_v0/runs/v2_B_base_openai_20260915T225924746964.json), [`v3 adversarial`](starter_v0/runs/v3_B_adversarial_openai_20260916T081224410943.json), [`v3 group`](starter_v0/runs/v3_B_group_openai_20260916T081245553232.json).
- Quyết định, khó khăn và cách xử lý: Dùng v0 làm baseline thay vì chỉ mô tả lỗi; sau khi v1 giảm `case_accuracy` từ 0.7000 xuống 0.6667, tiếp tục ghi nhận kết quả đúng thực tế. Ưu tiên bind confirmation với payload hiện hành ở v2, sau đó kiểm tra v3 bằng cả base, adversarial và group; v3 đạt lần lượt `30/30`, `12/12` và `10/10` với `provider_error_cases = 0`.
- Điều đã học: Metric tốt chỉ đáng tin khi có run, số case đo bằng tổng case và provider không lỗi; với action tool như `create_ticket`, phải kiểm tra thêm `actual_tool_calls`, `tool_results` và ticket sinh ra, không chỉ nhìn PASS/FAIL.
- AI/công cụ đã dùng và cách kiểm tra: Codex hỗ trợ tổng hợp evidence và soạn tài liệu; Git dùng để đối chiếu commit; đọc summary, actual tool calls và tool results trong các run JSON. Các số liệu đã kiểm tra lại với [`version_log.csv`](starter_v0/artifacts/version_log.csv) và 6 file trong [`runs/`](starter_v0/runs/).

### Đặng Thế Vinh - 2A202602587

- Phần việc và file/commit/PR:
  Tôi phụ trách bổ sung quy tắc v3 trong starter_v0/artifacts/system_prompt.md và xây dựng 10 test case trong starter_v0/data/eval_group.json, gồm 5 case một lượt và 5 case nhiều lượt. Phần v3 tập trung vào gọi đủ công cụ cho nhiều nguồn, chọn đúng phạm vi kiểm tra và xử lý thông tin sửa/hủy. Các thay đổi được ghi nhận trong commit c6d5567.
- Quyết định, khó khăn và cách xử lý:
  Khó khăn chính là hướng dẫn agent gọi đủ công cụ nhưng không gọi thừa. Tôi bổ sung quy tắc tách call theo từng thiết bị, môi trường và chỉ thực hiện những việc người dùng yêu cầu, đồng thời giữ nguyên nội dung v1/v2. Với bộ test, tôi tập trung vào ý định mơ hồ, đính chính mã máy, thay đổi quyết định, hủy hành động và xác nhận tạo ticket; mỗi case có kỳ vọng rõ để dễ đối chiếu.
- Điều đã học:
  Tôi hiểu rằng agent không chỉ cần chọn đúng tên công cụ mà còn phải điền đúng tham số và nhớ thông tin còn hiệu lực trong hội thoại. Tôi cũng học được cách phân biệt thiếu thông tin với chưa rõ ý định, và hiểu rằng bộ test cần giữ cố định để so sánh các phiên bản. JSON hợp lệ hay gọi đúng tool chưa đủ chứng minh hành động thực hiện thành công.
- AI/công cụ đã dùng và cách kiểm tra:
  Tôi dùng Codex hỗ trợ đề xuất tình huống, chuyển thành JSON và bổ sung prompt. Tôi xác định yêu cầu v3, các nhóm tình huống cần bao phủ và yêu cầu giữ nguyên v1/v2, sau đó nhờ AI rà soát cấu trúc 5+5, kỳ vọng và diff. Tôi dùng Git để lưu thay đổi; không coi kiểm tra cấu trúc hoặc nhận xét của AI là kết quả chạy thực tế.

### Nguyễn Hồng Cường — 2A202602415

- **Phần việc và file/commit/PR:** Phụ trách phát triển Version 2 (v2), xây dựng cơ chế xác nhận (Confirmation) gắn chặt với Ticket Payload và xử lý ranh giới an toàn (`ab4335f`). Chỉnh sửa [`system_prompt.md`](starter_v0/artifacts/system_prompt.md), chốt dữ liệu [`version_log.csv`](starter_v0/artifacts/version_log.csv) và ghi nhận evidence run v2 trong thư mục [`runs/`](starter_v0/runs/). Evidence run: [`v2 base`](starter_v0/runs/v2_B_base_openai_20260915T225924746964.json).
- **Quyết định, khó khăn và cách xử lý:** Ép Agent chỉ gọi `clarify(response_type="yes_no")` khi chưa có xác nhận rõ ràng và tự động vô hiệu hóa xác nhận cũ khi payload (`summary`, `priority`, `asset_id`) thay đổi. Khắc phục lỗi v1 bị vi phạm ranh giới (gọi `create_ticket` trước xác nhận ở H12, M05, M09) bằng cách đặt ưu tiên cho lệnh Hủy (Cancellation precedence) và coi input của user là untrusted data.
- **Điều đã học:** Cơ chế quản lý trạng thái (State Transition) và thiết lập Safety Boundary trong Prompt Engineering; đọc các log JSON trong `runs/` để phân tích lỗi Tool Call (`wrong_boundary`, `extra_tool_call`) và thành thạo quy trình Empirical Iteration.
- **AI/công cụ đã dùng và cách kiểm tra:** Gemini AI hỗ trợ phân tích log lỗi và soạn thảo quy tắc prompt; VS Code, Git CLI và Python (`run_eval.py`) dùng để thực thi kiểm thử. Kiểm tra đối chiếu trực tiếp kết quả pass các case mục tiêu (H12, M05, M09, M07) trên bộ [`eval_base.json`](starter_v0/data/eval_base.json).

### Nguyễn Thị Bảo Trang — 2A202602580

- Phần việc và file/commit/PR: Tôi xây dựng giao diện web demo độc lập cho IT Helpdesk trong [`starter_v0/ui/`](starter_v0/ui/): backend `app.py`, giao diện chat (`static/index.html`, `static/styles.css`, `static/app.js`) và hướng dẫn chạy trong [`ui/README.md`](starter_v0/ui/README.md). UI tận dụng agent loop, tool registry, provider và transcript sẵn có, không thay đổi prompt, tool, eval hay CLI. Thay đổi được lưu ở commit `1ca56fd` (`feat(ui): add standalone helpdesk demo interface`).
- Quyết định, khó khăn và cách xử lý: Tôi chọn không tạo một luồng agent riêng cho UI mà import trực tiếp runtime hiện có để demo phản ánh đúng tool call thực. UI tạo phiên mới khi đổi provider/model/version để không trộn lịch sử; khi reset, transcript của phiên cũ vẫn được lưu. Tôi bổ sung tool trace để người dùng xem tool, tham số và kết quả thay vì chỉ tin vào câu trả lời.
- Điều đã học: Giao diện cho agent cần tạo trải nghiệm dùng được nhưng không được che mất bằng chứng thực thi. Việc tách UI khỏi prompt, tool và eval giúp dễ tích hợp, đồng thời giữ nguyên khả năng so sánh các phiên bản agent. Tôi cũng nhận ra phải kết hợp an toàn ở backend (giới hạn request, không lộ chi tiết lỗi provider) với trình bày minh bạch ở frontend.
- AI/công cụ đã dùng và cách kiểm tra: Tôi dùng Codex để hỗ trợ rà soát cấu trúc UI và Git để lưu/đối chiếu thay đổi. Tôi kiểm tra UI theo hướng dẫn trong `ui/README.md`: chạy với provider/version đã chọn, gửi tin nhắn, đổi cấu hình, tạo phiên mới và đối chiếu tool trace cùng transcript JSON được lưu trong `starter_v0/transcripts/`. Không đưa API key, token, mật khẩu hay dữ liệu thực vào chat/transcript.

### Mẫu cho thành viên khác

- Phần việc và file/commit/PR:
- Quyết định, khó khăn và cách xử lý:
- Điều đã học:
- AI/công cụ đã dùng và cách kiểm tra:
- Thời điểm đã tự nộp URL repo chung trên VLearn:
