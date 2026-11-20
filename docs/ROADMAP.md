# Lộ trình thực hành Junior Data Engineer

**Bài toán cuối khóa.** Sáng thứ Hai, vận hành báo doanh số merchant ngày 1/11 đã thay đổi sau khi chốt ngày, còn sao kê cuối kỳ lệch 86.000 VND. Bạn phải tìm đúng giao dịch, giải thích chênh lệch, chạy lại đúng phạm vi và chứng minh báo cáo các ngày khác vẫn đúng. Các bài bên dưới tạo dần công cụ để xử lý yêu cầu này.

Nhịp gợi ý là 10 tuần, mỗi tuần 3 buổi, mỗi buổi khoảng 2 giờ. Buổi đầu lần theo một ví dụ, buổi hai tự triển khai, buổi ba đổi dữ liệu hoặc gây một lỗi rồi sửa. Có thể học chậm hơn ở phần Spoon hoặc Spark. Khi hoàn thành một bài, ghi lệnh, kết quả dự đoán, kết quả thực tế và một điều đã tự sửa vào [nhật ký học](../TIEN_DO.md).

## Bắt đầu từ đâu

Mỗi lesson gồm 4–6 micro-lesson có thao tác và tiêu chí tự kiểm tra. Mở [danh sách bài nhỏ](MICRO_LESSONS.md) và bắt đầu ở 1.1.

- **Có trong repo:** PostgreSQL với 5 giao dịch, HDFS lab, lab Spark SQL 12 dòng có lệnh chấm và [bộ đối soát đa nguồn](../data/capstone/README.md). Dùng lab 5 dòng để học giao diện; chuyển sang bộ lớn từ tuần 4.
- **Cần chuẩn bị theo từng mốc:** tuần 1 cần PDI/Spoon và Hadoop add-on tương thích. Tuần 3 cần Bash và PDI CLI. Tuần 7 và 8 tự dựng Rundeck và Airflow theo hướng dẫn chính thức, ghi phiên bản và lệnh khởi động vào repo. Các service điều phối và bài giải là phần thực hành. [Cài Spoon](https://docs.pentaho.com/install/pentaho-installation-overview-cp/installation-of-the-pentaho-design-tools) · [Rundeck Docker](https://docs.rundeck.com/docs/administration/install/docker.html) · [Airflow Docker Compose](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- **Buổi đầu:** mở [hướng dẫn Spoon](INGESTION_LAB.md), tạo transformation và dừng ở Preview. Đọc to một dòng: mã giao dịch nào, số tiền bao nhiêu, trạng thái gì. Lưu file `.ktr`, đóng rồi mở lại và tự kết nối lần nữa.

## Mười bài thực hành

| Tuần | Nhiệm vụ và sản phẩm cần nộp | Tự kiểm tra trước khi sang bài tiếp |
| --- | --- | --- |
| 1 · Spoon và SQL nguồn | Tạo transformation `extract_wallet.ktr` có `Table Input`. Preview 5 dòng rồi thử lọc `PENDING`. Tạo job `wallet_daily.kjb`, nối `START → Transformation` và gọi file vừa lưu. | Chạy được cả transformation riêng và job từ START. Giải thích được mũi tên trong job điều khiển thứ tự, còn mũi tên trong transformation chuyển dòng dữ liệu. |
| 2 · Job cha, job con, biến và HDFS | Mở rộng job cha thành `START → Set variables → Job`. Tạo job con gọi transformation ghi HDFS. Truyền hai mốc thời gian, dùng biến cho thư mục staging và thử nhánh lỗi. [Các bước trong Spoon](INGESTION_LAB.md#tổ-chức-job-cha-và-job-con) | Hai lần chạy từ job cha ghi hai thư mục, lần lượt 4 và 2 dòng. Lỗi ở transformation làm job cha báo lỗi. Đổi đường dẫn ở bước khởi tạo và kiểm tra nơi ghi mới. |
| 3 · Bash, Kitchen và Git | Viết script Bash nhận khoảng lô, kiểm tra đầu vào rồi gọi Kitchen chạy `wallet_daily.kjb`. Log khoảng chạy, đường dẫn và trả mã thoát cho bên gọi. Dùng Pan khi cần chạy riêng `extract_wallet.ktr` để chẩn đoán. | Đóng Spoon vẫn chạy được job cha. Khoảng ngược trả lỗi, khoảng hợp lệ nhưng rỗng có 0 dòng. Cố ý nhập sai tên bảng và xác nhận mã lỗi truyền từ job con ra Bash. |
| 4 · SQL và hợp đồng dữ liệu | Hoàn thành bài 1–2 của lab CSV. Nạp view capstone, khảo sát số dòng, khóa, NULL, bản sao và thứ tự đến. Viết SQL tìm một bản cũ đến sau bản mới. Lập từ điển dữ liệu ngắn cho ba đầu vào. | Chạy `check 1` và `check 2` của lab nhỏ. Trên bộ lớn, giải thích được vì sao lọc lô bằng `received_at`, chọn trạng thái bằng `version` và tính doanh số bằng `event_ts`. Minh họa bằng P02 và BG000020. [Lab SQL](../HUONG_DAN.md) · [Dữ liệu](../data/capstone/README.md) |
| 5 · Spark và chất lượng | Dùng Spoon đưa các lần giao lên HDFS, đưa hai CSV tham chiếu lên cùng cụm. Viết job PySpark đọc raw với schema tường minh, tách dòng lỗi, khử trùng và lưu bảng trạng thái dưới dạng Parquet. Viết kiểm tra tự động cho khóa duy nhất, số dòng và phiên bản thắng. | Chạy đủ kỳ được 3 dòng lỗi, 60.007 phiên bản hợp lệ và 30.006 dòng trạng thái. Ghi lại lý do của từng dòng lỗi. Phát lại lô cũ sau lô mới mà trạng thái vẫn đúng. |
| 6 · Mô hình dữ liệu và đối soát | Hoàn thành bài 3–4 của lab CSV. Với capstone, ghép lịch sử merchant theo thời gian, tạo bảng doanh số ngày và bảng đối soát kỳ bằng Spark SQL. Viết truy vấn cho vận hành xem các mã lệch. | P04 ở hạng PREMIUM ngay tại mốc đổi hạng. Mỗi giao dịch ghép được đúng một phiên bản merchant. Báo cáo M-PILOT khớp số kiểm tra của cả ba ngày và giải thích được từng khoản trong +86.000 VND. |
| 7 · Rundeck và thao tác vận hành | Tạo project và job chạy thủ công. Khai báo hai option thời gian, chọn node có Bash, Kitchen, driver, các file `.kjb` và `.ktr` và kết nối tới DB/HDFS. Gọi script tuần 3, lưu job definition và ghi cách import. | Một người khác bấm Run với hai mốc và tìm được file HDFS từ log. Thử thiếu file `.ktr`, ghi lại bước lỗi và mã thoát. Khôi phục file và chạy lại đúng khoảng. [Rundeck Script step](https://docs.rundeck.com/docs/manual/jobs/job-plugins/node-steps/builtin.html) |
| 8 · Airflow và chạy bù | Viết DAG theo ngày có các task lấy dữ liệu, kiểm tra raw, cập nhật trạng thái, tính lại các ngày bị ảnh hưởng và đối soát. Dùng cùng lệnh nghiệp vụ với Rundeck. Chọn timetable có data interval theo ngày, ghi rõ múi giờ và đầu cuối khoảng. | Chạy bù 3 ngày đầu tháng 11/2026. Log cho thấy các khoảng liên tiếp theo UTC+7. Tạo lỗi sau bước lưu raw, retry từ snapshot đã công bố. So sánh nội dung bảng kết quả trước và sau hai lần chạy lại. [Airflow DAG runs và data interval](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html) |
| 9 · Chẩn đoán và hiệu năng | Mô phỏng hai sự cố: thiếu sao kê và đối tác gửi lại file. Viết runbook để xác định lô, khoanh vùng task và khôi phục. Đo join lịch sử merchant trên cùng input trước và sau một thay đổi, lưu `explain`, số file và số liệu shuffle. | Thiếu file khiến bước đối soát báo lỗi và giữ kết quả đã công bố. File gửi lại không tăng doanh số. Trình bày vì sao số dòng sau join đúng; nếu thay đổi không nhanh hơn, giải thích bằng số đo. [Spark SQL performance](https://spark.apache.org/docs/3.5.0/sql-performance-tuning.html) |
| 10 · Bàn giao như một ticket thực tế | Nhận ticket mở đầu, chạy pipeline, tạo bản sửa trên branch, viết pull request có cách tái hiện và kiểm chứng. Bàn giao sơ đồ, lệnh chạy, định nghĩa doanh số, runbook, một báo cáo sự cố và demo 5 phút. | Một người đọc README có thể dựng lab, lần theo P02 từ nguồn đến báo cáo và chạy lại một ngày. Bạn giải thích được nguyên nhân, phạm vi ảnh hưởng và bằng chứng phục hồi mà không cần xem bài giải. |

## Ba quyết định kỹ thuật cần tự giải thích

1. **Nơi chạy tác vụ.** Spoon hiện dùng địa chỉ loopback trên Windows. Khi chạy từ container cùng mạng Compose, dùng PostgreSQL tại `postgres:5432`, NameNode tại `hdfs://namenode:8020` và Hadoop client kết nối DataNode theo IP nội bộ (`dfs.client.use.datanode.hostname=false`). Đặt driver và cấu hình kết nối trên node thực thi. Kiểm tra từ chính node đó bằng một lần ghi và đọc lại. [Kiến trúc và cấu hình hiện tại](ARCHITECTURE.md)
2. **Dữ liệu có thể chạy lại.** Raw giữ snapshot từng khoảng. Viết vào thư mục tạm, kiểm tra số dòng rồi mới công bố. Ghi manifest có khoảng, số dòng và đường dẫn, kể cả lô rỗng. Dùng snapshot đã công bố khi phát lại. Khi có thay đổi muộn, tính lại cả ngày phát sinh từ bảng trạng thái hiện hành. Thử bằng cách ngắt một lần chạy giữa hai bước.
3. **Ai được kích hoạt lần chạy.** Dùng Airflow cho lịch hàng ngày. Dùng Rundeck cho yêu cầu thủ công có tham số, ví dụ kiểm tra một lô hoặc yêu cầu chạy bù. Khi ghép hai công cụ, cho thao tác chạy bù đi qua một đầu mối ghi kết quả, giới hạn một lần ghi cùng phạm vi. Chứng minh hai yêu cầu trùng nhau không nhân đôi dữ liệu.

Với sao kê mẫu, chỉ kích hoạt bước đối soát kỳ sau khi đã xử lý dữ liệu qua ngày 3/11 và đến hạn nhận file. Các ngày trước đó vẫn xuất báo cáo vận hành. Nếu tới hạn mà thiếu file, lưu rõ kỳ bị ảnh hưởng và thử chạy bù khi file đến.

## Khi bị kẹt trong bài

- **Preview có dòng nhưng HDFS thiếu file.** Mở log của bước ghi, kiểm tra đường dẫn thực tế, quyền thư mục và trạng thái DataNode. Từ đúng máy chạy tác vụ, ghi thử một file nhỏ rồi đọc lại. Ghi lại phép thử nào phân biệt được lỗi mạng với lỗi quyền.
- **Spark cho tổng tiền cao hơn SQL.** Lấy riêng P02. Đếm số dòng qua từng điểm: raw, sau khử trùng, sau chọn trạng thái và sau join lịch sử. Viết một test Python nhỏ khẳng định chỉ còn một dòng sau join và hạng của giao dịch là STANDARD.
- **Airflow hiện thành công nhưng thiếu kết quả.** Tìm lệnh cuối của script Bash, kiểm tra mã thoát của Pan hoặc Spark, log task và đường dẫn output của đúng khoảng. Thêm phép kiểm tra sau ghi rồi tái hiện lỗi cũ để chứng minh DAG báo lỗi.

## Tự đánh giá mức sẵn sàng làm việc

| Tình huống đánh giá | Bằng chứng đạt |
| --- | --- |
| Nhận nguồn mới | Trong một buổi, tự chỉ ra đơn vị bản ghi, khóa nghiệp vụ, cửa sổ trích xuất và ba phép kiểm tra bằng SQL. |
| Thay đổi yêu cầu | Thêm chỉ số số giao dịch thành công theo ngày và hạng merchant, nêu quy tắc tính, viết test, chứng minh tổng theo hạng bằng tổng toàn ngày. |
| Trực vận hành | Nhận một lô lỗi chưa biết trước, tìm task gây lỗi từ log, chạy bù và so số liệu với chuẩn mà không xóa toàn bộ dữ liệu. |
| Bàn giao | Đồng nghiệp chạy được từ README. PR có mẫu input/output, truy vấn đối soát, cách phục hồi và ghi rõ phần nào chỉ kiểm chứng trong lab. |

Đánh dấu từng dòng là **cần gợi ý**, **tự làm được** hoặc **người khác đã chạy lại được**. Với dòng còn cần gợi ý, đổi ngày, đổi merchant hoặc đổi lỗi rồi làm lại từ đầu. Kết quả tự đánh giá và bằng chứng chạy là cơ sở để chọn phần còn thiếu trước khi phỏng vấn.
