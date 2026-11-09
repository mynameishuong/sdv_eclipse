# 03 — VSS và Eclipse KUKSA: từ bit đến dữ liệu có nghĩa

## 1. Vì sao cần signal model?

Hai xe có thể truyền tốc độ ở hai CAN ID, vị trí bit và scale khác nhau. Nếu app trực tiếp decode cả hai, mỗi thay đổi phần cứng đều lan vào app. Ta đặt một adapter/provider ở biên: nguồn riêng của xe → signal contract chung → app.

Ví dụ quy ước riêng của lab: raw CAN speed `6000`, scale `0.01 km/h` → `Vehicle.Speed = 60.0 km/h`. Khi đổi frame layout, sửa provider và mapping; app vẫn đọc cùng đường dẫn.

## 2. VSS là gì và không bao gồm gì?

VSS của COVESA định nghĩa cách mô tả signal và catalog. Một signal có path, type, datatype, description và có thể có unit/min/max/allowed. Branch tổ chức cây; sensor biểu diễn giá trị quan sát; actuator biểu diễn khả năng nhận yêu cầu tác động; attribute mô tả thuộc tính. VSS không tự biết byte CAN, không tự chạy server và không tự cấp quyền. Xem [VSS introduction](https://covesa.github.io/vehicle_signal_specification/introduction/), [rules](https://covesa.github.io/vehicle_signal_specification/rule_set/).

Contract của project:

| Path | Datatype | Unit | Nguồn |
| --- | --- | --- | --- |
| `Vehicle.Speed` | float | km/h | Chọn từ VSS 6.1 |
| `Vehicle.Powertrain.TractionBattery.StateOfCharge.Current` | float | percent | Chọn từ VSS 6.1, physical SOC |
| `Vehicle.Lab.BatteryTemperature` | float | celsius | Extension của project |
| `Vehicle.Lab.AdvisoryMode` | string | không có | Derived sensor, extension của project |

`Vehicle.Lab.*` được tạo cho giáo trình, **không phải đường dẫn chuẩn của COVESA**. Nhiệt độ đại diện cho cả pack là lựa chọn mô phỏng; một xe thật có thể có nhiều sensor/cell/module và yêu cầu aggregate khác. File `config/vss.json` là cây JSON tối giản nạp trực tiếp vào broker, không phải toàn bộ VSS catalog.

## 3. KUKSA thêm runtime

Databroker đăng ký signal metadata, cung cấp API đọc/publish/subscribe và cơ chế quyền truy cập. Provider hiểu nguồn dữ liệu; broker quản lý abstraction; app hiểu nghiệp vụ. Broker không tự sinh dữ liệu từ xe. Xem [KUKSA architecture](https://github.com/eclipse-kuksa/kuksa-databroker/blob/0.7.1/doc/system-architecture.md).

Trong baseline, dữ liệu được lưu và truy cập qua gRPC `kuksa.val.v2`. Đây không phải kho lịch sử cho fleet; muốn replay/history cần recorder hoặc backend riêng.

## 4. API v2 và ranh giới với ví dụ v1

| Việc cần làm | API v2 của lab | Ý nghĩa |
| --- | --- | --- |
| Đọc một/nhiều signal | `GetValue` / `GetValues` | Giá trị hiện được biết, có thể chưa có value |
| Đăng ký nhận cập nhật | `Subscribe` | Stream cập nhật, phải quản lý cache và timeout |
| Publish chậm | `PublishValue` | Provider gửi observed/derived value |
| Provider stream | `OpenProviderStream` | Nhánh nâng cao cho publishing/actuation |
| Yêu cầu tác động | `Actuate` / `BatchActuate` | Gửi yêu cầu tới provider của actuator |
| Xem metadata | `ListMetadata` | Xác minh path/type/entry type |

v1 có khái niệm current/target value. v2 dùng data value và luồng actuation riêng; không sao chép `set_target_values()` của SDK v1 rồi xem đó là tương đương API v2. Upstream cũng phân biệt các API cũ và mới: [protocol comparison](https://github.com/eclipse-kuksa/kuksa-databroker/blob/0.7.1/doc/protocol.md).

Trong lab chỉ dùng `PublishValue` ở tần số thấp 1 Hz để code dễ đọc. Khi tăng tốc độ hoặc cung cấp actuator, phải học provider stream và ownership đúng contract. Proto được khóa theo submodule broker 0.7.1, không lấy ngẫu nhiên file trên `main`.

## 5. Timestamp quan trọng ngang value

```text
Provider gửi: value=47, source_timestamp=10:00:00
App đọc lại: 10:00:05, broker vẫn trả 47
Tuổi nguồn: 5 giây → input quá hạn → UNKNOWN
```

Timestamp là phần riêng trong protobuf Datapoint. Giá trị 0, không có value và không có timestamp là ba trường hợp khác nhau. `decode()` giữ các trường hợp thiếu thành `None`; policy không biến chúng thành số 0.

Lab từ chối input quá 3 giây, timestamp tương lai quá 0,5 giây và bộ input lệch nhau quá 0,5 giây. Đây là kiểm tra coherence đơn giản. Các lần publish riêng lẻ vẫn không tạo atomic snapshot: khi đổi sang pipeline tốc độ cao, cần correlation/sequence/epoch hoặc thiết kế snapshot phù hợp.

NTP/PTP hỗ trợ đồng bộ clock nhưng phải đo sai số. Monotonic clock thích hợp cho timer nội bộ; wall clock dùng để so sánh timestamp giữa process chỉ khi có giả định clock rõ ràng.

## 6. Command accepted khác physical state

Giả sử app muốn quạt 60%. Một API trả success có thể chỉ xác nhận yêu cầu đã đi tới provider hoặc được chấp nhận. Để biết quạt đang quay, phải đọc feedback RPM/current và timeout theo yêu cầu. App cần phân biệt `requested`, `accepted`, `observed` và `failed`.

Project xuất `AdvisoryMode` dưới dạng sensor vì nó là kết quả quan sát/tính toán. Không đặt nó là actuator chỉ vì app đang publish. Contract v2 có mô tả riêng về actuation/provider: [proto được dùng](https://github.com/eclipse-kuksa/kuksa-proto/blob/28bf76ae57085dad425eedd95bc7bd442e1314a7/kuksa/val/v2/val.proto).

## Bài tập

Thêm một extension `Vehicle.Lab.InputQuality` rồi xác định datatype, allowed values, owner và test. Thay đổi schema, transport và test đồng bộ. Sau đó giải thích vì sao “broker trả giá trị” chưa đồng nghĩa “data có chất lượng tốt”.
