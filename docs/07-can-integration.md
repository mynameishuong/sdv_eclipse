# 07 — CAN/DBC → provider → VSS → ứng dụng

## 1. Thay đúng một lớp

Mục tiêu là giữ nguyên KUKSA, policy và output; thay nguồn dữ liệu từ simulator bằng CAN adapter. Đây là bài kiểm tra thiết kế: nếu đổi nguồn phải viết lại thuật toán cảnh báo thì ranh giới abstraction đang chưa tốt.

```text
Virtual ECU sender → vcan0 → SocketCAN provider → KUKSA → advisor
```

SocketCAN biểu diễn CAN device như network interface và cung cấp socket API trên Linux. `vcan` giúp thử nghiệm frame mà không cần transceiver. Nó không mô phỏng đầy đủ arbitration, electrical fault hay timing vật lý. Nguồn: [Linux SocketCAN](https://docs.kernel.org/networking/can.html).

## 2. Private frame của bài học

CAN ID 11 bit `0x321`, DLC 8. **Đây là protocol tự đặt của lab, không phải CAN message chuẩn của xe nào.**

| Byte | Field | Encode | Giá trị ví dụ |
| --- | --- | --- | --- |
| 0–1 | Speed | uint16 little endian, ×0.01 km/h | 6000 → 60 km/h |
| 2–3 | Physical SOC | uint16 little endian, ×0.01% | 7000 → 70% |
| 4–5 | Battery temperature | int16 little endian, ×0.1°C | 470 → 47°C |
| 6 | Counter | uint8, wrap 255→0 | 1 |
| 7 | Validity | đúng 1 mới nhận | 1 |

Payload ví dụ: `70 17 58 1B D6 01 01 01`. Bạn phải giải thích được từng byte và vì sao nhiệt độ âm cần signed decode. Linux `can_frame` gồm header và payload 8 byte, tổng 16 byte trong helper này; không được gửi trực tiếp 8 byte rồi mong socket tự hiểu arbitration ID.

File [lab.dbc](../project/config/lab.dbc) mô tả cùng layout để mở bằng DBC tooling. Các field `Counter` và `Validity` phục vụ adapter; không map trực tiếp thành standard VSS signals. Decoder hiện viết tay để thấy byte-level behavior, không parse DBC tự động.

## 3. Tạo vcan trên Linux

Trong một Linux host/VM có module vcan:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set dev vcan0 up
ip -details link show vcan0
```

Nếu `vcan0` đã tồn tại, bỏ bước add và kiểm tra nó đúng interface lab. Nếu kernel WSL không có vcan thì dùng Linux VM/host có hỗ trợ; không sửa code để giả vờ có CAN thật.

## 4. Chạy ba terminal

Đầu tiên chỉ giữ KUKSA broker, dừng simulator/advisor trong Compose:

```text
docker compose up -d broker
docker compose stop provider advisor
```

Chạy trong `project/` bằng Python Linux đã setup:

```bash
# Terminal 1: adapter
.venv/bin/python -m scripts.can_provider --interface vcan0
```

```bash
# Terminal 2: advisor
.venv/bin/python -m sdv_lab advisor
```

```bash
# Terminal 3: nguồn frame ảo, nhiệt độ gây WARN
.venv/bin/python -m scripts.can_sender --temperature 47 --count 30
```

Sender được giới hạn vào `vcan0` để lệnh thực hành có endpoint rõ ràng. Kết quả mong đợi là WARN khi input hợp lệ, rồi UNKNOWN sau khi sender dừng và timeout vượt 3 giây. Nếu adapter và Docker ở hai host khác nhau, cấu hình network/authorization phù hợp thay vì mặc định `127.0.0.1` trỏ sang host kia.

## 5. Từ helper đến provider thực tế

Adapter hiện kiểm tra ID/DLC/validity/range, loại duplicate counter liền kề và log gap/reset. Nó gán timestamp **lúc nhận ở gateway**, chưa có timestamp từ ECU. Nó không có CRC/E2E protection, timeout output quality riêng hay state machine tái đồng bộ counter. Khi broker lỗi adapter thoát; supervisor chịu trách nhiệm restart.

Trong dự án thực, DBC/ARXML và network description phải là nguồn mapping có version. Có thể đánh giá [KUKSA CAN Provider](https://github.com/eclipse-kuksa/kuksa-can-provider), nhưng phải kiểm tra API version/dependency trước khi ghép với VAL v2 baseline. Không đổi CAN ID, unit và bit layout bằng phỏng đoán.

Những thông tin phải bổ sung: multiplexing, endian, signedness, invalid raw values, timeout từng signal, counter reset sau ECU boot, checksum và mapping giữa ECU clock/gateway clock. Tránh đưa mẫu invalid vào broker như một giá trị đo mới hợp lệ.

## Bài tập và tiêu chí hoàn thành

Gửi temperature âm, gap counter và validity=0; ghi nhận adapter reject/accept ra sao. Viết decoder test cho một frame bị sai DLC. Hoàn thành khi bạn chỉ ra được phần đã kiểm tra bằng unit test và phần cần chạy SocketCAN/physical CAN để chứng minh.
