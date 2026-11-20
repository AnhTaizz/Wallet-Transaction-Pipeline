# Các bài thực hành nhỏ

Mỗi dòng là một micro-lesson. Đọc cột cuối, dự đoán kết quả rồi mới thao tác. Dành khoảng 20–40 phút cho một dòng, lâu hơn nếu cần cài công cụ. Có thể dừng ở bất kỳ dòng nào và ghi mã bài cùng bằng chứng vào [nhật ký](../TIEN_DO.md). Mục tiêu cuối mỗi lesson nằm trong [lộ trình](ROADMAP.md).

Với bộ dữ liệu Kaggle, xem [sáu buổi thực hành PaySim](PAYSIM_LAB.md). Các bài bên dưới dùng các bộ dữ liệu mẫu của repo.

## 1 · Lần đầu dùng Spoon

Dùng PostgreSQL 5 giao dịch và [hướng dẫn kết nối](INGESTION_LAB.md).

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 1.1 | Mở Spoon, chọn **File → New → Transformation**, kéo **Table Input** từ tab Design vào vùng làm việc và lưu thành `extract_wallet.ktr`. | Đóng rồi mở lại file, thấy đúng bước vừa thêm. |
| 1.2 | Nhấp đúp Table Input, tạo kết nối PostgreSQL bằng thông số lab, bấm **Test**. | Test thành công và bạn chỉ ra được tên database, host và port mình vừa dùng. |
| 1.3 | Viết SELECT lấy mã, số tiền và trạng thái từ `public.transactions`. Bấm **Preview**. | Thấy 5 dòng và đọc được số tiền 70.000 VND của TX004. |
| 1.4 | Dự đoán rồi thêm điều kiện lọc PENDING. Preview lần nữa, sau đó bỏ điều kiện và lưu. | Với nguồn ban đầu chỉ còn TX004 khi lọc, đủ 5 dòng sau khi bỏ lọc. |
| 1.5 | Tạo **New → Job**, nối START với entry Transformation gọi file vừa lưu. Lưu thành `wallet_daily.kjb` và Run. | Từ log job, tìm được lần chạy của transformation. Giải thích khi nào dùng Preview và khi nào dùng Run. |

## 2 · Từ START đến file HDFS

Mở lại hai file của lesson 1. [Hướng dẫn cấu hình từng cấp](INGESTION_LAB.md#tổ-chức-job-cha-và-job-con)

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 2.1 | Nối Hadoop File Output vào Table Input. Chọn cụm lab, xuất CSV có header vào thư mục staging rồi đọc bằng `hdfs dfs -cat`. | File có 5 dòng dữ liệu và một header. |
| 2.2 | Trong job cha thêm **Set variables** ngay sau START. Đặt STAGING_ROOT, dùng biến đó trong đường dẫn đầu ra. | Đổi thư mục thử ở job cha, chạy lại và tìm được file ở đường dẫn mới. |
| 2.3 | Tạo `ingest_wallet.kjb` gọi transformation. Tại job cha, dùng entry **Job** gọi file con sau bước đặt biến. | Theo được ba cấp cha → con → transformation trong một lần chạy và file vẫn xuất đúng. |
| 2.4 | Khai báo và truyền BATCH_START, BATCH_END, BATCH_DATE qua hai cấp gọi. Lọc SQL theo khoảng nửa mở và dùng nhãn ngày cho thư mục. | Chạy lô 1/11 với dữ liệu ban đầu, thấy 4 dòng và TX004 PENDING. |
| 2.5 | Cập nhật TX004 theo hướng dẫn lab, chạy lô 2/11 và mở lại cả hai file. | Lô 2 có TX004 SUCCESS và TX005. File lô 1 còn nguyên bản PENDING. |
| 2.6 | Thử sai tên bảng trong transformation. Nối nhánh thất bại của job con tới Abort job, lần theo log rồi sửa lại. | Job cha báo thất bại và bạn chỉ được dòng log nêu bảng sai. Sau khi sửa, chạy lại thành công. |

## 3 · Bash, Kitchen và Git

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 3.1 | Đóng Spoon, dùng Kitchen chạy job cha với cùng tham số đã thử. | File HDFS khớp kết quả ở lesson 2. |
| 3.2 | Bọc lệnh vào script Bash, kiểm tra đủ tham số, định dạng và thứ tự thời gian. | Khoảng kết thúc trước lúc bắt đầu bị từ chối trước khi ghi file. |
| 3.3 | Chạy một khoảng rỗng rồi thử với đường dẫn job sai. In mã thoát ngay sau mỗi lần chạy. | Phân biệt được 0 dòng hợp lệ và lần chạy lỗi bằng log cùng mã thoát. |
| 3.4 | Lưu script, job, transformation và hướng dẫn trên một branch. Chạy thử từ thư mục làm việc khác. | Tìm được file con qua đường dẫn tương đối và tái hiện được lần chạy từ README. |

## 4 · SQL và khám phá dữ liệu

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 4.1 | Làm bài khảo sát và làm sạch trên [CSV 12 dòng](../HUONG_DAN.md). | Hai lệnh check 1 và check 2 đạt; giải thích được mỗi dòng đại diện cho gì. |
| 4.2 | Mở [ba nguồn capstone](../data/capstone/README.md), ghi đơn vị bản ghi và thử khóa ứng viên bằng SQL. | Phân biệt được một lần giao, một phiên bản và một giao dịch. |
| 4.3 | Sắp các dòng BG000020 theo thời điểm nhận, rồi sắp theo phiên bản. | Chỉ ra vì sao lấy dòng đến cuối có thể khôi phục nhầm trạng thái cũ. |
| 4.4 | Viết truy vấn đếm dòng lỗi theo lý do, rồi đếm bản giao lại trong phần hợp lệ. | Đối chiếu được 3 dòng lỗi và 301 lần giao lại. |

## 5 · Spark, HDFS và Parquet

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 5.1 | Điều chỉnh luồng Spoon cho view capstone, trích theo received_at và đưa hai CSV tham chiếu vào HDFS. | Tổng số lần giao của cả kỳ ở raw bằng 60.311; đọc được cả hai CSV từ node chạy Spark. |
| 5.2 | Khai báo schema trong PySpark và tách hai tập hợp lệ, lỗi. | Đếm được 60.308 dòng hợp lệ và truy ra delivery_id cùng lý do của từng dòng lỗi. |
| 5.3 | Gộp các lần giao cùng phiên bản, sau đó chọn phiên bản lớn nhất của từng giao dịch. | Bước đầu còn 60.007 phiên bản, bước sau còn 30.006 giao dịch. |
| 5.4 | Ghi trạng thái thành Parquet, đọc lại và chạy test sau khi phát lại một lô cũ. | Khóa vẫn duy nhất, số dòng giữ nguyên và BG000020 vẫn giữ phiên bản mới. |

## 6 · Báo cáo và đối soát

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 6.1 | Hoàn thành bài 3–4 của lab CSV, chạy lại một ngày đã công bố. | Các lệnh check tương ứng đạt và giải thích được kết quả nào được thay thế. |
| 6.2 | Ghép trạng thái với lịch sử merchant bằng thời điểm phát sinh. | P02 thuộc STANDARD và P04 thuộc PREMIUM. Mỗi giao dịch có một dòng sau join. |
| 6.3 | Tính doanh số M-PILOT theo ngày phát sinh. So ngày 1 trước và sau khi nhận P02 phiên bản 2. | Ngày 1 tăng từ 100.000 lên 170.000 VND dù bản cập nhật đến ngày 3. |
| 6.4 | Đối chiếu giao dịch thành công với sao kê, giữ cả mã thiếu ở mỗi phía. | Giải thích +86.000 VND từ ba mã P04, P05, P99 và nêu được phía thiếu của từng mã liên quan. |

## 7 · Vận hành bằng Rundeck

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 7.1 | Dựng Rundeck, tạo project, chạy lệnh thử trên node đã chọn. | Log cho biết node thực tế, tìm được Kitchen và đọc được job cha từ chính node đó. |
| 7.2 | Tạo job có hai option thời gian, chuyển chúng vào script lesson 3 và suy ra nhãn ngày cho lô ngày. | Hai lần bấm Run với hai ngày tạo đúng hai khoảng trong log. |
| 7.3 | Truyền một khoảng sai rồi sửa và chạy lại. | Từ lịch sử Rundeck chỉ ra được lần lỗi, nguyên nhân, lần thành công và đường dẫn HDFS. |
| 7.4 | Export job definition và import vào project thử đã cấu hình node. | Job import chạy được cùng script với cùng tham số. |

## 8 · Điều phối bằng Airflow

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 8.1 | Dựng Airflow, viết DAG chỉ ghi hai biên của data interval theo ngày Việt Nam. | Ba khoảng liên tiếp có biên cuối ngày trước bằng biên đầu ngày sau. |
| 8.2 | Nối các task trích xuất, kiểm tra raw, cập nhật trạng thái và xuất báo cáo. | Khi raw thiếu, thấy đúng task lỗi và báo cáo cũ vẫn đọc được. |
| 8.3 | Chạy bù ngày 1–3/11, kích hoạt đối soát khi đủ kỳ và có file sao kê. | Truy được P02 về báo cáo ngày 1 và tái hiện chênh lệch của kỳ. |
| 8.4 | Gây lỗi sau khi công bố snapshot rồi retry. | Log chỉ ra snapshot được dùng lại; so nội dung đầu ra trước và sau phát lại cho cùng kết quả. |

## 9 · Xử lý sự cố và đo hiệu năng

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 9.1 | Cho pipeline chạy tới hạn đối soát với đường dẫn sao kê trống. | Xác định được kỳ bị ảnh hưởng và giữ được kết quả đã công bố trước đó. |
| 9.2 | Bổ sung file rồi mô phỏng đối tác giao lại cùng sao kê. | Phục hồi được kỳ và lần giao lại không tăng số tiền. |
| 9.3 | Đo join merchant trên cùng snapshot, thay một cấu hình hoặc cách join rồi đo lại. | Ghi hai kế hoạch thực thi, thời gian, shuffle và xác nhận kết quả nghiệp vụ bằng nhau. |
| 9.4 | Viết runbook ngắn từ sự cố vừa gặp rồi làm theo trên kỳ thử. | Từ log tìm được khoảng lỗi, lệnh chạy bù và truy vấn xác nhận phục hồi. |

## 10 · Bàn giao một ticket

| Bài | Tự làm | Dấu hiệu hoàn thành |
| --- | --- | --- |
| 10.1 | Nhận ticket đầu roadmap, tái hiện và ghi giả thuyết trước khi xem mốc kiểm tra. | Nêu rõ merchant, kỳ, số dự đoán, số thực tế và nguồn kiểm chứng. |
| 10.2 | Lần theo mã lệch qua raw, trạng thái, lịch sử merchant và sao kê. | Phân biệt được thay đổi doanh số do cập nhật muộn với sai lệch giữa hai nguồn. |
| 10.3 | Chọn một lỗi đã tái hiện, thêm test hồi quy, sửa trên branch rồi viết PR. | Test thất bại trước bản sửa và đạt sau bản sửa với cùng input. |
| 10.4 | Bàn giao README, runbook và demo 5 phút. Nhờ người khác chạy lại hoặc thử từ một checkout mới. | Tái hiện được một lô từ hướng dẫn và ghi lại điểm còn cần người hướng dẫn hỗ trợ. |
