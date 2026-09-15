# IT Helpdesk Web UI

Giao diện web độc lập cho agent IT Helpdesk. Toàn bộ source UI nằm trong thư mục `ui/`; UI import và sử dụng agent loop, tool registry, provider và cơ chế transcript có sẵn của starter, không sửa prompt, tool, eval hoặc CLI.

## Chạy UI

Từ thư mục `starter_v0/`, sau khi đã cài dependencies gốc và cấu hình `.env` cục bộ:

```powershell
python ui/app.py --provider openrouter --version v3
```

Mở `http://127.0.0.1:5000` trong trình duyệt. Có thể chọn provider khác (`openai`, `anthropic`, `gemini`) hoặc chỉ định model:

```powershell
python ui/app.py --provider openrouter --version v3 --model <model-name>
```

Tùy chọn: `--history-window 5`, `--max-tool-rounds 4`, `--host 127.0.0.1`, `--port 5000`.

Trong sidebar, chọn provider, model và version rồi nhấn **Áp dụng cấu hình**. Model được lọc theo provider. Thao tác này tạo phiên chat mới để không trộn lịch sử giữa model hoặc version. Version thay đổi nhãn/hash artifact hiện có; để chạy đúng nội dung lịch sử v0/v1/v2, nhóm cần lưu snapshot artifact tương ứng.

## Evidence

Mỗi lượt chat dùng agent loop và tool call thật. Transcript JSON được lưu tự động trong `starter_v0/transcripts/`; thư mục này không bị UI xóa khi bạn bấm **Cuộc trò chuyện mới**.

## Kịch bản demo

1. **Yêu cầu bình thường:** hỏi trạng thái một dịch vụ hoặc cách xử lý VPN.
2. **Thiếu thông tin:** báo lỗi thiết bị nhưng chưa nêu asset ID để agent hỏi lại.
3. **Nhiều lượt:** cung cấp thêm dữ liệu, sau đó sửa hoặc hủy yêu cầu ở lượt tiếp theo.
4. **Action có confirmation:** yêu cầu tạo ticket, xem agent thu thập đủ dữ liệu và chỉ thực hiện sau xác nhận rõ ràng.

Không đưa API key, mật khẩu, token, MFA code hoặc dữ liệu thật vào chat/transcript.
