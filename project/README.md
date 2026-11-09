# Battery Thermal Advisory — Eclipse KUKSA VAL v2 lab

Đọc [kiến trúc và walkthrough](../docs/06-project-walkthrough.md) trước khi mở rộng. Tất cả lệnh dưới đây chạy trong thư mục `project/`.

## 1. Offline, Python 3.12

```text
python -m sdv_lab offline
```

## 2. Setup trên PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\generate_proto.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Linux thay `.\.venv\Scripts\python.exe` bằng `.venv/bin/python`.

## 3. KUKSA thật (cần Docker với Linux containers)

```text
docker compose config
docker compose up -d broker
docker compose logs broker
```

Khi broker sẵn sàng, provider/advisor đang dừng:

```powershell
.\.venv\Scripts\python.exe -m tests.smoke_live
```

Sau khi smoke pass:

```text
docker compose up -d --build
docker compose logs -f advisor
docker compose run --rm advisor watch --broker broker:55555 --seconds 30
```

Để chạy smoke lại sau khi cả stack đã chạy, trước hết `docker compose stop provider advisor` nhằm giữ một writer. Dừng lab bằng `docker compose down`.

## 4. CLI trên host

```powershell
.\.venv\Scripts\python.exe -m sdv_lab inspect
.\.venv\Scripts\python.exe -m sdv_lab watch --seconds 30
.\.venv\Scripts\python.exe -m sdv_lab provider --scenario normal --iterations 10
.\.venv\Scripts\python.exe -m sdv_lab advisor --iterations 10
```

Hai dòng cuối chạy ở hai terminal; dừng các workload tương ứng trong Compose để tránh writer cạnh tranh. Xem `python -m sdv_lab --help`.

## 5. Baseline và trạng thái

Broker: **0.7.1** khóa OCI index digest trong Compose. Proto: commit **28bf76ae57085dad425eedd95bc7bd442e1314a7**, chính là submodule của broker tag 0.7.1. API: **kuksa.val.v2**. Bản pin Python trong requirements đã được cài và kiểm tra trên Python 3.12 Windows.

`test_transport.py` dùng gRPC fixture tối giản để test serialization/adapter, **không phải broker Eclipse**. `smoke_live.py` gọi broker thật và không chạy tự động trong unit test discovery. [VALIDATION](../VALIDATION.md) ghi rõ bằng chứng và phần chưa chạy.

`Vehicle.Lab.*` là extensions của project. Broker không có auth/TLS trong baseline. App chỉ advisory; mọi threshold là tham số học tập. Third-party notices ở [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md).
