BOT TELEGRAM TỰ ĐẶT ĐƠN 80 VIEW - BẢN KHUNG

CẦN CẤU HÌNH TRƯỚC KHI CHẠY
1. Tạo bot bằng @BotFather, lấy token.
2. Thêm bot làm quản trị viên của kênh và cấp quyền xem bài đăng.
3. Trong Railway, tạo các Variables từ .env.example.
4. Đổi API key đã lộ trước đó trước khi dùng; không gửi key mới vào chat.
5. MUALIKE_SERVICE_ID đã đặt mặc định là 3284 theo thông tin bạn cung cấp; hãy xác nhận đây đúng là dịch vụ view Telegram trong action=services.
6. Đặt ADMIN_CHAT_ID là ID chat Telegram muốn nhận thông báo. Bot cần có thể nhắn tin cho chat đó.
7. Deploy bot.py như worker.

LƯU Ý
- Mã này lấy link của chính bài đăng mới trong kênh (không trích link nằm trong nội dung).
- Nếu bạn muốn lấy link được đính kèm bên trong nội dung tin nhắn thay vì link bài đăng,
  cần chỉnh logic target_link.
- API endpoint và định dạng phản hồi dựa trên ảnh tài liệu bạn gửi; hãy xác nhận URL HTTPS
  và phản hồi thực tế trước khi bật chạy đơn tự động.
- Chưa đặt MUALIKE_SERVICE_ID thì bot không gửi đơn.
- Chỉ dùng với nội dung/kênh bạn quản lý và dịch vụ được website cho phép.
