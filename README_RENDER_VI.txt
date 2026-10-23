HƯỚNG DẪN CHẠY TRÊN RENDER (ĐIỆN THOẠI ANDROID)

1. Giải nén ZIP.
2. Tạo repository PRIVATE trên GitHub, tải các file trong thư mục telegram_view_bot lên.
   Không tải API key hoặc token thật lên GitHub.
3. Mở https://render.com và đăng nhập bằng GitHub.
4. Cách dễ nhất: Dashboard > New > Blueprint, chọn repository có render.yaml, rồi Apply.
   Nếu không thấy Blueprint, tạo Background Worker thủ công:
   Build Command: pip install -r requirements.txt
   Start Command: python bot.py
5. Trong Environment của service, thêm:
   TELEGRAM_BOT_TOKEN = token từ @BotFather
   MUALIKE_API_KEY = API key mới (hãy đổi key cũ đã lộ)
   MUALIKE_API_URL = https://mualike1s.com/api/v3
   MUALIKE_SERVICE_ID = 3284
   VIEW_QUANTITY = 80
   ADMIN_CHAT_ID = chat ID nhận thông báo (có thể để trống nếu không cần)
6. Save and deploy.
7. Mở Logs, kiểm tra dòng "Bot started". Thêm bot làm quản trị viên kênh và đăng bài thử.
8. Nếu API trả lỗi, tạm dừng bot cho đến khi xác nhận URL, ID dịch vụ và định dạng phản hồi.

LƯU Ý:
- Background Worker phù hợp bot polling vì không cần mở cổng HTTP.
- Giá và khả năng chạy liên tục phụ thuộc gói Render hiện tại.
- ID 3284 do người dùng cung cấp, chưa được xác minh độc lập.
- Bot hiện lấy link của chính bài đăng Telegram, không trích link khác nằm trong nội dung.
- Chỉ dùng với nội dung và dịch vụ bạn được phép sử dụng.
