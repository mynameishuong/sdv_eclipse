# 06 — Đọc và chạy project từ đầu đến cuối

## 1. Requirement trước code

Prototype nhận ba input: speed, SOC và representative battery temperature. Mỗi input có source timestamp. App xuất một trong bốn trạng thái và log lý do. Không có physical actuation.

| Điều kiện | Kết quả | Vì sao |
| --- | --- | --- |
| Thiếu, không hợp lệ, quá hạn hoặc lệch timestamp | UNKNOWN | Không đủ bằng chứng để kết luận |
| Temperature ≥55°C | CRITICAL | Ngưỡng mô phỏng |
| Đang CRITICAL và temperature ≥52°C | CRITICAL | Hysteresis tránh nhấp nháy |
| Temperature ≥45°C | WARN | Ngưỡng mô phỏng |
| Trước đó WARN/CRITICAL và temperature ≥42°C | WARN | Giảm cảnh báo có hysteresis |
| SOC ≤15% và speed ≥100 km/h | WARN | Rule minh họa dùng nhiều input |
| Các input còn lại hợp lệ | NORMAL | Theo rule của lab |

UNKNOWN xóa trạng thái hysteresis. Các ngưỡng cần requirement/calibration riêng nếu đem ý tưởng vào sản phẩm. Đây không phải thuật toán thermal management/BMS.

## 2. Đọc source theo đúng luồng

| File | Đọc để hiểu |
| --- | --- |
| `config/signals.csv` | Data contract, owner, unit |
| `config/vss.json` | Cây metadata broker nạp khi startup |
| `sdv_lab/policy.py` | Rule, validity, freshness, coherence và hysteresis |
| `sdv_lab/transport.py` | Encode/decode Datapoint, RPC deadline và VAL v2 calls |
| `sdv_lab/__main__.py` | Provider, advisor, watch, offline và retry loop |
| `proto/kuksa/val/v2/*.proto` | Contract thực upstream |
| `Dockerfile`, `compose.yaml` | Packaging, networking và runtime arguments |
| `tests/` | Yêu cầu nào đã có kiểm tra |

`Policy` không import gRPC để giữ nghiệp vụ độc lập. `Broker` là adapter: đổi transport không nên buộc viết lại rule. CLI nối hai phần lại thành một process.

## 3. Bài đầu tiên không cần broker

Chạy ở `project/`:

```text
python -m sdv_lab offline
```

Bạn sẽ thấy năm dòng JSON tương ứng `NORMAL`, `WARN`, `CRITICAL`, `NORMAL`, `UNKNOWN`. Dòng cuối cố tình gán input đã cũ 10 giây. Trường `transport=in-process` giúp phân biệt bài này với KUKSA thật.

## 4. Khởi động KUKSA thật và kiểm tra contract

Sau khi chuẩn bị Python và generate proto, chạy:

```text
docker compose up -d broker
```

Chờ log broker sẵn sàng qua `docker compose logs broker`. Sau đó trên PowerShell:

```powershell
.\.venv\Scripts\python.exe -m tests.smoke_live
```

Trên Linux:

```bash
.venv/bin/python -m tests.smoke_live
```

Chỉ chạy khi provider/advisor đang dừng để không có writer cạnh tranh. Smoke kiểm tra version, publish/read, preservation của source timestamp, policy transitions, invalid path/type/range và subscription initial snapshot. Nếu có lỗi thì xử lý lỗi thật; không thay broker bằng fixture rồi gọi kết quả đó là end-to-end thành công.

## 5. Chạy cả stack

```text
docker compose up -d --build
docker compose logs -f advisor
```

Provider chuyển scenario mỗi 6 tick, mỗi tick khoảng 1 giây khi RPC thành công. Bạn sẽ thấy normal → warn → critical → normal và lặp lại. Có thể có UNKNOWN ngắn lúc startup hoặc chuyển input do ba publish không atomic; xem timestamp và lý do trong log.

Một terminal khác xem bằng subscriber v2:

```text
docker compose run --rm advisor watch --broker broker:55555 --seconds 30
```

Hoặc chạy `python -m sdv_lab watch` bằng venv ở host. CLI `inspect` in server version và các sample hiện có.

## 6. Tiêm lỗi có chủ đích

```text
docker compose stop provider
docker compose logs -f advisor
```

Sau khi input vượt 3 giây, advisor phải publish UNKNOWN. Broker vẫn có thể trả các giá trị cũ, nên thành công của GetValues không đủ chứng minh freshness.

```text
docker compose start provider
docker compose stop broker
```

Khi broker mất, advisor log UNKNOWN cục bộ nhưng không publish được UNKNOWN. Signal output trong broker hoặc ở downstream cache có thể giữ giá trị trước đó; consumer bắt buộc kiểm tra **output timestamp**. Sau 5 lỗi transient liên tiếp, process thoát mã 2; Compose `restart: on-failure` khởi động lại. Khởi động broker lại rồi quan sát phục hồi.

Thử input cũ ngay từ provider: dừng provider chính, chạy `docker compose run --rm provider provider --broker broker:55555 --scenario normal --age 10 --iterations 5`. Advisor phải UNKNOWN. Không chạy đồng thời hai provider cùng path trong bài này.

## 7. Dừng lab

```text
docker compose down
```

Lệnh dừng và xóa các container/network của project Compose này; source và tài liệu vẫn ở thư mục project. Broker state của bài lab không được thiết kế để giữ lịch sử qua restart.

## 8. Giới hạn có chủ đích

Adapter dùng plaintext trên network lab, chưa có TLS/token handling. Retry có số lần giới hạn và interval cố định; production nên có backoff/jitter và shutdown policy rõ ràng. App chưa có metric endpoint, durable queue hay cloud bridge. Provider stream/actuation chưa implement. Những phần này có yêu cầu và bài nâng cấp trong các chương sau.

Tiêu chí hoàn thành: bạn chỉ ra được nguyên nhân mỗi trạng thái, chứng minh stale behavior và phục hồi, đồng thời phân biệt test chạy trên máy với phần cần broker/Linux thực.
