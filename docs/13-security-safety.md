# 13 — Security, isolation và safety trong kiến trúc

## 1. Đặt trust boundaries lên sơ đồ

Trong baseline, simulator, broker và app nằm trên network lab. Khi đổi simulator thành nguồn thật hoặc cho phép cloud connector, mức độ tin cậy thay đổi. Vẽ boundary giữa vehicle bus ↔ provider; provider ↔ broker; app ↔ lifecycle manager; vehicle ↔ cloud; build system ↔ artifact registry.

Với mỗi boundary, ghi ai gửi, ai nhận, xác minh identity bằng gì, quyền gì và dữ liệu không hợp lệ bị xử lý ở đâu.

## 2. Authentication, authorization và encryption

Authentication trả lời “ai đang kết nối”; authorization trả lời “được thao tác gì”; encryption bảo vệ nội dung truyền. TLS và token scope không thay thế nhau.

KUKSA có cấu hình TLS và authorization trong [user guide](https://github.com/eclipse-kuksa/kuksa-databroker/blob/0.7.1/doc/user_guide.md). Khi bật, cần client dùng secure channel, trust CA, xác minh server identity, token metadata và test positive/negative permissions. Không chỉ bỏ `--insecure` rồi xem toàn hệ thống đã secure.

Baseline dùng insecure channel trong adapter và tắt authorization **có chủ đích cho network lab**. Chương này là kế hoạch nâng cấp, không tuyên bố adapter đã hỗ trợ TLS/JWT.

## 3. Permission matrix đề xuất

| Principal | Read | Publish | Actuate |
| --- | --- | --- | --- |
| Provider | Chỉ metadata cần thiết | Speed, SOC, lab temperature | Không |
| Advisor | Ba input | AdvisoryMode | Không |
| Observer | Inputs + mode nếu được cấp | Không | Không |
| Cloud connector | Mode và telemetry được chọn | Không mặc định | Không mặc định |

Khi hiện thực, map bảng này vào đúng claim/policy format của broker version đã pin. Negative test phải chứng minh observer không publish được và advisor không tự ghi vào sensor nguồn.

## 4. Container isolation đủ đến đâu?

Container thường dùng chung kernel host. Namespace/cgroups/capabilities giúp giới hạn tài nguyên/quyền, nhưng không tự tạo mức isolation cho mọi safety/security requirement. VM/hypervisor hay process partitioning cũng cần cấu hình và bằng chứng, không có lựa chọn mặc định đúng cho mọi ECU.

Compose đã drop capabilities và chạy app non-root/read-only. Chưa có thiết kế resource budget hay malicious workload qualification. Thêm memory/CPU limits sau khi đo baseline, kiểm tra overload và quan sát OOM/restart behavior. Privileged hoặc host networking làm thay đổi boundary, cần có lý do cụ thể.

## 5. Safety khác cybersecurity

Functional safety quan tâm rủi ro do malfunction của hệ thống; cybersecurity engineering quan tâm threats và bảo vệ tài sản trước các hành vi tấn công. Hai hướng có liên quan nhưng assurance không tự chuyển từ hướng này sang hướng kia.

Để đọc thuật ngữ và phạm vi chuẩn, xem trang chính thức [ISO 26262-1:2018](https://www.iso.org/standard/68383.html) và [ISO/SAE 21434:2021](https://www.iso.org/standard/70918.html). Bộ này không sao chép chuẩn, không cung cấp đánh giá compliance và không thay safety/cybersecurity process của dự án.

## 6. Failure behavior cần được yêu cầu rõ

Trong lab, invalid/stale → UNKNOWN là hành vi quan sát; nó không được gọi là “safe state của BMS”. Safe state thực phụ thuộc chức năng, hazard analysis, hệ thống dự phòng và thời gian cho phép phản ứng.

Nếu broker chết, app log được UNKNOWN nhưng không ghi output mới lên broker. Downstream không kiểm tra output age có thể tiếp tục tin NORMAL cũ. Vì thế thiết kế phải kiểm tra freshness ở **mọi consumer có quyết định dựa trên dữ liệu**, không chỉ input của advisor.

Trường hợp nguồn đứng yên nhưng timestamp vẫn được refresh bởi provider lỗi cũng vượt qua stale check. Cần quality, source counter, plausibility và diagnostic mechanism phù hợp để giải quyết; không có một if-condition giải quyết toàn bộ data validity.

## 7. Bài threat model và failure analysis

Lập bảng cho bốn tình huống: provider phát nhiệt độ giả; observer ghi nhầm signal; app ăn hết RAM; clock lùi/tiến. Ghi asset, cause/threat, observable effect, detection, reaction và test. Phân biệt thứ đã implement với mitigation dự kiến.

Tiêu chí hoàn thành: có permission matrix, hai negative auth tests sau khi thêm TLS/token, một overload test và giải thích được giới hạn safety của prototype.
