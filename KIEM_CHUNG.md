# Phạm vi đã kiểm chứng

Ngày: 18/11/2026.

- Đã chạy thật `src/lab.py preview` bằng PySpark/Spark 3.5.0 và đọc đủ 12 dòng CSV.
- Đã chạy một bộ SQL tham chiếu trong bản sao riêng để kiểm tra cả ba bài SQL; tất cả đạt giá trị/kiểu dữ liệu kỳ vọng.
- Đã kiểm tra ghi theo ngày, chạy lại cùng ngày, giữ nguyên ngày khác và giữ file cũ khi lỗi giả lập trước bước thay file.
- Đã kiểm tra ngày sai định dạng/ngày không có dữ liệu không được xuất kết quả.
- Đã kiểm tra SQL bài tập chưa hoàn thành bị báo chưa đạt.
- Đã kiểm tra cú pháp Python.

Môi trường kiểm tra: Linux, Python 3.12.14, OpenJDK 21.0.13, PySpark/Spark 3.5.0. Đây là môi trường đã quan sát chạy được trong lượt soạn lab; đường cài riêng trong README khuyến nghị Python 3.10/3.11 và Java 11/17. Docker Compose ghim image Spark 3.5.0/Java 11/Python 3, nhưng container chưa được chạy thử vì môi trường soạn lab không có Docker.

SQL tham chiếu dùng khi kiểm chứng không nằm trong gói bài tập. Ba file SQL trong gói vẫn là khung để người học tự viết. Các bộ kiểm tra áp dụng dữ liệu mẫu đã cung cấp, chưa đánh giá khả năng xử lý mọi tình huống ngoài mẫu.
