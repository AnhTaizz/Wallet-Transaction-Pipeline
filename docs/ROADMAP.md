# Lộ trình MVP hai tuần

Mỗi mốc phải có một kết quả có thể chạy hoặc quan sát. Dùng [kiến trúc](ARCHITECTURE.md) để tra hợp đồng giữa các bước và ghi kết quả thực tế trong [TIEN_DO.md](../TIEN_DO.md).

## Tuần 1 — Từ PostgreSQL đến báo cáo ngày

| Ngày | Việc cần làm | Tự kiểm tra trước khi chuyển tiếp |
| --- | --- | --- |
| 1 | Chạy preview của lab CSV, đọc luồng trong `src/lab.py` và hoàn thành truy vấn khảo sát trong `sql/01_profile.sql`. | Giải thích mỗi dòng raw đại diện cho gì và vì sao số dòng có thể lớn hơn số giao dịch. |
| 2 | Dựng PostgreSQL local và seed dữ liệu mẫu. Dùng AI dựng Compose/DDL nếu cần. | Tự `UPDATE` trạng thái TX004 và viết truy vấn theo khoảng `updated_at`. Chứng minh bản cập nhật thuộc lô ngày 2. |
| 3 | Tự cấu hình Pentaho Table Input, truyền hai mốc thời gian và ghi staging cho từng lô. | Preview đúng dòng, đọc được file staging và xác minh một giá trị ngay ranh giới hai lô chỉ xuất hiện một lần khi chạy theo thứ tự. |
| 4 | Dùng dữ liệu staging cập nhật bảng trạng thái giao dịch. Dùng Spark SQL tính ba chỉ số theo ngày phát sinh. | So kết quả của một ngày với phép tính tay. Chỉ ra nơi cập nhật trạng thái và nơi chọn ngày cần tính lại. |
| 5 | Ghép các bước và demo thủ công ca TX004. | Trước cập nhật, TX004 chưa góp vào số tiền thành công. Sau lô ngày 2, ngày 1 tăng đúng 70.000đ và một giao dịch thành công. |

## Tuần 2 — Airflow, xử lý lỗi và bàn giao

| Ngày | Việc cần làm | Tự kiểm tra trước khi chuyển tiếp |
| --- | --- | --- |
| 6 | Viết lệnh chạy từng bước theo khoảng thời gian và kiểm tra exit code. | Lệnh hợp lệ chạy được; đầu vào sai khiến bước thất bại rõ ràng. |
| 7 | Ghép DAG Airflow với các bước đọc, xử lý và xuất. | Sử dụng khoảng của lần chạy để lấy dữ liệu. Xem được khoảng thời gian và đường dẫn staging trong log. |
| 8 | Tạo lỗi sau staging hoặc trước công bố báo cáo. Tập retry từ đầu vào đã lưu. | Bản báo cáo đã công bố vẫn đọc được; sau khi khắc phục, kết quả khớp lần chạy chuẩn. |
| 9 | Thử chạy lại lô ngày 2 và phát lại lô ngày 1 sau khi ngày 2 đã hoàn thành. | TX004 còn SUCCESS, không sinh bản sao và báo cáo ngày 1 không tăng lần thứ hai. Kiểm tra thêm một lô rỗng. |
| 10 | Chạy demo từ môi trường sạch, bổ sung lệnh xác nhận vào README và ghi bằng chứng trong hồ sơ học tập. | Tự lần theo TX004 từ DB đến báo cáo trong khoảng 5 phút và giải thích cách tìm lỗi khi số liệu lệch. |

## Cách học với AI trong repo

1. Chốt đầu vào, kết quả mong đợi và một ca lỗi trước khi yêu cầu sinh code.
2. Giao AI dựng khung từng bước. Tự cấu hình Pentaho, viết ít nhất một truy vấn cốt lõi và chạy lệnh kiểm tra.
3. Đọc diff, theo dấu một giao dịch qua bước vừa làm, rồi tự đổi dữ liệu và dự đoán kết quả.
4. Ghi link commit cùng lệnh hoặc log giúp người khác tái hiện.

## Mở rộng sau MVP

- **PaySim:** lấy một tập con cố định, chạy cùng truy vấn trên CSV và Parquet, so kết quả và thời gian. Tăng dữ liệu nếu máy chạy ổn.
- **Fraud:** thêm một quy tắc cảnh báo có thể giải thích, lưu lý do gắn cờ và dùng nhãn của bộ mô phỏng để đo ca bắt đúng và báo nhầm.
