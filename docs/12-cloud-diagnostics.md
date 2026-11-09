# 12 — Cloud, digital twin, fleet và diagnostics

## 1. Xe phải hoạt động khi không có cloud

Thermal advisory local dùng dữ liệu trong xe. Connector có thể gửi summary lên backend, nhưng mất mạng không được khiến app chờ RPC cloud để tính trạng thái. Tách local decision khỏi telemetry upload là một quyết định kiến trúc của capstone.

```text
Vehicle: provider → KUKSA → advisory
                         ↘ connector → local queue → authenticated uplink
Cloud:                    ingestion → twin / time series / fleet dashboard
```

Đây là kiến trúc mở rộng đề xuất; baseline chưa có cloud connector.

## 2. Các building block phía cloud

| Thành phần | Vai trò | Không được nhầm |
| --- | --- | --- |
| MQTT / Mosquitto | Pub/sub telemetry | MQTT topic không tự mang VSS metadata/vehicle policy |
| Hono | Device connectivity, identity, tenant concepts | Không tự là thuật toán ứng dụng trong xe |
| Ditto | Mô hình digital twin và state access/policy | Twin state có thể cũ; không phải physical truth tức thì |
| Time-series/event store | History, analytics/replay | Broker current values chưa thay thế database này |
| Fleet release service | Chọn nhóm nhận version/config | Không đồng nghĩa orchestrator local |

Nguồn: [Mosquitto documentation](https://mosquitto.org/documentation/), [Hono concepts](https://eclipse.dev/hono/docs/concepts/), [Ditto overview](https://eclipse.dev/ditto/intro-overview.html).

## 3. Thiết kế telemetry contract

Một message nên có `vehicle_id` giả cho lab, `schema_version`, `source_timestamp`, `sent_at`, `sequence`, `mode` và `data_quality`. Dùng UTC cho timestamp liên process, giải thích đơn vị thời gian. Với signal values, đi kèm unit/contract version hoặc có schema registry rõ ràng.

Không dùng thời điểm backend nhận làm thời điểm đo. Mất mạng 10 phút rồi upload backlog phải phân biệt observed_at và received_at. Với location/VIN hoặc dữ liệu liên quan người sử dụng, cần requirement về thu thập/quyền truy cập/retention trước khi thêm vào telemetry.

## 4. Store-and-forward

Queue local phải có dung lượng tối đa, TTL, chính sách drop và backoff. Chọn ưu tiên: alarm transition quan trọng hơn dòng sample lặp lại mỗi giây. Ghi metric queue depth/drop count. Khi reconnect, backend phải xử lý duplicate và out-of-order bằng identity/sequence/epoch phù hợp.

MQTT QoS cao không tự làm side effect ở backend thành exactly-once nghiệp vụ. Hãy thiết kế idempotency: xử lý lại cùng event ID không tạo thêm một công việc hay bản ghi logic trùng.

## 5. Diagnostics khác telemetry

Telemetry cho biết các giá trị/trạng thái vận hành; diagnostic flow có thể đọc lỗi, status dịch vụ, identification hoặc điều khiển operation đặc biệt. DTC là mã lỗi theo diagnostic design, không phải cứ log ERROR là có một DTC hợp lệ.

UDS là diagnostic service model; DoIP mang diagnostic communication trên IP theo các lớp giao thức tương ứng. SOVD hướng tới chẩn đoán service/compute của kiến trúc mới. Eclipse OpenSOVD là điểm nghiên cứu hiện thực nguồn mở: [OpenSOVD](https://github.com/eclipse-opensovd/opensovd). Chúng không tự map mọi process exception thành automotive diagnostic behavior.

Trong capstone, trước tiên expose health snapshot qua một interface lab có schema: app version, last input timestamp, last decision và last broker error. Chỉ gọi đó là endpoint health của lab. Tích hợp UDS/SOVD phải có diagnostic specification và contract test riêng.

## 6. Remote commands

Lệnh từ backend phải đi qua identity, authorization, request ID, expiry, vehicle condition và audit. Một queued command hết hạn không được áp dụng chỉ vì xe vừa online. Kết quả cần tách accepted, running, completed, rejected và timed out.

Không mở gRPC broker trực tiếp ra internet để thay connector. Cloud policy và local vehicle permissions là hai boundary phải thiết kế rõ ràng.

## Bài tập

Thiết kế connector gửi mode transition, queue tối đa 10 MB và TTL 1 giờ. Mô phỏng offline 10 phút, restart connector, reconnect với duplicated messages. Chứng minh local advisory vẫn chạy và backlog không làm storage tăng vô hạn.
