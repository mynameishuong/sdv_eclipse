# 00 — SDV từ số 0

## 1. Xe được “định nghĩa bằng phần mềm” nghĩa là gì?

Hãy bắt đầu với một chức năng: hiển thị cảnh báo khi nhiệt độ pin tăng. Bạn cần đo nhiệt độ, đưa dữ liệu đến chương trình, quyết định cảnh báo và hiển thị. Khi thay đổi hành vi, bạn muốn thay phần mềm mà không phải thiết kế lại toàn bộ ECU và dây điện.

SDV là cách tổ chức kiến trúc và vòng đời phát triển để làm được điều đó: chức năng được hiện thực bằng phần mềm, có interface rõ ràng, có thể kiểm thử và cập nhật theo những ràng buộc của xe. Việc có màn hình lớn, cài Linux hoặc dùng container chỉ là những lựa chọn kỹ thuật; từng lựa chọn chưa đủ tạo thành một kiến trúc SDV.

Ví dụ trong giáo trình: phiên bản app đầu cảnh báo ở 45°C; phiên bản sau bổ sung kiểm tra dữ liệu quá hạn. Provider lấy dữ liệu và broker không cần biết thuật toán cảnh báo thay đổi thế nào. Sự tách rời này có ý nghĩa khi interface giữa các bên được giữ ổn định.

## 2. Các khối cơ bản

| Khái niệm | Hiểu bằng một ví dụ | Câu hỏi kỹ sư phải trả lời |
| --- | --- | --- |
| Sensor | Cảm biến nhiệt đo 47°C | Ai đo? Lúc nào? Độ chính xác bao nhiêu? |
| Actuator | Quạt/pump thực hiện lệnh | Ai được ra lệnh? Có feedback không? |
| ECU | Máy tính chuyên dụng trong xe | CPU, RAM, OS, interface, deadline? |
| MCU | Vi điều khiển gần cảm biến/actuator | Tài nguyên và timing có phù hợp? |
| HPC/SoC | Máy tính mạnh chạy nhiều ứng dụng | Các workload được cách ly ra sao? |
| Signal | `BatteryTemperature = 47` | Đơn vị, timestamp, quality? |
| Service | `StartCooling(mode)` | Request/response, lỗi và quyền truy cập? |
| Application | Logic tính cảnh báo | Input/output contract là gì? |
| Platform | OS, middleware và dịch vụ nền | App dựa vào những bảo đảm nào? |
| Cloud backend | Thu thập trạng thái của đội xe | Xe mất mạng thì xử lý thế nào? |

**Signal là một giá trị có nghĩa; CAN frame là một cách mang các bit.** Bạn không thể suy ra “byte thứ 2 nghĩa là tốc độ” nếu chưa có mapping. **Service là một hành vi có contract; cổng TCP chỉ là endpoint vận chuyển.**

## 3. Tách bốn câu chuyện

1. **Chức năng:** cần cảnh báo cái gì? Khi nào chuyển trạng thái?
2. **Dữ liệu:** lấy giá trị nào, kiểu gì, đơn vị gì, có mới không?
3. **Thực thi:** process nào chạy trên ECU nào, có đủ CPU/RAM không?
4. **Vòng đời:** build, deploy, quan sát, cập nhật và phục hồi thế nào?

Nếu nói “dùng KUKSA” mà chưa trả lời câu 1 thì chưa có thiết kế chức năng. Nếu nói “dùng Docker” mà chưa trả lời câu 2 thì chưa có data contract. Một architecture tốt nối được cả bốn câu chuyện.

## 4. Các nền tảng cần học trước

- **Linux:** process/thread, file permission, systemd, signal SIGTERM, journal.
- **Networking:** IP, port, DNS, TCP/UDP, localhost, namespace và TLS.
- **Programming:** Python để thử app; C/C++/Rust để hiểu embedded và middleware.
- **Git/build:** commit, branch, dependency pin, compiler và cross compilation.
- **Automotive:** CAN/CAN FD, DBC, E/E architecture, sensor/actuator feedback.

Bạn đã có thư mục `linux_networking` ở workspace: có thể nối kiến thức socket/network namespace ở đó với chương 04 và 07 của bộ này. Không cần hoàn thành mọi chủ đề trước khi chạy offline policy.

## 5. Thế nào là hiểu, thế nào là chạy được?

Chạy được là thấy một process in `WARN`. Hiểu được là giải thích tại sao nó in `WARN`, dữ liệu từ đâu đến, chuyện gì xảy ra khi nguồn ngừng gửi và chương trình khôi phục như thế nào. Triển khai được là đóng gói, cấu hình, đo tài nguyên và chứng minh hành vi trên môi trường đích.

Expert không có nghĩa nhớ tên tất cả Eclipse project. Bạn phải đặt được yêu cầu, chọn đúng công cụ, chứng minh tính phù hợp và vận hành được hệ thống khi có lỗi.

## Bài tập và tiêu chí hoàn thành

Vẽ một luồng “đo nhiệt độ → cảnh báo”. Đánh dấu đâu là sensor, ECU, network, signal, application và output. Sau đó thêm trường hợp sensor ngừng gửi trong 10 giây.

Hoàn thành khi bạn giải thích được vì sao nhận lại giá trị `47` từ broker chưa chứng minh rằng cảm biến vừa đo `47`.

Đọc tiếp: [01 — Kiến trúc SDV](01-sdv-architecture.md). Nguồn định hướng hệ sinh thái: [Eclipse SDV](https://eclipsesdv.org/).
