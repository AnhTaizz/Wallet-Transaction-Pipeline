BEGIN;

CREATE TABLE public.transactions (
    transaction_id text PRIMARY KEY,
    customer_id text NOT NULL,
    amount_vnd bigint NOT NULL CHECK (amount_vnd > 0),
    status text NOT NULL CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED')),
    event_ts timestamptz NOT NULL,
    updated_at timestamptz NOT NULL CHECK (updated_at >= event_ts)
);

INSERT INTO public.transactions (transaction_id, customer_id, amount_vnd, status, event_ts, updated_at)
VALUES
    ('TX001', 'U001', 100000, 'SUCCESS', '2026-11-01 09:00:00+07', '2026-11-01 09:01:00+07'),
    ('TX002', 'U002',  50000, 'SUCCESS', '2026-11-01 09:30:00+07', '2026-11-01 09:31:00+07'),
    ('TX003', 'U001',  30000, 'FAILED',  '2026-11-01 10:00:00+07', '2026-11-01 10:01:00+07'),
    ('TX004', 'U003',  70000, 'PENDING', '2026-11-01 10:30:00+07', '2026-11-01 10:31:00+07'),
    ('TX005', 'U002', 200000, 'SUCCESS', '2026-11-02 00:00:00+07', '2026-11-02 00:00:00+07');

COMMIT;
