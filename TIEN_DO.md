# Hồ sơ thực hành

## PostgreSQL → Spoon → HDFS

- Tự tạo transformation trong Spoon, đọc giao dịch từ PostgreSQL và đối chiếu dữ liệu đã ghi trên HDFS.
- Bắt đầu bằng cách chạy PostgreSQL và HDFS lab, tạo `Table Input` rồi preview 5 dòng mẫu. [Hướng dẫn thực hành](docs/INGESTION_LAB.md)
- Ghi lại truy vấn đã dùng, đường dẫn HDFS, số dòng và trạng thái TX004 ở từng lô.

## Lab Spark SQL

- Mục tiêu: tự làm sạch, tổng hợp và đối soát dữ liệu giao dịch giả lập.
- Vị trí bắt đầu: Bài 1 / mục 1.1 trong [HUONG_DAN.md](HUONG_DAN.md).
- Đã chuẩn bị: dữ liệu mẫu, khung chạy và ba file SQL bài tập.
- Đã tự làm được: chưa có bài làm để đánh giá.
- Môi trường trên máy người học: chưa kiểm tra.
- Tiến độ Bài 1–4: chưa bắt đầu, chưa đánh giá.
- Bước tiếp theo: chạy `docker compose run --rm lab preview`, đọc Bài 1 và sửa `sql/01_profile.sql`.

Sau mỗi bài, ghi: SQL đã viết; kết quả; lỗi gặp; giải thích bằng lời; phần cần ôn. Phân biệt làm được có gợi ý với làm độc lập.

## Theo dõi 10 bài thực hành

Ghi mã [micro-lesson](docs/MICRO_LESSONS.md) vào cột đầu, ví dụ `2.3` khi tập gọi job con. Ghi bài tiếp theo ở cột cuối để lần sau học tiếp đúng chỗ.

Xem [lộ trình học](docs/ROADMAP.md) để chọn việc tiếp theo. Ghi một dòng sau mỗi buổi làm:

| Buổi / bài | Dự đoán trước khi chạy | Kết quả và bằng chứng (commit, log hoặc truy vấn) | Lỗi đã tự sửa | Mức tự làm và bước tiếp theo |
| --- | --- | --- | --- | --- |
