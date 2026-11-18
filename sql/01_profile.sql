-- Bài 1: thay các giá trị NULL bằng phép đếm phù hợp.
-- Đầu ra: đúng một dòng, ba cột như dưới đây.
-- Đếm trạng thái SUCCESS ở đây là đếm bản ghi nguồn, chưa phải giao dịch cuối cùng.
SELECT
  CAST(NULL AS BIGINT) AS raw_rows,
  CAST(NULL AS BIGINT) AS distinct_transaction_ids,
  CAST(NULL AS BIGINT) AS success_event_rows
FROM transactions_raw
LIMIT 1
