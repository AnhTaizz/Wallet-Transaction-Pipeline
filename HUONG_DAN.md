# Học từng bài với một ví dụ xuyên suốt

## Quy ước dữ liệu giả lập

`row_id` là số dòng sự kiện nguồn. `transaction_id` là mã giao dịch nghiệp vụ. Một giao dịch có thể xuất hiện nhiều lần do gửi lại hoặc cập nhật trạng thái; vì vậy số dòng nguồn không bằng số giao dịch.

| Cột | Ý nghĩa |
| --- | --- |
| row_id | Khóa bản ghi nguồn; dùng phá hòa khi updated_at bằng nhau |
| transaction_id | Mã giao dịch; khóa nghiệp vụ của bảng sạch |
| customer_id | Mã khách hàng giả lập |
| amount_vnd | Số tiền nguyên, đơn vị VND |
| status | SUCCESS, FAILED hoặc PENDING |
| event_ts | Thời điểm phát sinh giao dịch |
| updated_at | Thời điểm phiên bản trạng thái được cập nhật |

Các timestamp trong CSV là giờ địa phương Việt Nam. Lab đặt Spark session timezone `Asia/Ho_Chi_Minh`. Số tiền là số nguyên; dữ liệu không có phí, tiền tệ khác, hoàn tiền hay sổ cái. Chỉ tiêu ở đây là **số tiền của giao dịch đang ở trạng thái SUCCESS**, không gọi là doanh thu hoặc số dư ví.

## Bài 1 — Khảo sát dữ liệu nguồn

**Mục tiêu:** phân biệt bản ghi nguồn với giao dịch, rồi viết được ba phép đếm.

### 1.1. Grain: mỗi dòng đại diện cho điều gì?

Grain là mức chi tiết của một dòng dữ liệu. Ở bảng `transactions_raw`, mỗi dòng là một bản ghi nhận được, có thể là bản gửi lại hoặc một phiên bản trạng thái. Ở bảng sạch, mỗi dòng sẽ là trạng thái hợp lệ mới nhất của một giao dịch.

Ví dụ: `TX004` có hai dòng PENDING và SUCCESS. Đếm hai dòng là đúng nếu hỏi “đã nhận bao nhiêu bản ghi?”, nhưng sai nếu hỏi “có bao nhiêu giao dịch TX004?”.

Chạy `preview`, nhìn riêng TX002 và TX004. Tự diễn giải khác biệt giữa gửi trùng và cập nhật trạng thái.

### 1.2. COUNT và NULL

`COUNT(*)` đếm dòng. `COUNT(cột)` đếm giá trị không NULL. `COUNT(DISTINCT cột)` đếm giá trị khác nhau, bỏ qua NULL. Trong bài này, transaction_id trống của CSV được đọc thành NULL.

Ví dụ khác bộ mẫu: cột có A, A, B, NULL thì ba phép đếm trên lần lượt là 4, 3 và 2. Đếm có điều kiện có thể dùng `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`.

### 1.3. Thực hành

Sửa `sql/01_profile.sql` để trả đúng một dòng gồm `raw_rows`, `distinct_transaction_ids`, `success_event_rows`. Ở bài 1 chưa lọc lỗi hoặc khử trùng. Sau đó chạy `check 1`.

**Checkpoint cuối bài:** giải thích vì sao số dòng, số mã giao dịch khác nhau và số bản ghi SUCCESS không phải cùng một chỉ tiêu. Gửi SQL và cách bạn hiểu để nhận phản hồi; PASS trên bộ mẫu chưa chứng minh đã vận dụng được tình huống mới.

## Bài 2 — Làm sạch và chọn phiên bản mới nhất

**Mục tiêu:** tạo `transactions_clean`, mỗi transaction_id đúng một dòng.

### 2.1. Kiểu dữ liệu và quy tắc hợp lệ

Ở raw, các trường ngoài row_id được giữ dạng chuỗi. Chuyển `amount_vnd` sang BIGINT; chuyển hai cột thời gian sang TIMESTAMP theo mẫu `yyyy-MM-dd HH:mm:ss`. `try_to_timestamp` trả NULL nếu không phân tích được chuỗi thời gian trong lab.

Quy tắc theo thứ tự cố định:

1. Chuẩn hóa kiểu.
2. Bỏ bản ghi có transaction_id/customer_id NULL hoặc chỉ gồm khoảng trắng; bỏ amount_vnd NULL hoặc <= 0; bỏ trạng thái ngoài SUCCESS/FAILED/PENDING; bỏ timestamp NULL.
3. Trong các bản ghi hợp lệ, giữ phiên bản có updated_at lớn nhất cho mỗi transaction_id. Nếu hòa, giữ row_id lớn nhất.

Đây là quy tắc bài tập đã chốt. Chọn giữ bản hợp lệ mới nhất sau lọc lỗi là một quyết định nghiệp vụ của lab; hệ thống thật cần có chính sách rõ ràng cho bản cập nhật lỗi.

### 2.2. Window function

`ROW_NUMBER()` đánh số trong từng nhóm. Ví dụ ý tưởng cho một bảng minh họa khác:

```sql
ROW_NUMBER() OVER (
  PARTITION BY business_key
  ORDER BY version_time DESC, source_sequence DESC
)
```

CTE (`WITH ... AS (...)`) giúp chia truy vấn thành các bước đọc được. Sau khi đánh số, lọc dòng có thứ tự 1 ở lớp truy vấn ngoài.

### 2.3. Thực hành

Viết `sql/02_clean.sql` theo đúng thứ tự cột/kiểu trong khung và chạy `check 2`. FAILED vẫn là bản ghi hợp lệ; bước làm sạch chưa chỉ lấy SUCCESS. Kiểm tra in cả giá trị lẫn kiểu cột; thứ tự các dòng không ảnh hưởng kết quả.

**Checkpoint cuối bài:** giải thích vì sao bỏ trùng bằng tất cả các cột chưa giải quyết được TX004; thử nghĩ trường hợp hai bản cập nhật có cùng updated_at. Viết một câu SELECT riêng liệt kê bản ghi lỗi và lý do để đối soát bằng mắt.

## Bài 3 — Tính chỉ tiêu theo ngày

**Mục tiêu:** tạo một dòng cho mỗi ngày event_ts trong `transactions_clean`.

### 3.1. Chốt câu hỏi trước khi SUM

Trong lab, một ngày được tính theo DATE của event_ts. `total_transactions` đếm mọi giao dịch sạch của ngày đó. Hai chỉ tiêu còn lại chỉ tính SUCCESS. Không nhóm theo updated_at: thời điểm cập nhật trạng thái và ngày giao dịch trả lời hai câu hỏi khác nhau.

### 3.2. Tổng hợp có điều kiện

Dùng `GROUP BY`, `COUNT`, `SUM(CASE WHEN ...)`; tạo `business_date` kiểu DATE. Tất cả số đếm/số tiền trong đầu ra phải là BIGINT.

### 3.3. Thực hành và đối soát

Viết `sql/03_daily.sql`, chạy `check 3`. Tự cộng số tiền trên các giao dịch SUCCESS sau làm sạch và đối chiếu tổng các ngày. Nếu lệch, quay lại grain và trạng thái trước khi tối ưu query.

**Checkpoint cuối bài:** chỉ ra giao dịch nào làm số tiền bị phóng đại nếu tổng trực tiếp từ raw; thử đổi một ngày giao dịch trong một bản sao dữ liệu và dự đoán chỉ tiêu nào thay đổi. Bộ check cố định chỉ áp dụng CSV mẫu; thay dữ liệu xong cần cập nhật kỳ vọng hoặc phục hồi mẫu.

## Bài 4 — Chạy lại và quan sát lỗi ghi kết quả

**Mục tiêu:** hiểu tính idempotent trên ví dụ file nhỏ và đọc được khung vận hành đã có.

### 4.1. Chạy lại cùng đầu vào

Idempotent trong phạm vi lab nghĩa là chạy lại cùng dữ liệu và ngày xử lý vẫn giữ đúng kết quả đã chốt. Khung Python đọc ngày từ tham số, chọn đúng một dòng tổng hợp và thay file của riêng ngày đó. Bạn đã viết phần logic dữ liệu trong bài 2 và 3; phần ghi file có sẵn để đọc và thử nghiệm.

```bash
docker compose run --rm lab publish --date 2026-11-01
docker compose run --rm lab publish --date 2026-11-02
docker compose run --rm lab publish --date 2026-11-01
docker compose run --rm lab check 4
```

Mở hai file JSON trong `outputs/daily`. Giải thích vì sao không cộng thêm kết quả vào file cũ mỗi lần chạy lại.

### 4.2. Lỗi trước bước thay file

Khung ghi vào file tạm cạnh file đích, đóng file sau khi flush/fsync, rồi gọi `os.replace`. Lệnh sau cố tình lỗi trước bước thay file và sẽ trả mã thoát khác 0:

```bash
docker compose run --rm lab publish --date 2026-11-01 --simulate-failure
```

Đọc file cũ trước/sau, so sánh và xem lỗi. `check 4` tự kiểm tra chạy lại, không ảnh hưởng ngày khác và giữ bản cũ khi lỗi giả lập. Kiểm tra này áp dụng file lab trên filesystem hiện tại; chưa chứng minh exactly-once cho hệ thống phân tán, tính bền vững khi mất điện hoặc xử lý nhiều job ghi đồng thời.

### 4.3. Liên hệ công việc

Sau này Airflow/Rundeck có thể truyền ngày xử lý vào lệnh. Lịch chạy và retry chỉ hữu ích khi logic dữ liệu của job chịu được chạy lại. Trước khi thêm công cụ, hãy thử giải thích cách khung xử lý ngày không có dữ liệu và lỗi SQL.

**Checkpoint cuối bài:** dùng lời của bạn giải thích đường đi raw → clean → daily → file ngày; xác định phần bạn tự viết, phần khung có sẵn; nêu một hạn chế của bản lab.
