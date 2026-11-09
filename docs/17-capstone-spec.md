# 17 — Đặc tả capstone: từ lab đến prototype thực tế

## 1. Mục tiêu và phạm vi

Xây **Vehicle Thermal Advisory Gateway** trên một Linux target: nhận dữ liệu từ ECU mô phỏng hoặc bench CAN đã định nghĩa, cung cấp vehicle abstraction qua KUKSA, chạy app advisory, quản lý workload, quan sát và cập nhật có kiểm soát.

Prototype tiếp cận thực tế bằng integration, lifecycle và test evidence. Nó không nhận trách nhiệm BMS protection/control loop, không tự chứng minh functional safety và không tác động phanh/lái/powertrain thật.

## 2. Architecture triển khai đề xuất

```text
Bench ECU / virtual CAN
   │ private DBC or verified bench network description
   ▼
Linux target: CAN driver → provider → KUKSA → advisory → observer
                                      │               │
                                      └── connector ──┴── offline queue → backend

systemd → container runtime → Ankaios server/agent → workload lifecycle
CI → signed/versioned artifacts → release decision → local deployment
```

Chọn target sau khi xác định CPU/RAM, OS/BSP, CAN interface, container support và recovery method. Raspberry Pi có thể là lựa chọn học tập nếu driver/runtime phù hợp; chưa chọn cụ thể board nào cho mọi yêu cầu automotive.

## 3. Yêu cầu chức năng và trạng thái hiện tại

| ID | Yêu cầu | Acceptance criterion | Baseline |
| --- | --- | --- | --- |
| FR-01 | Normalize speed/SOC/temp | Đúng path, type, unit, range và timestamp semantics | Code + schema có |
| FR-02 | Advisory rule | Đúng thresholds, hysteresis, precedence | Unit test đã chạy |
| FR-03 | Invalid/stale → UNKNOWN | Missing/NaN/old/future/incoherent bị phát hiện | Unit test đã chạy |
| FR-04 | Broker contract | Version/API/schema/negative cases đúng | Smoke có, cần broker thật |
| FR-05 | CAN ingestion | Decode, validity, counter policy đúng | Decoder test; vcan pending |
| FR-06 | Restart/recovery | Crash app và broker restart rồi functional health phục hồi | Manifest có; runtime pending |
| FR-07 | Output freshness | Observer không tin output đã cũ | Thiết kế; cần implement observer guard |
| FR-08 | Telemetry offline | Queue bounded, TTL, duplicate handling | Chưa implement |
| FR-09 | Access control | Provider/app/observer đúng matrix, negative tests pass | Chưa implement |
| FR-10 | Controlled update | Deploy digest mới, verify health, rollback có evidence | Kế hoạch + CI mẫu |

`watch` trong baseline chỉ in sample/timestamp, chưa phải observer guard của FR-07. Đây là việc phải bổ sung trước khi downstream tự quyết định dựa trên mode.

## 4. Yêu cầu phi chức năng tham khảo cho prototype

| ID | Mục tiêu ban đầu | Cách đo |
| --- | --- | --- |
| NFR-01 | Source publish nominal 1 Hz | Counter/timestamp log trong 10 phút |
| NFR-02 | Input >3 s không được coi fresh | Dừng nguồn, đo UNKNOWN và timer resolution |
| NFR-03 | Advisor emit UNKNOWN không quá 1,5 s sau khi tuổi input vượt 3 s khi broker healthy và RPC nhanh | End-to-end log trên target dưới tải quy định |
| NFR-04 | Process restart/reconnect có giới hạn | Kill/crash/restart có log timestamps |
| NFR-05 | Queue/log/storage có giới hạn | Soak 2 giờ đầu, nâng 24 giờ khi mốc trước pass |
| NFR-06 | CPU/RAM nằm trong budget target | Đặt budget sau baseline measurement, thử overload |
| NFR-07 | Release tái xác định được | Manifest source/schema/image/proto/OS hashes |

NFR-03 là **mục tiêu cần đo**, không phải guarantee hiện tại: RPC có timeout 2 giây và ba publish riêng lẻ có thể làm vòng lặp lâu hơn. Muốn bảo đảm budget phải điều chỉnh thiết kế và kiểm chứng worst case, không chỉ sửa văn bản.

## 5. Interface contracts phải bàn giao

- Signal contract: path, semantics, datatype, unit, range, publisher/consumer, sample rate, timestamp và missing/quality behavior.
- CAN contract: ID, DLC, endian, scale, offset, counter/CRC/validity, ECU restart và timeout.
- Process contract: arguments/env, startup readiness, exit codes, shutdown/retry và permissions.
- Deployment contract: node/agent names, runtime context, image digest, mounts, network và resource budget.
- Release contract: versions/compatibility, health gates, rollback, persistent data migration.

Mỗi contract phải có version và owner. Đổi scale hay unit là interface change, không phải chỉnh implementation nội bộ vô hại.

## 6. Backlog triển khai theo thứ tự

1. **P0 — Baseline thực:** setup Linux engine, real broker smoke, Compose scenarios và stale behavior; lưu output.
2. **P1 — Observer guard:** kiểm tra output age, broker reconnect và UNKNOWN reason; test downstream không dùng NORMAL cũ.
3. **P2 — CAN bench:** vcan, mapping/counter cases, sau đó verified physical bench; ghi rõ timestamp limitation.
4. **P3 — Supervision:** Ankaios trên target, crash/reboot/recovery, log rotation và tài nguyên.
5. **P4 — Secure boundary:** TLS/token/policy adapters và negative tests theo matrix.
6. **P5 — Delivery:** CI thật, image digests, SBOM/signature verification, staged deployment và rollback.
7. **P6 — Fleet:** connector bounded queue, timestamps, duplicate/out-of-order và offline recovery.
8. **P7 — Core study:** một S-CORE example và ADR đánh giá bridge/integration boundary khi có use case phù hợp.

## 7. Bộ test nghiệm thu

Nominal và thresholds; missing/bad type/out-of-range; stale source/output; ECU counter reset; broker unavailable; network reconnect; advisor kill/restart; resource pressure; clock skew; unauthorized access; invalid update; rollback; storage full/log quota; boot recovery.

Không cần chạy lại toàn bộ test cho mỗi thay đổi tài liệu. Chọn impact-based regression; khi thay data contract/runtime/target thì mở rộng kiểm tra tương ứng.

## 8. Dossier cuối project

```text
requirements + traceability
architecture: physical / logical / deployment + ADRs
source + dependency manifest + schema/mapping
build instructions + target/BSP config
test plans/results + fault/measurement evidence
security boundaries + permission matrix
release manifest + update/rollback report
known limitations + maintenance backlog
```

Tiêu chí hoàn thành prototype: một người khác theo tài liệu dựng lại được môi trường, chạy nominal/fault scenarios, chỉ ra artifact thực đang chạy và khôi phục được sau lỗi đã quy định.
