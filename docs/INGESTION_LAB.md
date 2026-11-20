# Đọc PostgreSQL và ghi HDFS bằng Spoon

Trong bài này, bạn tự tạo transformation trong Spoon trên Windows, xuất 5 giao dịch mẫu thành CSV trên HDFS và kiểm tra lại số dòng. Sau đó bạn dùng cùng transformation để thử hai lô theo `updated_at`.

## Khởi động PostgreSQL và HDFS

Cần Docker Desktop chạy Linux containers và một bản Pentaho Data Integration (PDI) có bước `Hadoop File Output` cùng driver Apache Hadoop tương thích. Mở PDI bằng `Spoon.bat` và dùng bản Java mà phiên bản PDI đó hỗ trợ. [Mở Spoon](https://docs.pentaho.com/pdia-data-integration/start-the-pdi-client) · [Driver Hadoop](https://docs.pentaho.com/install/use-hadoop-with-pentaho)

Chạy các lệnh sau từ thư mục gốc của repo.

```powershell
docker compose --profile ingest up -d --wait postgres datanode
docker compose --profile ingest ps
docker compose --profile ingest exec postgres psql -U wallet -d wallet_lab -c 'SELECT count(*) FROM public.transactions;'
docker compose --profile ingest exec namenode hdfs dfsadmin -report -live
docker compose --profile ingest exec namenode hdfs dfs -mkdir -p /wallet-lab/staging
docker compose --profile ingest exec namenode hdfs dfs -chmod 1777 /wallet-lab/staging
```

Kỳ vọng `count = 5` và `Live datanodes (1)`. Lần đầu Docker cần tải image. PostgreSQL nạp bảng mẫu khi volume DB được khởi tạo. Mở `http://127.0.0.1:19870` để xem NameNode. Thư mục `/wallet-lab/staging` cho phép người dùng Spoon trên máy ghi file.

## Đọc nguồn trong Spoon

1. Tạo **New transformation** rồi kéo **Table Input** vào canvas. Trong step, tạo kết nối kiểu **PostgreSQL**, access **Native (JDBC)**.

   | Trường | Giá trị trong lab |
   | --- | --- |
   | Host | `127.0.0.1` |
   | Port | `15432` |
   | Database | `wallet_lab` |
   | Username | `wallet` |
   | Password | `wallet_lab` |

2. Bấm **Test**, rồi nhập truy vấn và bấm **Preview**. Kiểm tra TX004 đang `PENDING` ở lần khởi tạo đầu tiên. [Tài liệu Table Input](https://docs.pentaho.com/pdia-data-integration/pdi-transformation-steps-reference-overview/table-input)

   ```sql
   SELECT transaction_id, customer_id, amount_vnd, status, event_ts, updated_at
   FROM public.transactions
   ORDER BY transaction_id;
   ```

## Ghi và đối chiếu trên HDFS

1. Trong **View → Hadoop Clusters**, tạo kết nối `wallet-hdfs` với driver Apache Hadoop mà bản PDI hỗ trợ. Dùng cấu hình trong [`config/spoon`](../config/spoon), với `fs.defaultFS` là `hdfs://127.0.0.1:18020` và `dfs.client.use.datanode.hostname` là `true`. Hai thiết lập giúp Spoon trên Windows tìm đến NameNode và cổng truyền dữ liệu `19866` của DataNode qua Docker Desktop. [Nhập cấu hình cụm trong PDI](https://docs.pentaho.com/pdia-data-integration/extracting-data-into-pdi/connecting-to-a-hadoop-cluster-with-the-pdi-client-article/adding-a-cluster-connection-connect-to-a-hadoop-cluster-with-the-pdi-client/add-a-cluster-connection-by-import-add-hadoop-cluster-connection) · [Hadoop và hostname DataNode](https://hadoop.apache.org/docs/r3.4.3/hadoop-project-dist/hadoop-hdfs/HdfsMultihoming.html)

   Nếu trình import của bản PDI yêu cầu XML cho các dịch vụ khác, dùng **New cluster** để nhập HDFS host `127.0.0.1`, port `18020` và kiểu bảo mật **None**. Sau khi lưu, thêm `dfs.client.use.datanode.hostname=true` vào `hdfs-site.xml` của kết nối đó trong thư mục `~/.pentaho/metastore/pentaho/NamedCluster/Configs/wallet-hdfs`, rồi mở lại Spoon. [Cấu hình Hadoop trong Pentaho](https://docs.pentaho.com/install/use-hadoop-with-pentaho)

2. Nối **Table Input → Hadoop File Output**. Chọn `wallet-hdfs` và đặt **Folder/File** là `/wallet-lab/staging/transactions` cùng **Extension** là `csv`. Dùng dấu phẩy, bật header, chọn UTF-8 và dùng **Get Fields** để lấy các cột từ `Table Input`. Lưu transformation dưới dạng `.ktr` rồi chạy trong Spoon. [Tài liệu Hadoop File Output](https://docs.pentaho.com/pdia-data-integration/pdi-transformation-steps-reference-overview/hadoop-file-output-cp-main-page)

3. Xem file và đối chiếu 5 dòng dữ liệu với Preview. Kiểm tra `transaction_id`, `status` và `amount_vnd` của TX004 trước khi chuyển bài.

   ```powershell
   docker compose --profile ingest exec namenode hdfs dfs -ls /wallet-lab/staging
   docker compose --profile ingest exec namenode hdfs dfs -cat /wallet-lab/staging/transactions.csv
   ```

Nếu Spoon đọc được thư mục nhưng ghi file lỗi, kiểm tra trạng thái DataNode bằng lệnh `dfsadmin` ở trên và cổng `19866` bằng `Test-NetConnection 127.0.0.1 -Port 19866`. Kiểm tra quyền ghi và cấu hình `dfs.client.use.datanode.hostname` của kết nối đang dùng.

## Tổ chức job cha và job con

Trong buổi đầu, chọn **File → New → Job**, kéo **START** và **Transformation** vào canvas. Trong entry **Transformation**, chọn file `extract_wallet.ktr` đã thử bằng Preview. Nối hai entry, lưu job thành `wallet_daily.kjb` rồi bấm **Run**. Bây giờ bạn có thể theo dõi lần chạy từ cấp job.

Ở bài 2, tổ chức ba file trong cùng thư mục và dùng đường dẫn tương đối với `${Internal.Entry.Current.Directory}` khi chọn file con.

| File | Các bước trên canvas | Việc tự cấu hình |
| --- | --- | --- |
| `wallet_daily.kjb` | START → Set variables → Job | Trong **Job settings → Parameters**, khai báo `BATCH_START`, `BATCH_END` và `BATCH_DATE`. Khi Run, nhập hai mốc có offset +07 và nhãn ngày dạng YYYY-MM-DD. Trong **Set variables**, đặt `STAGING_ROOT=/wallet-lab/staging` với phạm vi dùng được từ job gốc và các bước con. Trong entry **Job**, chọn `ingest_wallet.kjb`. |
| `ingest_wallet.kjb` | START → Transformation | Khai báo cùng ba tham số. Trong tab **Parameters** của entry gọi job con ở job cha, chọn **Pass parameter values to sub-job**. Tại job con, chọn `extract_wallet.ktr` rồi truyền tiếp ba tham số trong tab **Parameters** của entry **Transformation**. |
| `extract_wallet.ktr` | Table Input → Hadoop File Output | Khai báo cùng tên tham số trong **Transformation settings**. Lọc theo khoảng lô và đặt tên file đầu ra là `${STAGING_ROOT}/${BATCH_DATE}/transactions`, extension `csv`. Bật tạo thư mục cha. |

Để thử hai mốc trong **Table Input**, có thể dùng truy vấn mẫu dưới đây với **Replace variables in script** cho các mốc ISO do chính bạn nhập trong lab. Khi đưa vào script, kiểm tra định dạng thời gian và thứ tự hai mốc trước khi gọi Kitchen.

```sql
SELECT transaction_id, customer_id, amount_vnd, status, event_ts, updated_at
FROM public.transactions
WHERE updated_at >= CAST('${BATCH_START}' AS timestamptz)
  AND updated_at <  CAST('${BATCH_END}' AS timestamptz)
ORDER BY updated_at, transaction_id;
```

Dùng hop thành công từ bước khởi tạo sang entry **Job**. Để tập xử lý lỗi, nối hop thất bại từ entry **Transformation** của job con sang **Abort job**. Thử sai tên bảng, chạy từ job cha và tìm câu lỗi SQL trong log của transformation. Job cha phải báo thất bại. Sửa lại rồi chạy thành công cùng bộ tham số. [Job entry và truyền tham số](https://docs.pentaho.com/pdia-data-integration/pdi-job-entries-reference-overview/job-job-entry)

## Lấy dữ liệu thay đổi theo lô

Tự thêm hai tham số thời gian vào `Table Input` và lọc theo `updated_at >= start AND updated_at < end`. Dùng các mốc `00:00:00+07` ngày `2026-11-01`, `2026-11-02` và `2026-11-03`. Chạy lô 1 trước, rồi trong PostgreSQL mẫu tự cập nhật TX004 sang `SUCCESS` với `updated_at = '2026-11-02 09:00:00+07'` và giữ `event_ts` ban đầu. Chạy lô 2, lưu hai lô vào hai thư mục HDFS riêng. Dùng **Create parent folder** hoặc tạo sẵn thư mục con.

| Lô | Số dòng | Điểm kiểm tra |
| --- | --- | --- |
| Ngày 1 | 4 | TX004 là `PENDING`. |
| Ngày 2 | 2 | TX004 là `SUCCESS`. TX005 có `updated_at` đúng bằng mốc bắt đầu lô 2 và chỉ nằm trong lô này. |

Khi nghỉ, dùng `docker compose --profile ingest stop postgres namenode datanode`. Lần khởi động sau tiếp tục dùng dữ liệu đã ghi. Ghi truy vấn, đường dẫn và kết quả đối chiếu vào [hồ sơ học tập](../TIEN_DO.md).
