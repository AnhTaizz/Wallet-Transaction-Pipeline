-- Bài 2: chuẩn hóa kiểu, lọc dữ liệu lỗi, sau đó giữ bản hợp lệ mới nhất.
-- Thứ tự xử lý đã được quy định trong HUONG_DAN.md.
-- Khung dưới đây chỉ mô tả tên/kiểu cột đầu ra và cố tình trả về 0 dòng.
-- Hãy tự viết phần làm sạch và ROW_NUMBER; có thể thay toàn bộ truy vấn này.
SELECT
  CAST(row_id AS INT) AS row_id,
  transaction_id,
  customer_id,
  CAST(amount_vnd AS BIGINT) AS amount_vnd,
  status,
  try_to_timestamp(event_ts, 'yyyy-MM-dd HH:mm:ss') AS event_ts,
  try_to_timestamp(updated_at, 'yyyy-MM-dd HH:mm:ss') AS updated_at
FROM transactions_raw
WHERE FALSE
