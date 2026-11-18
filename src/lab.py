"""Small Spark SQL learning harness; learners edit sql/*.sql, not this file."""

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
RAW_COLUMNS = ["row_id", "transaction_id", "customer_id", "amount_vnd", "status", "event_ts", "updated_at"]
CLEAN_COLUMNS = RAW_COLUMNS
DAILY_COLUMNS = ["business_date", "total_transactions", "successful_transactions", "successful_amount_vnd"]
EXPECTED_PROFILE = [{"raw_rows": 12, "distinct_transaction_ids": 9, "success_event_rows": 9}]
EXPECTED_CLEAN = [
    {"row_id": 1, "transaction_id": "TX001", "customer_id": "U001", "amount_vnd": 100000, "status": "SUCCESS", "event_ts": "2026-11-01 09:00:00", "updated_at": "2026-11-01 09:01:00"},
    {"row_id": 3, "transaction_id": "TX002", "customer_id": "U002", "amount_vnd": 50000, "status": "SUCCESS", "event_ts": "2026-11-01 09:30:00", "updated_at": "2026-11-01 09:31:00"},
    {"row_id": 4, "transaction_id": "TX003", "customer_id": "U001", "amount_vnd": 30000, "status": "FAILED", "event_ts": "2026-11-01 10:00:00", "updated_at": "2026-11-01 10:01:00"},
    {"row_id": 6, "transaction_id": "TX004", "customer_id": "U003", "amount_vnd": 70000, "status": "SUCCESS", "event_ts": "2026-11-01 10:30:00", "updated_at": "2026-11-01 10:35:00"},
    {"row_id": 7, "transaction_id": "TX005", "customer_id": "U002", "amount_vnd": 200000, "status": "SUCCESS", "event_ts": "2026-11-02 08:00:00", "updated_at": "2026-11-02 08:01:00"},
    {"row_id": 8, "transaction_id": "TX006", "customer_id": "U004", "amount_vnd": 80000, "status": "SUCCESS", "event_ts": "2026-11-02 08:30:00", "updated_at": "2026-11-02 08:31:00"},
]
EXPECTED_DAILY = [
    {"business_date": "2026-11-01", "total_transactions": 4, "successful_transactions": 3, "successful_amount_vnd": 220000},
    {"business_date": "2026-11-02", "total_transactions": 2, "successful_transactions": 2, "successful_amount_vnd": 280000},
]


def normalize(value):
    if isinstance(value, datetime):
        return value.strftime(TIME_FORMAT)
    if isinstance(value, date):
        return value.isoformat()
    return value


def records(frame):
    # Format timestamps inside Spark's session timezone, independent of host timezone.
    from pyspark.sql.functions import col
    from pyspark.sql.types import TimestampType
    display_frame = frame.select(*[
        col(field.name).cast("string").alias(field.name)
        if isinstance(field.dataType, TimestampType) else col(field.name)
        for field in frame.schema.fields
    ])
    return [{key: normalize(value) for key, value in row.asDict().items()} for row in display_frame.collect()]


def same_result(frame, columns, expected, label):
    if frame.columns != columns:
        raise ValueError(f"{label}: tên/thứ tự cột phải là {columns}; đang có {frame.columns}")
    actual = records(frame)
    canonical = lambda rows: sorted(json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows)
    if canonical(actual) != canonical(expected):
        print("Kết quả hiện tại:", json.dumps(actual, ensure_ascii=False, indent=2))
        print("Kết quả mẫu cần đạt:", json.dumps(expected, ensure_ascii=False, indent=2))
        raise ValueError(f"{label}: kết quả chưa khớp. Xem gợi ý trong HUONG_DAN.md.")
    print(f"PASS {label}")


def require_clean_types(frame):
    from pyspark.sql.types import IntegerType, LongType, StringType, TimestampType
    expected = [IntegerType, StringType, StringType, LongType, StringType, TimestampType, TimestampType]
    if len(frame.schema.fields) != len(expected):
        raise ValueError("Bài 2: số cột chưa đúng; xem sql/02_clean.sql.")
    for field, kind in zip(frame.schema.fields, expected):
        if not isinstance(field.dataType, kind):
            raise ValueError(f"Bài 2: cột {field.name} cần kiểu {kind.__name__}; đang là {field.dataType}.")


def read_sql(spark, filename):
    query = (ROOT / "sql" / filename).read_text(encoding="utf-8").strip().rstrip(";")
    return spark.sql(query)


def load_clean(spark):
    frame = read_sql(spark, "02_clean.sql")
    require_clean_types(frame)
    same_result(frame, CLEAN_COLUMNS, EXPECTED_CLEAN, "Bài 2 — dữ liệu sạch")
    frame.createOrReplaceTempView("transactions_clean")
    return frame


def load_daily(spark):
    load_clean(spark)
    frame = read_sql(spark, "03_daily.sql")
    from pyspark.sql.types import DateType, LongType
    expected = [DateType, LongType, LongType, LongType]
    if len(frame.schema.fields) != len(expected):
        raise ValueError("Bài 3: số cột chưa đúng; xem sql/03_daily.sql.")
    for field, kind in zip(frame.schema.fields, expected):
        if not isinstance(field.dataType, kind):
            raise ValueError(f"Bài 3: cột {field.name} cần kiểu {kind.__name__}.")
    same_result(frame, DAILY_COLUMNS, EXPECTED_DAILY, "Bài 3 — tổng hợp theo ngày")
    return frame


def parse_date(value):
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Ngày phải theo dạng YYYY-MM-DD.") from error
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("Ngày phải theo dạng YYYY-MM-DD.")
    return parsed


def publish(frame, run_date, simulate_failure=False):
    key = run_date.isoformat()
    daily_rows = [row for row in records(frame) if row["business_date"] == key]
    if len(daily_rows) != 1:
        raise ValueError(f"Không có đúng một dòng cho ngày {key}; chưa ghi file.")
    output_dir = ROOT / "outputs" / "daily"
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{key}.json"
    payload = json.dumps(daily_rows[0], ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{key}-", suffix=".tmp", dir=output_dir)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if simulate_failure:
            raise RuntimeError("Lỗi giả lập trước bước thay file: kết quả cũ được giữ nguyên.")
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(f"Đã ghi {destination.relative_to(ROOT)}")
    return destination


def check_rerun(frame):
    dates = [date(2026, 11, 1), date(2026, 11, 2)]
    paths = [publish(frame, day) for day in dates]
    before = [path.read_bytes() for path in paths]
    publish(frame, dates[0])
    if before != [path.read_bytes() for path in paths]:
        raise ValueError("Chạy lại đã thay đổi kết quả hoặc ảnh hưởng ngày khác.")
    try:
        publish(frame, dates[0], simulate_failure=True)
    except RuntimeError:
        pass
    else:
        raise ValueError("Không kích hoạt được lỗi giả lập.")
    if before != [path.read_bytes() for path in paths]:
        raise ValueError("Lỗi giả lập làm thay đổi kết quả đã ghi.")
    if list(paths[0].parent.glob(".*.tmp")):
        raise ValueError("Còn file tạm sau lỗi giả lập.")
    print("PASS Bài 4 — chạy lại giữ kết quả, không ảnh hưởng ngày khác, lỗi trước commit giữ bản cũ")


def parser():
    result = argparse.ArgumentParser(description="Mini lab Spark SQL: preview, check và publish.")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("preview", help="Đọc CSV và xem dữ liệu thô; chạy được ngay.")
    check = commands.add_parser("check", help="Kiểm tra bài SQL bạn đã viết.")
    check.add_argument("lesson", type=int, choices=[1, 2, 3, 4])
    write = commands.add_parser("publish", help="Ghi kết quả cho một ngày sau khi bài 2 và 3 đạt.")
    write.add_argument("--date", type=parse_date, required=True)
    write.add_argument("--simulate-failure", action="store_true")
    return result


def main():
    args = parser().parse_args()
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.types import IntegerType, StringType, StructField, StructType
    except ImportError:
        print("Chưa có PySpark. Dùng lệnh Docker trong README.md hoặc môi trường PySpark có sẵn.", file=sys.stderr)
        return 2
    spark = None
    try:
        spark = (SparkSession.builder.master("local[2]").appName("wallet-sql-mini-lab")
                 .config("spark.ui.enabled", "false")
                 .config("spark.sql.shuffle.partitions", "2")
                 .config("spark.sql.session.timeZone", "Asia/Ho_Chi_Minh")
                 .config("spark.sql.ansi.enabled", "false")
                 .getOrCreate())
        spark.sparkContext.setLogLevel("ERROR")
        schema = StructType([StructField(column, IntegerType() if column == "row_id" else StringType(), True) for column in RAW_COLUMNS])
        raw = (spark.read.option("header", True).option("mode", "FAILFAST")
               .schema(schema).csv(str(ROOT / "data" / "transactions_raw.csv")))
        raw.createOrReplaceTempView("transactions_raw")
        print(f"Spark {spark.version} | bảng nguồn: transactions_raw | múi giờ lab: Asia/Ho_Chi_Minh")
        if args.command == "preview":
            raw.orderBy("row_id").show(20, truncate=False)
            raw.printSchema()
            print("Nguồn có", raw.count(), "dòng. Tiếp theo đọc Bài 1 trong HUONG_DAN.md.")
        elif args.command == "check":
            if args.lesson == 1:
                same_result(read_sql(spark, "01_profile.sql"), list(EXPECTED_PROFILE[0]), EXPECTED_PROFILE, "Bài 1 — khảo sát dữ liệu")
            elif args.lesson == 2:
                load_clean(spark).orderBy("transaction_id").show(truncate=False)
            elif args.lesson == 3:
                load_daily(spark).orderBy("business_date").show(truncate=False)
            else:
                check_rerun(load_daily(spark))
        else:
            publish(load_daily(spark), args.date, args.simulate_failure)
        return 0
    except Exception as error:
        print(f"CHƯA ĐẠT: {error}", file=sys.stderr)
        return 1
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    raise SystemExit(main())
