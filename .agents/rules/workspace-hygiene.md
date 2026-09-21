# Workspace Hygiene & Temporary Files

## Quy tắc quản lý file tạm thời (tmp/)

- **Nguyên tắc cốt lõi:** Tuyệt đối không tạo các script, file dữ liệu test, file tải về tạm thời hoặc output chạy thử ở thư mục gốc hoặc trong các thư mục mã nguồn chính (`/backend`, `/frontend`, `/vto-service`, `/supabase`).
- **Thư mục lưu trữ:** Mọi file/script/data/item tạm thời, dùng 1 lần, không tái sử dụng và không ảnh hưởng đến các service/pipeline chính **BẮT BUỘC** phải được tạo/lưu trong thư mục `tmp/`.
- **Git ignore:** Thư mục `tmp/` đã được ignore trong `.gitignore` để đảm bảo sạch sẽ cho workspace và commit history.
