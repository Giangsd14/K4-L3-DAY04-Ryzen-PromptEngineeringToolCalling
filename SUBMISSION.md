# Nộp bài Day04

**Làm nhóm. Mỗi thành viên tự nộp cùng URL repo nhóm trên VLearn.**

## Tên repo

```text
K4-L3-DAY04-Ryzen-PromptEngineeringToolCalling
```

Dùng họ tên không dấu và MSSV của người đại diện; không có khoảng trắng; dùng `DAY04` và `L3`. Liệt kê mọi thành viên trong [TEAM.md](TEAM.md).

Khi repo đề bài public và cho phép Fork, nhóm trưởng Fork rồi đổi tên. Nếu chưa Fork được, clone repo đề bài, đổi `origin` sang repo nhóm rỗng và push `main`:

```powershell
git clone https://github.com/VinUni-AI20k/K4-L3B-Day04-Prompt-Engineering-Tool-Calling-Labs.git <TEN_REPO_NHOM>
cd <TEN_REPO_NHOM>
git remote rename origin upstream
git remote add origin <URL_REPO_NHOM>
git push -u origin main
```

## Bản nộp hoàn chỉnh

- `README.md`, `TEAM.md` và `starter_v0/artifacts/REPORT.md`.
- Prompt, `tools.yaml`, `version_log.csv`, run base v0–v3, run group và adversarial.
- Giữ các bộ IT gốc. Nếu đổi lĩnh vực, nộp bộ riêng 30 câu cơ bản (20 + 10) và 12 câu an toàn, chốt trước v0; ghi đường dẫn/lệnh chạy. Mọi nhóm viết thêm 10 câu mới (5 + 5), theo README.
- UI chạy được theo README, transcript cho yêu cầu bình thường, thiếu thông tin, nhiều lượt và hành động ghi dữ liệu của lĩnh vực đã chọn.
- Commit kỹ thuật của từng thành viên và INDIVIDUAL tự viết trong `TEAM.md`.

Có thể commit `runs/`, `transcripts/` và `analysis/` sau khi kiểm tra nội dung. Không commit `.env`, khóa truy cập, dữ liệu thật, `.venv`, cache hay `tickets/`.

## Hạn và cách nộp

Hạn mặc định: **23:59 ngày làm lab, Asia/Ho_Chi_Minh (UTC+07:00)**. Keycoach có thể thông báo hạn khác trong 48 giờ sau buổi lab; đây không phải gia hạn tự động. `T+155` lúc 20:25 chỉ là mốc kiểm tra tại lớp.

Mỗi thành viên mở đúng bài Day04 trên VLearn, nộp URL trang gốc của repo nhóm và mở lại để kiểm tra URL đã lưu. Ghi commit chốt trong `TEAM.md`. Sửa sau deadline phải tạo commit/branch mới và ghi rõ thời điểm; xem [RULES.md](RULES.md).

## Kiểm tra trước khi nộp

- [ ] Tên repo, TEAM và INDIVIDUAL đúng quy tắc.
- [ ] Có đủ run, report, UI/transcript và 10 case nhóm.
- [ ] Không sửa bộ câu cố định, không có key hoặc dữ liệu thật.
- [ ] Repo mở được cho người chấm và từng thành viên đã nộp cùng URL trên VLearn.
