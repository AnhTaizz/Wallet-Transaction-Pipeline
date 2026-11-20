# Thực hành pipeline với PaySim

Bạn sẽ đọc tệp giao dịch ví điện tử giả lập từ Kaggle, kiểm tra dữ liệu, tạo báo cáo theo loại giao dịch và phát lại một lô. Cuối bài, bạn tự đo cùng một truy vấn trên CSV và Parquet. Mỗi mục là một buổi khoảng 30 phút. Việc quét cả tệp hoặc dựng môi trường có thể cần thêm thời gian.

## Chuẩn bị

- Đặt tệp `PS_20174392719_1491204439457_log.csv` trong `data/`. Đây là tệp khoảng 494 MB và đã có trong `.gitignore`. [Bộ dữ liệu PaySim trên Kaggle](https://www.kaggle.com/datasets/ealaxi/paysim1)
- Có thể làm buổi Spoon sau bài 1.3 trong [danh sách micro-lesson](MICRO_LESSONS.md). Để bắt đầu phần Spark, dùng service `lab` trong `compose.yaml` và phần [lab Spark SQL](../HUONG_DAN.md) để ôn cách đếm và tổng hợp.

## Hiểu dữ liệu trước khi chạy

Một dòng là một lần giao dịch trong mô phỏng. `step` là giờ mô phỏng. Ngày mô phỏng đầu tiên gồm `step >= 1 AND step < 25`. Dùng số giờ và ngày mô phỏng trong báo cáo. [Mô tả thời gian trong mô hình PaySim](https://ntnuopen.ntnu.no/ntnu-xmlui/bitstream/handle/11250/2584265/2017%20IJSPM%20EDL%20Final%20version.pdf?sequence=2)

| Cột | Cách dùng trong lab |
| --- | --- |
| `step` | Số nguyên dương, dùng để chia lô. |
| `type` | `CASH_IN`, `CASH_OUT`, `DEBIT`, `PAYMENT` hoặc `TRANSFER`. |
| `amount` | Giá trị giao dịch theo đơn vị của nguồn. Dùng số thập phân chính xác khi tính tổng. |
| `nameOrig`, `nameDest` | Mã tài khoản bên gửi và bên nhận. Cùng tài khoản có thể xuất hiện nhiều lần. |
| `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest` | Số dư trước và sau từ nguồn. Giữ nguyên dữ liệu gốc khi đọc lần đầu. |
| `isFraud`, `isFlaggedFraud` | Nhãn gian lận của mô phỏng và cờ cảnh báo có sẵn. Cả hai nhận `0` hoặc `1`. |

PaySim dùng một tập sự kiện cố định. Giữ từng dòng khi nạp và kiểm tra số lượng khi phát lại. Bài đối soát cuối khóa của repo dùng hợp đồng dữ liệu riêng với mã giao dịch, lần cập nhật, lịch sử merchant và sao kê đối tác.

## Buổi 1 Xem CSV trong Spoon

1. Tạo transformation riêng và thêm **CSV file input**. Chọn tệp PaySim, dấu phẩy, dòng đầu là header và mã hóa UTF-8.
2. Dùng **Get fields** để lấy tên cột. Giữ mã tài khoản dạng chuỗi. Dùng **Preview** xem 10 dòng.
3. Lưu `paysim_sample.ktr` và ghi lại tên cột đầu, cột cuối và hai cột nhãn bạn nhìn thấy.

**Đạt khi** Preview có đủ 11 cột và bạn giải thích được một dòng đại diện cho gì. **Gợi ý:** Nếu cả header nằm trong một cột, kiểm tra dấu phân cách.

## Buổi 2 Đọc bằng Spark và kiểm tra kiểu

1. Tự tạo `src/paysim.py`. Đọc CSV bằng schema tường minh theo thứ tự header, giữ cột ở dạng chuỗi ở tầng raw. Trong Spark, dùng đường dẫn `/workspace/data/PS_20174392719_1491204439457_log.csv`.
2. Đổi `step` thành số nguyên, `amount` thành `DECIMAL(20,2)` và hai cột nhãn thành số nguyên. Giữ giá trị raw để giải thích lỗi chuyển kiểu. Tệp có 5.650 giá trị `amount` viết theo ký pháp khoa học và 16 giá trị bằng 0. Kiểm tra cả hai trường hợp khi chuyển kiểu.
3. Tách dòng sai kiểu, thiếu trường bắt buộc, sai loại giao dịch, số tiền âm hoặc nhãn ngoài `0/1`. Đếm dòng raw, dòng hợp lệ và dòng lỗi. Viết hàm kiểm tra riêng cho phạm vi `step = 1` để thử nhanh.

Chạy tệp bạn vừa viết từ PowerShell ở thư mục gốc của repo.

```powershell
docker compose run --rm --entrypoint /opt/spark/bin/spark-submit lab `
  --master 'local[2]' --driver-memory 1g /workspace/src/paysim.py
```

**Đạt khi** `step = 1` có 2.708 dòng, toàn tệp có 6.362.620 dòng và `step` từ 1 đến 743. **Gợi ý:** So từng hàng lỗi với chuỗi `amount` gốc trước khi sửa quy tắc.

## Buổi 3 Ghi Parquet và kiểm tra đầu ra

1. Ghi tập đã kiểm tra kiểu vào `outputs/paysim/transactions.parquet`.
2. Mở lại bằng Spark. So số dòng, kiểu của `amount`, tổng tiền và số lượng theo `type` với CSV.
3. Kiểm tra `step` ở hai đầu và đếm số giá trị tiền bằng 0. Ghi lại các phép kiểm tra đã chạy để dùng cho buổi đo hiệu năng.

**Đạt khi** tổng tiền toàn tệp là `1144392944759.77` theo đơn vị của nguồn và mỗi loại giao dịch giữ nguyên số dòng. [Spark đọc và ghi Parquet](https://spark.apache.org/docs/3.5.6/sql-data-sources-parquet.html)

## Buổi 4 Tổng hợp và đối chiếu nhãn

1. Dùng Spark SQL hoặc DataFrame để nhóm theo `type`. Xuất số giao dịch, tổng `amount` và số dòng `isFraud = 1`.
2. Lập bảng đếm theo hai cột `isFraud` và `isFlaggedFraud`. Tính tỷ lệ phát hiện bằng số dòng cả hai cùng bằng `1` chia cho toàn bộ số dòng `isFraud = 1`.
3. Kiểm tra tổng của từng bảng báo cáo bằng số dòng đầu vào. Ghi một câu giải thích vì sao số dòng được gắn cờ khác số dòng có nhãn gian lận.

| Loại | Số giao dịch | Có nhãn gian lận |
| --- | ---: | ---: |
| `CASH_IN` | 1.399.284 | 0 |
| `CASH_OUT` | 2.237.500 | 4.116 |
| `DEBIT` | 41.432 | 0 |
| `PAYMENT` | 2.151.495 | 0 |
| `TRANSFER` | 532.909 | 4.097 |

**Đạt khi** có 8.213 dòng `isFraud = 1`, gồm 16 dòng được gắn cờ và 8.197 dòng còn lại. Bảng đếm có 6.354.407 dòng cả hai bằng `0` và 0 dòng chỉ có cờ cảnh báo. Đây là phép đối chiếu hai cột có sẵn trên file mô phỏng.

## Buổi 5 Phân lô và chạy lại

1. Thêm hai tham số giờ bắt đầu và kết thúc. Lọc bằng `step >= start AND step < end`. Thử `[1,25)` và `[25,49)`.
2. Ghi kết quả mỗi lô vào một thư mục riêng dưới `outputs/paysim/batches/`. Ghi hai biên, số dòng và đường dẫn vào log. Khi chạy lại, ghi thay thế thư mục của chính lô đó.
3. Chạy lại `[1,25)`. So số dòng, tổng tiền và số nhãn trước và sau. Kiểm tra thư mục và kết quả của lô `[25,49)` còn đọc được với cùng số đếm.

**Đạt khi** lô đầu có 574.255 dòng, 271 nhãn gian lận và tổng tiền `92131865625.65` trước và sau khi chạy lại. **Gợi ý:** Giờ `25` thuộc đúng lô bắt đầu từ `25`.

## Buổi 6 So CSV với Parquet

1. Chọn cùng một truy vấn lọc lô `[1,25)`, nhóm theo `type` và tính `COUNT(*)`, `SUM(amount)`. Áp dụng cùng quy tắc chuyển kiểu và lọc dữ liệu trên hai đầu vào.
2. Giữ cấu hình Spark và phạm vi dữ liệu giống nhau. Đo thời gian cho phần thực thi lấy kết quả tổng hợp, chạy mỗi loại ba lần và ghi trung vị. Ghi rõ lần nào dùng cache.
3. So kích thước lưu trên đĩa, số file và `explain("formatted")`. Nêu phần đọc cột hoặc lọc có thay đổi trong kế hoạch thực thi. Đối chiếu số dòng và tổng tiền trước khi đưa ra nhận xét về thời gian.

**Đạt khi** hai kết quả nghiệp vụ trùng nhau và nhận xét hiệu năng có kèm số đo. Một bảng so sánh theo lượt chạy là đủ để bàn giao.

## Tự kiểm tra và ghi tiến độ

Giải thích vì sao chạy lại khoảng `[1,25)` giữ nguyên kết quả của lô này, rồi dùng một số đếm và một tổng tiền bạn vừa đo để chứng minh. Ghi buổi PaySim, dự đoán, kết quả chạy, tệp đầu ra và mức hỗ trợ vào [nhật ký](../TIEN_DO.md).

Các mốc số liệu trong bài được đếm trực tiếp từ CSV có tên ở trên bằng trình đọc CSV của Python và số thập phân chính xác. Truy vấn Spark, đầu ra Parquet và số đo thời gian là sản phẩm bạn tự tạo khi thực hành.
