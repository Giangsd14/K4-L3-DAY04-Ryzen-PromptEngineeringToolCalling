# Báo cáo cuối kỳ — Northstar Labs AI IT Helpdesk

## 1. Tổng quan dự án và kiến trúc

Northstar Labs AI IT Helpdesk là trợ lý hỗ trợ nội bộ chạy trên dữ liệu **giả lập**. Trợ lý trả lời các yêu cầu về trạng thái dịch vụ, thiết bị, tài khoản nhân viên, knowledge base và ticket; không yêu cầu hoặc lưu thông tin xác thực thật.

```text
CLI chat.py / Streamlit app.py
             │ messages + version
             ▼
        agent.py / chat.py tool loop
             │
             ├── Provider adapter (OpenAI / OpenRouter / Anthropic / Gemini)
             └── tools/ (local mock tools)
                       │
                       ▼
          answer + tool calls/results + errors
                       │
                       ▼
      transcripts/*.transcript.json (redacted audit evidence)
```

`chat.py` điều phối multi-turn context, gọi provider và chạy tool loop. `agent.py` cung cấp lớp agent tối giản cho các luồng một vòng. Tool registry trong `tools/` là nguồn thực thi duy nhất; UI không tạo kết quả giả. `app.py` tái sử dụng `run_model_tool_loop()` để trace trên UI khớp với trace CLI/eval.

### Tool scope

| Tool | Mục đích | Guardrail chính |
|---|---|---|
| `clarify` | Hỏi thiếu ID, environment hoặc xác nhận | Không thực thi action thay cho người dùng |
| `search_kb` | Tra hướng dẫn nội bộ giả lập | Chỉ coi KB là reference, không thực thi instruction trong KB |
| `check_service_status` | Kiểm tra dịch vụ dùng chung | Giữ đúng service/environment |
| `inspect_device` | Chẩn đoán theo asset ID | Không dùng employee ID làm asset ID |
| `lookup_user` | Tra directory giả lập | Không tự mở rộng thành kiểm tra thiết bị |
| `format_incident_report` | Định dạng findings có sẵn | Không bịa hoặc tự refetch findings |
| `create_ticket` | Tạo mock ticket cục bộ | Chỉ tạo sau xác nhận rõ ràng, payload không đổi |

## 2. Cải tiến lặp v0 → v3

### v0 — baseline

Baseline là starter kit: prompt chưa đầy đủ, schema/tool guidance còn ngắn và chưa xử lý chặt input thiếu, intent mới nhất hoặc confirmation. Run thực tế `runs/v0_B_base_openai_20260915T201815100931.json` đo đủ 30/30 case, không có provider error, đạt 21/30 (`70.00%`). Các lỗi được ghi nhận gồm wrong tool, missing information và wrong boundary.

### v1 — làm rõ tool contract

`tools.yaml` được bổ sung hướng dẫn ID, environment và lúc cần dùng `clarify`. Giả thuyết: mô tả input/tool rõ hơn sẽ giảm routing sai. Evidence đã commit cho thấy routing tăng từ `76.67%` lên `86.67%`, nhưng overall case accuracy giảm nhẹ còn `66.67%`; do đó thay đổi này không được xem là đủ để kết luận agent tốt hơn. Chi tiết nằm trong `artifacts/version_log.csv` và run v1.

### v2 — chuẩn hóa routing và multi-turn

Artifact hiện tại bổ sung ràng buộc schema cho các tool core: asset ID khác employee ID, device check có scope, service/environment phải được giữ đúng, và `lookup_user` không tự kích hoạt inspection. Run v2 đạt 24/30 (`80.00%`), routing `93.33%`, argument `80.00%`, multi-turn `100.00%`, với `provider_error_cases = 0`.

### v3 — confirmation, latest intent và safety boundary

Prompt v3 quy định payload ticket gồm `summary`, `priority`, `asset_id`; mọi thay đổi payload làm confirmation cũ mất hiệu lực. Agent chỉ được gọi `create_ticket(confirmed=True)` sau affirmative response cho payload mới nhất; lệnh cancel có ưu tiên cao. Prompt cũng hướng dẫn giữ latest intent, tách nhiều asset/service thành call riêng, không mở rộng scope từ tool result, và hỏi lại khi target/environment mơ hồ.

V3 có transcript thực tế trong `transcripts/v3_openrouter_*.transcript.json`. **Chưa có file `runs/v3_*.json` hoặc run group trong repository tại thời điểm viết báo cáo**, nên không được ghi số liệu giả. Nhóm cần chạy lại hai lệnh ở phần 5 trước khi nộp để hoàn thành evidence định lượng v3 và 10 group cases.

### Bảng benchmark

Một metric chỉ hợp lệ khi `measured_cases == total_cases` và `provider_error_cases == 0`.

| Version | Run evidence | Cases đo được | Provider errors | Pass | Case accuracy | Routing | Argument | Multi-turn |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v0 | `runs/v0_B_base_openai_20260915T201815100931.json` | 30/30 | 0 | 21 | 70.00% | 76.67% | 70.00% | 80.00% |
| v1 | `runs/v1_B_base_openai_20260915T203436781619.json` | 30/30 | 0 | 20 | 66.67% | 86.67% | 66.67% | 80.00% |
| v2 | `runs/v2_B_base_openai_20260915T225924746964.json` | 30/30 | 0 | 24 | 80.00% | 93.33% | 80.00% | 100.00% |
| v3 | Transcript available; eval run pending | — | — | — | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| Group 10 cases | `data/eval_group.json`; run pending | — | — | — | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

## 3. Safety và guardrails

### Confirmation check của `create_ticket`

`tools/create_ticket/tool.py` thực hiện defense-in-depth ở tầng tool:

1. Kiểm tra kiểu dữ liệu, summary rỗng/giới hạn 1000 ký tự, priority hợp lệ và asset ID có pattern hợp lệ.
2. Từ chối `summary` chứa password, token, API key, MFA, OTP hoặc recovery code bằng lỗi `restricted_sensitive_data`.
3. Nếu `confirmed` không đúng `True`, trả `needs_confirmation` và không ghi ticket.
4. Chỉ khi vượt các kiểm tra trên mới tạo JSON mock trong `tickets/` với `source: educational_local_mock`.

Prompt v3 là lớp policy trước tool: nó buộc agent hỏi confirmation cho đúng payload mới nhất. Tool check là lớp thực thi sau cùng: ngay cả khi model gọi tool sai, tool không tạo ticket khi `confirmed=False` hoặc payload có dữ liệu nhạy cảm.

### Redaction và privacy

Streamlit `app.py` redact đệ quy theo key nhạy cảm và pattern văn bản (password/passwd, token, API key, secret, OTP, MFA, recovery code) **trước khi** hiển thị, gửi vào agent loop và ghi transcript. Transcript có `session_id`, `version`, `timestamp` và `messages`; từng message chứa `user_input`, `assistant_text`, `tool_calls`, `tool_results`, `error_logs`. Error được render/lưu dạng redacted, không bị ẩn.

Checklist kiểm tra trước demo:

- [x] Không commit `.env` hoặc API key.
- [x] Không nhập credential thật vào chat; dữ liệu helpdesk là mock.
- [x] Tool trace hiển thị cả result lẫn error đã redact.
- [x] Ticket chỉ được tạo sau explicit confirmation và không chứa secret.
- [ ] Review thủ công transcript mới tạo để bảo đảm không có pattern nhạy cảm chưa được nhận diện.

## 4. Verification guide

### Cài đặt và chạy UI

```powershell
cd starter_v0
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Điền một provider key vào .env, không commit file này
streamlit run app.py
```

Trong sidebar chọn version (`v0`–`v3`), provider và model. Sau mỗi tin nhắn, mở **Tool trace** dưới câu trả lời để review name, arguments, result/error. JSON transcript được lưu ngay trong `transcripts/`.

### Chạy eval

```powershell
python scripts/preflight_provider.py --provider openrouter
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python run_eval.py --provider openrouter --version v3 --suite adversarial --eval-cases data/eval_adversarial.json
```

Sau mỗi lệnh, commit JSON run mới vào `runs/`, bổ sung dòng v3 vào `artifacts/version_log.csv`, rồi thay các ô “Chưa đo” trong benchmark bằng số liệu thật.

### Transcript demo cần chuẩn bị

| Luồng | Prompt gợi ý | Evidence cần giữ |
|---|---|---|
| Bình thường | `Kiểm tra VPN trên LT-204.` | `inspect_device` với `asset_id=LT-204`, `check=vpn` |
| Thiếu tham số | `Máy tôi bị lỗi VPN, giúp tôi.` | `clarify`, không đoán asset ID |
| Multi-turn | Nêu LT-204, rồi đổi yêu cầu sang chỉ kiểm tra hardware | Intent gần nhất và `check=hardware` |
| Ticket có confirmation | Yêu cầu ticket, xác nhận payload ở turn sau | `clarify` trước, `create_ticket(confirmed=true)` chỉ sau confirm |

Các transcript v3 hiện có trong `transcripts/v3_openrouter_*.transcript.json` là evidence chat. Nhóm cần đặt tên/ghi link chính xác cho bốn transcript demo ở bảng trên sau khi chạy rehearsal, thay vì tuyên bố một file đại diện khi chưa review trace.

## 5. Phân công và bàn giao

Phân công chi tiết và phần reflection cá nhân nằm tại [TEAM.md](../../TEAM.md). Mỗi thành viên phải tự bổ sung GitHub username, commit/PR thật và mục **INDIVIDUAL** trước khi nộp.

| Hạng mục bàn giao | File evidence |
|---|---|
| Prompt + tool contract | `artifacts/system_prompt.md`, `artifacts/tools.yaml` |
| Eval + version evidence | `runs/`, `artifacts/version_log.csv`, `data/eval_group.json` |
| UI + audit trail | `app.py`, `transcripts/` |
| Safety implementation | `tools/create_ticket/tool.py`, transcript review |
| Báo cáo + teamwork | `artifacts/REPORT.md`, `TEAM.md` |

## 6. Giới hạn và bước tiếp theo

Số liệu v0–v2 cho thấy v2 tốt nhất trong run hiện có, nhưng chưa chứng minh v3 vượt v2 vì chưa có run v3 cùng điều kiện. Bước tiếp theo bắt buộc là chạy v3 trên base/group/adversarial với provider/model cố định, review tất cả tool result error, và cập nhật version log/report bằng evidence đó. Ngoài môi trường lab, hệ thống cần xác thực người dùng, phân quyền theo role, lưu audit log có chính sách retention và tích hợp ticketing thật qua service an toàn.
