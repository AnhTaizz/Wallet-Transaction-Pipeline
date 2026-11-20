# Phạm vi đã kiểm chứng

## Lab PostgreSQL → Spoon → HDFS

Ngày 19/11/2026, đã chạy PostgreSQL 18 bằng Docker Desktop và kết nối từ Windows qua `127.0.0.1:15432`. Bảng mẫu có 5 dòng. Truy vấn theo `updated_at` cho 4 dòng ở lô 1 và 2 dòng ở lô 2 sau khi cập nhật thử TX004. TX005 chỉ thuộc lô 2. Đã rollback giao dịch thử nên TX004 trở lại `PENDING`.

NameNode nhận một DataNode. Hadoop client 3.4.3 chạy trên Windows, đọc cấu hình XML trong `config/spoon`, ghi CSV của 5 dòng PostgreSQL vào HDFS và đọc lại đúng từng byte. Transformation trong Spoon chưa được chạy thử.

## Dữ liệu capstone

Đã chạy [SQL tạo nguồn](sql/capstone/source.sql) trên PostgreSQL lab và đọc hai CSV trong [bộ đối soát](data/capstone/README.md) vào bảng tạm. Truy vấn độc lập xác nhận 60.311 lần giao, 60.308 dòng hợp lệ, 60.007 phiên bản và 30.006 giao dịch. Doanh số M-PILOT ba ngày lần lượt là 170.000, 140.000 và 30.000 VND. Các khoản lệch là +1.000, +90.000 và −5.000 VND. Đây là kết quả đối chiếu nguồn dùng để chấm các bài Spark và vận hành sau này.

## Lab Spark SQL

Ngày: 18/11/2026.

- Đã chạy thật `src/lab.py preview` bằng PySpark/Spark 3.5.0 và đọc đủ 12 dòng CSV.
- Đã chạy một bộ SQL tham chiếu trong bản sao riêng để kiểm tra cả ba bài SQL; tất cả đạt giá trị/kiểu dữ liệu kỳ vọng.
- Đã kiểm tra ghi theo ngày, chạy lại cùng ngày, giữ nguyên ngày khác và giữ file cũ khi lỗi giả lập trước bước thay file.
- Đã kiểm tra ngày sai định dạng/ngày không có dữ liệu không được xuất kết quả.
- Đã kiểm tra SQL bài tập chưa hoàn thành bị báo chưa đạt.
- Đã kiểm tra cú pháp Python.

Môi trường kiểm tra: Linux, Python 3.12.14, OpenJDK 21.0.13, PySpark/Spark 3.5.0. Đây là môi trường đã quan sát chạy được trong lượt soạn lab; đường cài riêng trong README khuyến nghị Python 3.10/3.11 và Java 11/17. Docker Compose ghim image Spark 3.5.0/Java 11/Python 3, nhưng container chưa được chạy thử vì môi trường soạn lab không có Docker.

SQL tham chiếu dùng khi kiểm chứng không nằm trong gói bài tập. Ba file SQL trong gói vẫn là khung để người học tự viết. Các bộ kiểm tra áp dụng dữ liệu mẫu đã cung cấp, chưa đánh giá khả năng xử lý mọi tình huống ngoài mẫu.
