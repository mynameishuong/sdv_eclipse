# 18 — Thuật ngữ và câu hỏi thường gặp

## Thuật ngữ đọc source

| Từ | Giải thích trong ngữ cảnh bộ này |
| --- | --- |
| SDV | Software Defined Vehicle; kiến trúc và vòng đời hướng phần mềm |
| E/E | Electrical/Electronic architecture của xe |
| ECU | Electronic Control Unit |
| MCU / SoC / HPC | Vi điều khiển / system-on-chip / high-performance compute |
| BSP | Board Support Package |
| HAL | Hardware Abstraction Layer |
| VAL | Vehicle Abstraction Layer; với KUKSA còn là namespace/API cụ thể |
| VSS | Vehicle Signal Specification của COVESA |
| DBC | Mô tả mapping signal trong CAN messages |
| Provider | Adapter publish giá trị và/hoặc cung cấp actuator theo API |
| Consumer | Đọc/subscribe và sử dụng dữ liệu |
| Broker | Trung gian quản lý dữ liệu/message theo contract cụ thể |
| RPC / gRPC | Remote procedure call / framework RPC dùng trong demo |
| Protobuf / proto | Message schema và serialization; `.proto` là source contract |
| IPC | Inter-process communication |
| SOME/IP-SD | Service discovery cho SOME/IP |
| QoS | Quality of service; tập chính sách cụ thể theo middleware |
| OCI | Open Container Initiative; standards liên quan container image/runtime |
| Digest | Content identifier, khác mutable tag |
| Desired state | Trạng thái workload mong muốn ở control plane |
| Readiness / liveness | Sẵn sàng phục vụ / còn hoạt động theo tiêu chí kiểm tra |
| SIL / HIL | Software-in-the-loop / hardware-in-the-loop |
| DTC / UDS / DoIP | Diagnostic trouble code / diagnostic services / diagnostics over IP |
| SOVD | Service-oriented vehicle diagnostics |
| OTA / A-B | Update từ xa / bố trí slot phục vụ update/recovery theo thiết kế |
| SBOM | Software bill of materials |
| Provenance | Thông tin nguồn gốc/quá trình tạo artifact |
| ASIL / QM | Thuật ngữ mức integrity/quality trong functional-safety context; không tự gán cho demo |
| TARA / HARA | Threat analysis and risk assessment / hazard analysis and risk assessment |
| NTP / PTP | Các cơ chế đồng bộ thời gian qua mạng |
| E2E | Có thể là end-to-end integration hoặc protection profile tùy ngữ cảnh; phải nói rõ |

## Có bắt buộc Eclipse IDE không?

Không. IDE/CDT phục vụ development; Eclipse SDV là hệ sinh thái projects/runtime/tooling rộng hơn. Chọn editor phù hợp ngôn ngữ, build và debug workflow.

## Eclipse SDV có thay AUTOSAR không?

Không thể kết luận chung cho cả hệ sinh thái. Các thành phần có scope khác nhau, có thể được tích hợp trong kiến trúc cùng các platform khác. Muốn so sánh phải chọn chức năng, API, compatibility, target và assurance cụ thể. “Open source” chưa trả lời câu hỏi feature coverage và qualification.

## KUKSA có tự đọc CAN không?

Databroker không tự suy ra mapping bus. Cần provider hiểu source, mapping và quality. Schema VSS mô tả signal; DBC/mapping giải thích bit ở nguồn.

## Tại sao không dùng MQTT cho mọi thứ?

MQTT phù hợp nhiều luồng telemetry; nhưng không tự cung cấp VSS semantics, memory ownership cho raw image IPC hay deadline control loop. Chọn theo contract và measurement.

## Vì sao get thành công vẫn UNKNOWN?

RPC success là thành công giao tiếp. Policy còn kiểm tra missing/type/range/source timestamp/coherence. Đây là những bằng chứng độc lập.

## Polling hay subscribe tốt hơn?

Polling đơn giản để quan sát và kiểm tra age định kỳ. Subscribe hiệu quả khi cần phản ứng với thay đổi nhưng phải có cache, reconnect/backpressure và timer phát hiện im lặng. Dù dùng cách nào, consumer vẫn kiểm tra tuổi dữ liệu.

## Docker restart có phải OTA không?

Không đủ. Còn artifact identity, compatibility, điều kiện cập nhật, rollout policy, health gate, rollback và audit. Restart là một thao tác lifecycle.

## Có thể triển khai ngay lên xe không?

Bạn có thể dùng code làm điểm khởi đầu cho bench/prototype. Để chạy chức năng trên xe phải có yêu cầu, hardware mapping, integration, timing, security/safety engineering và validation phù hợp. Bộ này đã tách phần code có sẵn khỏi phần cần hoàn thành trong capstone.

## Học xong có thành expert không?

Tài liệu giúp đi đúng trình tự và tạo project có bằng chứng. Năng lực expert còn đến từ phát triển/vận hành thực, review, đo đạc và xử lý lỗi trên nhiều release và target.
