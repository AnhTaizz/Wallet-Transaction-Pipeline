-- Deterministic event deliveries for the wallet curriculum.
BEGIN;
CREATE SCHEMA IF NOT EXISTS wallet_course;

CREATE OR REPLACE VIEW wallet_course.event_deliveries AS
WITH generated AS (
    SELECT i,
           'BG' || lpad(i::text, 6, '0') AS transaction_id,
           CASE WHEN i % 5 <> 0 THEN 'M-HOT' ELSE 'M-SMALL' END AS merchant_id,
           (1000 * (1 + i % 199))::bigint AS amount_vnd,
           timestamptz '2026-11-01 00:00:00+07' + i * interval '80 seconds' AS event_ts
    FROM generate_series(1, 30000) AS series(i)
), background AS (
    SELECT transaction_id, merchant_id, amount_vnd, event_ts, version,
           CASE WHEN version = 1 THEN 'PENDING'
                WHEN i % 13 = 0 THEN 'FAILED' ELSE 'SUCCESS' END AS status,
           event_ts + CASE WHEN version = 1 THEN interval '0'
                           ELSE interval '4 minutes' END AS updated_at,
           CASE WHEN version = 1 AND i % 20 = 0 THEN interval '2 days'
                ELSE interval '1 minute' END AS delay
    FROM generated CROSS JOIN (VALUES (1), (2)) AS versions(version)
), pilot(transaction_id, merchant_id, amount_vnd, event_ts, version, status, updated_at) AS (
    VALUES
      ('P01','M-PILOT',100000,timestamptz '2026-11-01 09:00+07',1,'SUCCESS',timestamptz '2026-11-01 09:01+07'),
      ('P02','M-PILOT', 70000,timestamptz '2026-11-01 10:00+07',1,'PENDING',timestamptz '2026-11-01 10:01+07'),
      ('P02','M-PILOT', 70000,timestamptz '2026-11-01 10:00+07',2,'SUCCESS',timestamptz '2026-11-03 08:01+07'),
      ('P03','M-PILOT', 40000,timestamptz '2026-11-01 11:00+07',1,'FAILED', timestamptz '2026-11-01 11:01+07'),
      ('P04','M-PILOT', 50000,timestamptz '2026-11-02 00:00+07',1,'SUCCESS',timestamptz '2026-11-02 00:00+07'),
      ('P05','M-PILOT', 90000,timestamptz '2026-11-02 13:00+07',1,'SUCCESS',timestamptz '2026-11-02 13:01+07'),
      ('P06','M-PILOT', 30000,timestamptz '2026-11-03 08:00+07',1,'SUCCESS',timestamptz '2026-11-03 08:01+07')
), events AS (
    SELECT transaction_id, merchant_id, amount_vnd, event_ts, version, status,
           updated_at, updated_at + delay AS received_at FROM background
    UNION ALL
    SELECT pilot.*, updated_at FROM pilot
), deliveries AS (
    SELECT events.*, 1 AS attempt FROM events
    UNION ALL
    SELECT transaction_id, merchant_id, amount_vnd, event_ts, version, status,
           updated_at, received_at + interval '1 day', 2
    FROM events
    WHERE version = 2 AND (transaction_id LIKE '%00' OR transaction_id = 'P02')
)
SELECT transaction_id || '-' || version || '-' || attempt AS delivery_id,
       transaction_id, merchant_id, amount_vnd, event_ts, version, status, updated_at, received_at
FROM deliveries
UNION ALL
SELECT 'BAD-' || id, tx, 'M-PILOT', amount, ts, 1, state, ts, ts
FROM (VALUES (1, NULL::text, 1000, 'SUCCESS'),
             (2, 'BAD02', -2000, 'SUCCESS'),
             (3, 'BAD03',  3000, 'UNKNOWN')) AS invalid(id, tx, amount, state)
CROSS JOIN (VALUES (timestamptz '2026-11-03 12:00+07')) AS batch(ts);
COMMIT;
