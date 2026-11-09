# 15 — Test, đo đạc và debug có bằng chứng

## 1. Test level khác nhau trả lời câu khác nhau

| Level | Trong project | Chứng minh được | Chưa chứng minh được |
| --- | --- | --- | --- |
| Pure unit | `test_policy.py` | Rule/freshness/hysteresis theo input chỉ định | Broker, network, target |
| Decoder unit | `test_can_frame.py` | Byte layout, endian, signedness và reject cases | CAN driver/bus điện |
| Transport fixture | `test_transport.py` | Generated v2 messages qua gRPC loopback | KUKSA thật có cùng behavior |
| Broker contract | `tests.smoke_live` | API/schema thực của broker được pin | Toàn bộ runtime và physical target |
| End-to-end | Compose + scenario/fault | Các component ghép hoạt động | Deadline/safety trên xe |
| Target/HIL | Bài capstone | Behavior trên platform/hardware đã ghi rõ | Mọi cấu hình/xe khác |

Không đổi nhãn “fixture pass” thành “KUKSA integration pass”. Khi môi trường thiếu Docker, ghi SKIPPED/NOT RUN và nguyên nhân cụ thể.

## 2. Test matrix tối thiểu

| Tình huống | Kỳ vọng | Evidence |
| --- | --- | --- |
| Input hợp lệ, nhiệt độ 30 | NORMAL | Rule test + log |
| 45/55°C và ngưỡng hồi phục | WARN/CRITICAL theo hysteresis | Boundary sequence test |
| Missing/None/NaN/Inf/bool | UNKNOWN | Data validity test |
| Data cũ >3 s | UNKNOWN | Timestamp test + dừng provider |
| Timestamp tương lai/lệch nhau | UNKNOWN | Coherence test |
| Path/type/range sai | Broker reject | Real broker smoke |
| Broker mất | Log UNKNOWN, retry, exit/restart | Process log + supervisor state |
| Advisor chết | Output dừng đổi timestamp | Consumer freshness check |
| CAN duplicate/gap | Drop duplicate/log gap theo helper | Bench log + decoder test |
| Reboot target | Stack trở lại theo yêu cầu | Boot log + functional check |

Mỗi test phải chỉ ra requirement và expected behavior trước khi nhìn kết quả. Một log “không crash” chưa chứng minh output đúng.

## 3. Debug theo đường dữ liệu

1. **Nguồn:** có sample mới/counter tiến không? Scenario có đúng không?
2. **Adapter:** ID/DLC/endian/scale/quality có đúng không?
3. **Broker metadata:** path/datatype/unit và API version đúng chưa?
4. **RPC:** endpoint/DNS, deadline, status code và permission?
5. **App:** giá trị và source timestamp nào được tính?
6. **Consumer:** có kiểm tra output timestamp không?
7. **Lifecycle:** process chết/restart, image và config thực đang chạy là gì?

Đừng sửa threshold để che lỗi CAN scale. Ví dụ raw 470 đáng ra là 47°C nhưng được publish 470°C thì phải sửa mapping, không tăng CRITICAL threshold lên 550°C.

## 4. Các lỗi thường gặp

| Triệu chứng | Kiểm tra đầu tiên |
| --- | --- |
| `ModuleNotFoundError: kuksa` | Đã generate proto bằng đúng venv chưa? |
| `UNAVAILABLE` | Broker chạy chưa, endpoint ở host hay container? |
| `UNIMPLEMENTED` | Có đang gọi sai API version/endpoint không? |
| `NOT_FOUND` | Schema đang mount thực có path đó không? |
| `INVALID_ARGUMENT` | Datatype, range, allowed values |
| `PERMISSION_DENIED` | Token/policy scope của principal |
| RPC OK nhưng UNKNOWN | Timestamp/missing/quality/coherence trong reason |
| Advisor Running nhưng không có data | Provider, schema, source freshness |
| Ankaios không tìm image | Rootful/rootless image storage và agent context |
| vcan lỗi trên Windows | Chạy Linux interpreter và kernel có module |

## 5. Lệnh quan sát

```text
docker compose ps
docker compose logs --tail 100 broker provider advisor
docker stats
```

Trên Linux: `ss -lntp` xem listener, `ip -details link show vcan0` xem interface, `candump vcan0` nếu có can-utils, `journalctl -u ank-agent` xem agent service. Chỉ packet capture khi cần kiểm tra traffic cụ thể; TLS làm payload không đọc như plaintext và đó là hành vi mong đợi.

## 6. Performance và reliability

Đo CPU, RSS, startup time, RPC latency và output age dưới các mức tải. Tách benchmark latency của RPC khỏi end-to-end sensor→decision latency. Trong lab polling 1 Hz, chu kỳ polling tự thêm độ trễ đến gần một chu kỳ; không gọi đây là hard real-time.

Soak test cần thời gian/mức tải, disk/log growth và tiêu chí fail. Fault injection gồm dừng provider, restart broker, kill app, đổi clock trong môi trường thử phù hợp và hạn chế CPU/RAM. Chỉ kết luận cho target/config đã đo.

## Bài tập

Dùng [mẫu nhật ký](../notes/lab-journal.md), chọn một fault, dự đoán output, chạy và lưu evidence. Kết quả tốt phải chỉ ra root cause, assumption và giới hạn của phép thử, kể cả khi test fail.
