# Mini project: Làm sạch và đối soát giao dịch bằng Spark SQL

Bài tập cá nhân dùng dữ liệu giả lập, thiết kế để vừa học lý thuyết vừa tự viết SQL.
Mục tiêu đầu tiên: biến 12 bản ghi nguồn thành dữ liệu giao dịch đúng và bảng tổng hợp theo ngày.

Khung đọc dữ liệu, tạo SparkSession và kiểm tra đã có sẵn. Ba file `sql/*.sql` là bài tập còn để trống có chủ ý. Bạn tự hoàn thành từng file; chạy kiểm tra ngay từ bản đầu sẽ báo chưa đạt là bình thường.

## Bắt đầu trong một buổi

1. Giải nén, mở terminal tại thư mục có `compose.yaml`.
2. Mở Docker Desktop/engine và chạy:

```bash
docker compose run --rm lab preview
```

3. Đọc **Bài 1** trong [HUONG_DAN.md](HUONG_DAN.md).
4. Sửa `sql/01_profile.sql`, lưu file, rồi chạy:

```bash
docker compose run --rm lab check 1
```

Nếu kết quả đúng sẽ có `PASS Bài 1`. Nếu chưa đúng, chương trình in kết quả hiện tại và kết quả mẫu để bạn đối chiếu. Không cần làm xong cả project trong một buổi.

Các lệnh trên dùng được trong PowerShell hoặc terminal WSL khi Docker Compose hoạt động. Lần đầu cần tải image. Lab dùng Spark local với 2 luồng, đặt driver memory 1 GiB và giới hạn container 2 GiB; đây là cấu hình lab, không phải số đo mức tiêu thụ thực tế.

Trên Linux/WSL, mặc định container chạy UID/GID 1000. Nếu thư mục không cho ghi, tạo `.env` cạnh `compose.yaml` với `LAB_UID` và `LAB_GID` bằng kết quả `id -u` và `id -g` của bạn.

## Nếu đã có môi trường Spark/PySpark của Tiki

Bạn có thể chạy trực tiếp trong môi trường đó:

```bash
python src/lab.py preview
python src/lab.py check 1
```

Không cần cài lại Spark nếu môi trường hiện tại đã dùng được PySpark. Tùy chọn cài riêng: dùng Python 3.10/3.11 và Java 11/17, tạo virtualenv rồi `python -m pip install -r requirements.txt`. Đường Docker là lựa chọn mặc định của gói này; Java/Python trên máy host không cần cho đường Docker.

## Bốn bài học cố định

| Bài | Lý thuyết chính | Việc tự làm | Kiểm tra |
| --- | --- | --- | --- |
| 1 | Grain, dữ liệu thô, COUNT và NULL | Khảo sát bản ghi nguồn bằng SQL | `check 1` |
| 2 | Chất lượng dữ liệu, kiểu dữ liệu, bản ghi mới nhất | Làm sạch và khử trùng bằng window function | `check 2` |
| 3 | Tổng hợp có điều kiện, quy tắc nghiệp vụ, đối soát | Tính số giao dịch và số tiền thành công theo ngày | `check 3` |
| 4 | Idempotency, chạy theo ngày, lỗi trước bước ghi | Chạy lại, so sánh file, giải thích cơ chế khung có sẵn | `check 4` |

Gợi ý nhịp học: mỗi bài 1–2 buổi, mỗi buổi 45–90 phút nếu bạn đã dùng SQL cơ bản. Tốc độ được điều chỉnh theo bài làm, không theo số buổi cố định.

## Các lệnh tiếp theo

```bash
docker compose run --rm lab check 2
docker compose run --rm lab check 3
docker compose run --rm lab publish --date 2026-11-01
docker compose run --rm lab check 4
```

`publish` chỉ chạy khi bài 2 và 3 đạt kiểm tra trên bộ mẫu. Kết quả nằm trong `outputs/daily/YYYY-MM-DD.json`. Chạy lại cùng ngày thay file của đúng ngày đó. Bản lab đọc lại toàn bộ CSV nhỏ mỗi lần; đây chưa phải cơ chế incremental ingestion, CDC hay hệ thống tài chính thực tế.

## Cách dùng AI để học

Tự dự đoán kết quả, viết SQL, chạy kiểm tra rồi mới nhờ giải thích lỗi. Khi gửi bài, gửi câu SQL, kết quả/lỗi và điều bạn đang hiểu. Nếu vướng, yêu cầu gợi ý từng mức trước khi xem lời giải hoàn chỉnh.

Mẫu gửi: “Tôi đang học mini lab giao dịch, Bài 1. Đây là SQL của tôi: ... Tôi nghĩ kết quả phải là ... nhưng đang nhận ... Hãy chỉ ra chỗ sai và cho một gợi ý trước.”

## Sau bản nhỏ này

Khi làm độc lập bốn bài: dùng Pentaho để đưa CSV/API vào staging, Airflow để gọi pipeline theo ngày, rồi Rundeck để cung cấp thao tác chạy bù. Kubernetes/Flink là phần mở rộng sau; gói hiện tại chỉ chứa Spark SQL và khung kiểm tra.

## Tài liệu gốc và kiểm chứng

- [Spark 3.5.0 Quick Start](https://spark.apache.org/docs/3.5.0/quick-start.html)
- [Spark SQL reference](https://spark.apache.org/docs/3.5.0/sql-ref.html)
- [Nguồn Docker image Spark/Python](https://github.com/apache/spark-docker/tree/master/3.5.0/scala2.12-java11-python3-ubuntu)
- Xem [KIEM_CHUNG.md](KIEM_CHUNG.md) để biết chính xác phần nào đã được chạy thử.
