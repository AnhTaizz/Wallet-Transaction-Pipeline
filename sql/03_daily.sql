-- Bài 3: tổng hợp transactions_clean theo ngày event_ts.
-- Khung dưới đây mô tả đầu ra và cố tình trả về 0 dòng.
-- total_transactions gồm mọi trạng thái hợp lệ sau làm sạch.
-- successful_transactions / successful_amount_vnd chỉ tính trạng thái SUCCESS.
SELECT
  CAST(NULL AS DATE) AS business_date,
  CAST(NULL AS BIGINT) AS total_transactions,
  CAST(NULL AS BIGINT) AS successful_transactions,
  CAST(NULL AS BIGINT) AS successful_amount_vnd
FROM transactions_clean
WHERE FALSE
