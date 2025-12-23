## FastAPI Auth Example

Dự án mẫu FastAPI cho đăng ký, đăng nhập, tạo access token/refresh token với `pyjwt` và hash mật khẩu bằng `pwdlib`.

### Yêu cầu
- Python 3.12+

### Cài đặt
- Tạo môi trường ảo (tuỳ chọn):
  - Windows: `python -m venv .venv && .\.venv\Scripts\activate`
- Cài dependency: `pip install -r requirements.txt`

### Chạy app
- Lệnh phát triển: `uvicorn app.main:app --reload`
- Mặc định chạy ở `http://127.0.0.1:8000` với tài liệu tương tác tại `/docs`.

### Cấu hình qua biến môi trường
- `SECRET_KEY`: khoá ký access token (mặc định: `change-me-access`)
- `REFRESH_SECRET_KEY`: khoá ký refresh token (mặc định: `change-me-refresh`)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: thời gian sống access token, phút (mặc định: `15`)
- `REFRESH_TOKEN_EXPIRE_DAYS`: thời gian sống refresh token, ngày (mặc định: `7`)
- `JWT_ALGORITHM`: thuật toán ký (mặc định: `HS256`)

### Các endpoint chính
- `POST /register`: tạo user mới.
- `POST /token`: đăng nhập, nhận access/refresh token (chuẩn OAuth2 Password Flow).
- `POST /refresh`: đổi refresh token để lấy cặp token mới.
- `POST /logout`: xoá refresh token (session) của user.
- `GET /me`: lấy thông tin user từ access token.

### Cấu hình DB MySQL
- Mặc định `DATABASE_URL=mysql+pymysql://app_user:app_pass@mysql:3306/auth_db` (phù hợp docker-compose).
- Thay đổi qua `.env` nếu cần:
  ```
  DATABASE_URL=mysql+pymysql://user:pass@host:port/dbname
  ```
- Khi chạy lần đầu, app sẽ tự tạo bảng `users` và `sessions` (demo, chưa có migration).
- Bảng `sessions` lưu refresh token theo từng thiết bị (device_id). Mỗi user + device có 1 refresh token; đăng nhập lại cùng device sẽ dùng token cũ, device khác sẽ tạo token mới.

### Thiết bị / session
- Truyền `client_id` trong form OAuth2 (field chuẩn) như một `device_id`.
- `/token`: nếu đã có session cho `user + client_id` sẽ trả refresh token cũ, không sinh mới; nếu `client_id` khác sẽ tạo refresh token mới.
- `/refresh`: kiểm tra refresh token còn thuộc user; cấp access token mới, giữ nguyên refresh token.
- `/logout`: nhận refresh token, xoá session tương ứng (revoke refresh token).

### Gợi ý xử lý đăng xuất (revoke token)
- Access token dạng JWT tự hết hạn: nếu không có blacklist, không thể “thu hồi” ngay lập tức. Có thể thêm danh sách đen (store token ID jti + exp) để từ chối sớm.
- Refresh token nên dùng rotation (mỗi lần refresh cấp token mới và vô hiệu hoá token cũ). Lưu refresh token (hoặc jti) trong DB/cache và đánh dấu revoked khi đăng xuất.

