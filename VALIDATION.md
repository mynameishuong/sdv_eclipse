# Trạng thái kiểm chứng

Ngày chuẩn bị: **09/11/2026**. Local host: Windows, Python 3.12. Không tìm thấy Docker trong PATH; lệnh kiểm tra WSL chưa trả về môi trường distro hoạt động. Không tự cài system runtime hay reboot máy.

## Đã kiểm tra cục bộ

| Hạng mục | Kết quả |
| --- | --- |
| Cài dependencies trong `project/.venv` | Thành công, versions pin trong requirements |
| Generate protobuf từ upstream files được pin | Thành công, VAL v2 |
| Policy, decoder CAN và transport | Tổng cộng 9 test cases pass; mỗi case còn có subcases |
| Policy và invalid/freshness/hysteresis | Unit tests pass |
| CAN private frame decode | Unit tests pass; không thay thế vcan/physical CAN |
| gRPC serialization qua TCP loopback | Pass với test fixture nhỏ trong `test_transport.py` |
| Offline demo | NORMAL → WARN → CRITICAL → NORMAL → UNKNOWN |
| Dependency consistency | `pip check` pass |
| YAML và schema | Parse Compose/Ankaios, parse nested runtimeConfig, đối chiếu CSV/JSON và proto SHA-256 |
| Tài liệu | Kiểm tra local Markdown links, HTML anchors/files và duplicate IDs |
| HTML reader | Đã mở bằng Chrome headless, kiểm tra ảnh chụp desktop ở `artifacts/reader-preview.png` |
| Upstream versions | Đối chiếu GitHub releases/repository metadata; kiểm tra OCI index digest từ GHCR |

Kết quả tự động chi tiết ở [artifacts/validation.json](artifacts/validation.json); stdout/stderr từng bước nằm cùng thư mục. Test fixture dùng network/gRPC thật giữa client và server chạy trên các thread trong cùng process, nhưng server fixture **không phải Eclipse KUKSA**.

## Chưa chạy trong phiên chuẩn bị này

- `docker compose config`, pull/start thực tế, Dockerfile build và smoke với **KUKSA Databroker thật**.
- Workflow CI trên runner Linux thật.
- SocketCAN/vcan và physical CAN bench.
- Ankaios server/agent/Podman lifecycle và restart/update thực tế.
- ARM board, Leda/Yocto build, target resource/timing/soak tests.
- S-CORE docs build/reference integration example.
- TLS/JWT/ACL, cloud connector và OTA end-to-end; những phần này là backlog nâng cấp, chưa implement trong baseline.

Các cấu hình deployment là kết quả chuẩn bị để review/chạy tiếp, không được ghi nhận là runtime pass. `smoke_live.py` có thể phát hiện các vấn đề compatibility/schema chưa lộ trong fixture.

## Chạy lại kiểm chứng cục bộ

Từ `SDV_Eclipse` trong PowerShell sau khi đã setup venv:

```powershell
.\project\.venv\Scripts\python.exe tools\build_reader.py
.\project\.venv\Scripts\python.exe tools\verify.py
```

Linux thay interpreter bằng `./project/.venv/bin/python`. Script verify ghi kết quả local và **không tự chạy broker smoke hay Linux runtime labs**. Báo cáo NOT RUN của script tương ứng phiên kiểm chứng cục bộ; thêm bằng chứng runtime riêng khi đã chạy.

## Thứ tự xác minh trên môi trường đủ điều kiện

1. `docker compose config`, build, start broker.
2. Khi provider/advisor đang dừng: `python -m tests.smoke_live` bằng Python đã generate proto.
3. Chạy cả stack, kiểm tra scenarios, stale input và broker failure/recovery.
4. Linux vcan, rồi Ankaios, rồi target tests theo chương tương ứng.
5. Ghi target/config/artifact digest và raw logs vào [nhật ký](notes/lab-journal.md).
