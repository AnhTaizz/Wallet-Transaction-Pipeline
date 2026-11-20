# Dữ liệu thực hành đối soát ví điện tử

Đây là bộ dữ liệu giả lập cố định. Bạn đóng vai kỹ sư phụ trách báo cáo doanh số và giải thích chênh lệch cho bộ phận vận hành. Ba nguồn có ba đơn vị bản ghi khác nhau.

| Nguồn | Một dòng đại diện cho | Khóa và phạm vi |
| --- | --- | --- |
| PostgreSQL `wallet_course.event_deliveries` | Một lần hệ thống nhận một phiên bản giao dịch | `delivery_id` riêng cho mỗi lần nhận. Một cặp `transaction_id, version` hợp lệ có thể được giao lại. |
| [merchant_history.csv](merchant_history.csv) | Một khoảng hiệu lực của phân hạng merchant | Ghép theo `merchant_id` và `valid_from <= event_ts < valid_to`. Ô trống ở `valid_to` nghĩa là còn hiệu lực. |
| [partner_statement.csv](partner_statement.csv) | Một dòng sao kê của đối tác, số tiền nguyên VND | Sao kê cuối kỳ chỉ bao phủ merchant `M-PILOT`, cho giao dịch phát sinh ngày 1–3/11/2026. Đối tác quyết toán giao dịch thành công. |

## Mở dữ liệu

Chạy từ thư mục gốc trong PowerShell. Script SQL tạo một view xác định từ công thức trong schema riêng, dùng được cả với volume PostgreSQL đã có. Nạp lại cho cùng kết quả.

```powershell
docker compose --profile ingest up -d --wait postgres
Get-Content -Raw -Encoding utf8 sql/capstone/source.sql | docker compose --profile ingest exec -T postgres psql -X -v ON_ERROR_STOP=1 -U wallet -d wallet_lab
docker compose --profile ingest exec -T postgres psql -U wallet -d wallet_lab -c "SELECT * FROM wallet_course.event_deliveries WHERE transaction_id = 'P02' ORDER BY received_at"
```

Trong Spoon dùng kết nối PostgreSQL của bài đầu và chọn view trên cho **Table Input**. Đọc mỗi ngày theo `received_at >= start AND received_at < end`. Phát lại từng ngày theo thứ tự để mô phỏng nguồn đang đến. Với hai CSV, dùng **CSV File Input** hoặc đưa nguyên file lên HDFS bằng HDFS CLI rồi đọc bằng Spark. Dùng hai thư mục raw riêng cho danh mục và sao kê. Nếu làm bài Spark trên máy trước, đọc hai CSV từ thư mục này.

## Quy tắc nghiệp vụ

- `event_ts` là lúc phát sinh giao dịch, `updated_at` là lúc nguồn tạo phiên bản, `received_at` là lúc nhận lần giao đó. Mốc báo cáo dùng giờ Việt Nam. Toàn bộ lần nhận nằm trong khoảng từ 01/11 đến trước 01/12/2026 theo UTC+7.
- Giữ từng lần giao ở raw. Đưa dòng thiếu mã giao dịch, số tiền không dương hoặc trạng thái ngoài `PENDING/SUCCESS/FAILED` vào bảng lỗi kèm lý do. Với dòng hợp lệ, gộp các lần giao cùng phiên bản rồi lấy phiên bản lớn nhất cho mỗi giao dịch. Một số phiên bản cũ đến sau phiên bản mới.
- Doanh số là tổng `amount_vnd` của giao dịch đang `SUCCESS`, nhóm theo ngày phát sinh và phân hạng merchant tại thời điểm phát sinh. Khi một giao dịch đổi trạng thái, ngày phát sinh có thể phải tính lại.
- Đối soát tập giao dịch thành công của merchant và kỳ sao kê với các dòng đối tác theo `merchant_id, transaction_id`. Mỗi mã có đúng một kết luận trong bốn loại: khớp, lệch tiền, chỉ có nội bộ, chỉ có đối tác. Quy ước chênh lệch là nội bộ trừ đối tác, phía thiếu tính bằng 0.

## Mốc tự kiểm tra

Trước khi mở bảng dưới, thử lần theo P02 và P04 bằng tay rồi dự đoán ngày, hạng merchant và doanh số.

| Sau khi xử lý đủ kỳ | Kết quả để đối chiếu |
| --- | --- |
| Raw | 60.311 lần giao, 60.311 mã lần giao khác nhau. |
| Kiểm tra chất lượng | 3 dòng lỗi. 60.308 dòng hợp lệ, trong đó có 301 lần giao lại. Còn 60.007 phiên bản hợp lệ và 30.006 giao dịch ở bảng trạng thái. |
| Doanh số riêng M-PILOT | Ngày 1 là 170.000 VND hạng STANDARD, ngày 2 là 140.000 VND hạng PREMIUM, ngày 3 là 30.000 VND hạng PREMIUM. Trước khi nhận phiên bản 2 của P02, ngày 1 là 100.000 VND. |
| Sao kê | 3 mã khớp. P04 lệch +1.000 VND, P05 chỉ có nội bộ +90.000 VND, P99 chỉ có đối tác −5.000 VND. Tổng chênh +86.000 VND. |

Để luyện tối ưu, đo phân bố theo merchant. M-HOT giữ 24.000 trong 30.000 giao dịch nền. Dùng Spark UI hoặc `explain` để kiểm tra kế hoạch thực thi trước khi kết luận nguyên nhân chậm.
