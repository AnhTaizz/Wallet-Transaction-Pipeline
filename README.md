# Wallet Transaction Pipeline

Dự án thực hành công việc của Junior Data Engineer trên dữ liệu ví điện tử giả lập. Bạn bắt đầu bằng cách **tự dùng Spoon đọc 5 giao dịch từ PostgreSQL và ghi lên HDFS**. Qua [10 bài thực hành](docs/ROADMAP.md), bạn xây pipeline đối soát, vận hành bằng Bash, Rundeck và Airflow, rồi xử lý một ticket lệch doanh số.

| Phần | Trạng thái |
| --- | --- |
| Lab PostgreSQL → Spoon → HDFS | Có Compose cho PostgreSQL mẫu và HDFS một NameNode, một DataNode. Người học tạo transformation trong Spoon trên máy. |
| Lab CSV 12 dòng | Có sẵn Docker Compose, dữ liệu, khung PySpark và lệnh kiểm tra. Ba truy vấn SQL là bài tập để tự hoàn thành. |
| Capstone đối soát | Có [nguồn PostgreSQL gồm 60.311 lượt giao sự kiện, lịch sử merchant và sao kê đối tác](data/capstone/README.md), kèm số liệu chuẩn để tự kiểm tra. |
| Bash, Rundeck và Airflow | Bài 3, 7 và 8 hướng dẫn thiết kế script, job vận hành và DAG. Người học triển khai các phần này. |
| Pipeline báo cáo | Đã lên kế hoạch dùng snapshot HDFS làm đầu vào cho Spark SQL, sau đó điều phối theo ngày bằng Airflow. |
| Mở rộng | PaySim để đo hiệu năng Spark; bảng cảnh báo fraud để thử và đánh giá quy tắc. |

**Ca demo MVP.** Giao dịch TX004 trị giá 70.000đ phát sinh ngày 1 và chuyển từ PENDING sang SUCCESS ngày 2. Lô ngày 2 phải cập nhật báo cáo **ngày 1**. Chạy lại lô ngày 2 vẫn chỉ tính TX004 một lần. Ca này dùng dữ liệu PostgreSQL riêng; fixture CSV hiện tại chứa hai trạng thái của TX004 trong cùng ngày.

- [Thực hành PostgreSQL → Spoon → HDFS](docs/INGESTION_LAB.md) — cách chạy DB mẫu, cấu hình kết nối và đối chiếu file trên HDFS.
- [Lộ trình học](docs/ROADMAP.md) — thứ tự làm, việc tự thực hành và tiêu chí đạt.
- [Kiến trúc và hợp đồng dữ liệu](docs/ARCHITECTURE.md) — vai trò từng bước, hai mốc thời gian và cách chạy lại.
- [Hướng dẫn lab Spark SQL](HUONG_DAN.md), [hồ sơ học tập](TIEN_DO.md) và [phạm vi đã kiểm chứng](KIEM_CHUNG.md).

## Bắt đầu với Spoon

Mở Docker Desktop rồi chạy `docker compose --profile ingest up -d --wait postgres datanode` để khởi động nguồn mẫu và HDFS. Cài hoặc mở Spoon trên Windows, rồi làm theo [hướng dẫn thực hành](docs/INGESTION_LAB.md).

## Bắt đầu với lab Spark SQL

1. Clone repo hoặc tải ZIP từ GitHub, rồi mở terminal tại thư mục có `compose.yaml`.
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

Dùng bảng này để ôn nhanh các khái niệm cần cho MVP. Nếu đã làm được một bài, chạy lệnh kiểm tra và giải thích kết quả trước khi sang bước kế tiếp.

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

## Tài liệu gốc và kiểm chứng

- [Spark 3.5.0 Quick Start](https://spark.apache.org/docs/3.5.0/quick-start.html)
- [Spark SQL reference](https://spark.apache.org/docs/3.5.0/sql-ref.html)
- [Nguồn Docker image Spark/Python](https://github.com/apache/spark-docker/tree/master/3.5.0/scala2.12-java11-python3-ubuntu)
- Xem [KIEM_CHUNG.md](KIEM_CHUNG.md) để biết chính xác phần nào đã được chạy thử.
