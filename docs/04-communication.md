# 04 — Middleware và communication: dùng cái nào ở đâu?

## 1. Tách semantic model, API và transport

Trong demo: VSS mô tả ý nghĩa dữ liệu; KUKSA VAL v2 mô tả API; protobuf mô tả message/serialization; gRPC thực hiện RPC; HTTP/2 và TCP/IP mang dữ liệu qua mạng. Container network cung cấp connectivity. Mỗi lớp trả lời một câu hỏi khác nhau.

“Đã dùng TCP” chưa cho bạn service discovery, permission hay signal semantics. “Đã dùng VSS” chưa cho bạn kết nối tới ECU.

## 2. Bảng lựa chọn

| Cơ chế | Phù hợp | Cần chú ý |
| --- | --- | --- |
| CAN/CAN FD | Liên lạc ECU/MCU, frame gọn | Arbitration, bus load, mapping, counter, quality |
| SOME/IP + SD | Service/method/event trên automotive Ethernet | Service/instance/version, discovery, eventgroup |
| gRPC | RPC giữa component có protobuf contract | Deadline, streaming, TLS, backpressure |
| DDS | Data-centric pub/sub với QoS | Discovery, reliability, history, deadlines, resource limits |
| Zenoh | Pub/sub/query giữa các node/môi trường mạng | Keyspace, routing, topology, delivery behavior |
| iceoryx2 | IPC giữa process bằng shared memory | Ownership, lifetime, pool size, process failure |
| MQTT | Telemetry kiểu broker qua mạng/cloud | QoS, retained, expiry, identity, duplicate handling |
| uProtocol | Model/API giao tiếp cùng các transport binding | Chọn và kiểm chứng binding; không coi là một bus vật lý |

Đây là hướng chọn ban đầu, không phải benchmark khẳng định công cụ nào nhanh nhất. Nguồn từng cơ chế: [SocketCAN](https://docs.kernel.org/networking/can.html), [vsomeip](https://github.com/COVESA/vsomeip), [gRPC concepts](https://grpc.io/docs/what-is-grpc/core-concepts/), [Cyclone DDS](https://github.com/eclipse-cyclonedds/cyclonedds), [Zenoh](https://zenoh.io/docs/overview/what-is-zenoh/), [iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2), [uProtocol specification](https://github.com/eclipse-uprotocol/up-spec).

## 3. SOME/IP từ ví dụ cụ thể

Một thermal service có thể expose `GetStatus()` và event `TemperatureChanged`. Client phải biết service ID, instance ID, major/minor version, method/event ID và payload contract. SOME/IP-SD giúp offer/find/subscribe; nhận được discovery không có nghĩa phương thức đã được cấp quyền hoặc thực thi thành công.

vsomeip hiện thực SOME/IP. CommonAPI C++ hỗ trợ cách biểu diễn interface và binding/generation cho C++; phải kiểm tra version của generator/runtime/binding. Không tự xem vsomeip là bản hiện thực đầy đủ AUTOSAR Adaptive Platform. Tham khảo [CommonAPI core](https://github.com/COVESA/capicxx-core-runtime).

Lab nâng cao: expose cùng thermal status qua SOME/IP ở một service riêng, viết adapter sang signal KUKSA. Ghi rõ field nào là sensor, field nào là method và ai sở hữu logic. Không cần ghép hai middleware chỉ để có thêm tên công nghệ.

## 4. Streaming và backpressure

Một subscriber đọc 1 message/giây trong khi nguồn gửi 1000 message/giây sẽ làm queue tăng nếu không có giới hạn. Bạn phải chọn: giữ mọi sample, giữ mới nhất, drop oldest hoặc giảm tốc producer. Lựa chọn phụ thuộc vào việc đây là telemetry hiện tại, lịch sử phân tích hay event không được phép mất.

Trong lab subscriber dùng buffer nhỏ. Khi stream reconnect, initial snapshot là trạng thái hiện tại; các event đã mất không tự biến thành history. `UNKNOWN` cần timer độc lập vì không có message mới cũng là một tình huống chức năng.

## 5. Vì sao không đưa ảnh camera vào signal broker?

Một frame 1920×1080 RGB khoảng 6,2 MB chưa nén. 30 fps khoảng 187 MB/s cho một camera, chưa tính overhead/copy. Một scalar `Vehicle.Speed` có bài toán khác hoàn toàn. Đưa raw image qua cây signal làm sai lớp abstraction của use case này.

Có thể dùng VSS cho metadata/trạng thái camera; image pipeline dùng buffer/media transport phù hợp. Nếu dùng shared memory, phải đo số lần copy thực tế toàn tuyến. Zero copy ở một đoạn không chứng minh toàn pipeline không copy.

## 6. Đo thay vì đoán

Ghi các điểm timestamp, clock source, payload size, message rate, số subscriber và CPU load. Báo cáo p50/p95/p99/max trên một cửa sổ đo đủ dài. Xác định mất message bằng sequence/counter thay vì chỉ nhìn log “received”.

Một benchmark trên localhost không đại diện cho Ethernet switch, congestion, ARM target, thermal throttling hay isolation thực. Đưa điều kiện đo vào artifact.

## Bài tập

Chọn cơ chế cho: nhiệt độ 1 Hz; camera 30 fps cùng host; lệnh yêu cầu seat position có feedback; telemetry lên fleet qua mạng chập chờn. Viết lựa chọn, tradeoff, failure behavior và phép đo để xác minh.
