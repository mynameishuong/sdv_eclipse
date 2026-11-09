# 05 — Chuẩn bị môi trường trên Windows và Linux

## 1. Ba mức môi trường

| Mức | Cần có | Chạy được |
| --- | --- | --- |
| A | Python 3.12 | Offline policy, không cần dependencies |
| B | Python + dependencies | Policy tests, protobuf, gRPC fixture qua loopback |
| C | Linux containers qua Docker/Podman | Eclipse KUKSA thật và end-to-end demo |

SocketCAN và Ankaios lab dùng Linux. Trên Windows có thể dùng Linux VM, máy Linux khác hoặc WSL2 phù hợp. Chỉ có file `wsl.exe` không có nghĩa đã có distro dùng được. Kiểm tra `wsl --list --verbose`.

Ngày chuẩn bị bộ này: Python 3.12 có sẵn; không tìm thấy `docker` trong PATH và WSL chưa cung cấp distro hoạt động qua lệnh kiểm tra. Bộ tài liệu không tự cài hypervisor, reboot hoặc thay cấu hình Windows.

## 2. PowerShell: tạo môi trường Python

Mở PowerShell tại `SDV_Eclipse`:

```powershell
Set-Location .\project
python -m sdv_lab offline
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts\generate_proto.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Không cần activate venv nên không cần sửa execution policy. Bước generate đọc proto đã đi kèm project, không fetch `main`. Output trong `project/kuksa/` là code sinh tự động, không sửa tay.

## 3. Linux: cùng workflow

Chạy từ `project/`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/generate_proto.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m sdv_lab offline
```

Nếu Ubuntu thiếu module venv, cài gói `python3-venv` bằng package manager của distro. Tránh vừa dùng Python global vừa dùng dependency trong venv khác.

## 4. Chuẩn bị container engine

Trên Windows, cài Docker Desktop với backend Linux containers theo [hướng dẫn chính thức](https://docs.docker.com/desktop/setup/install/windows-install/). Trên Linux, dùng [Docker Engine](https://docs.docker.com/engine/install/) hoặc Podman cho nhánh Ankaios. Kiểm tra:

```text
docker version
docker compose version
```

Có client nhưng không kết nối được daemon thì chưa sẵn sàng. `compose.yaml` dùng DNS nội bộ `broker`, không dựa vào host networking trên Windows. Host truy cập `127.0.0.1:55555`; app trong container truy cập `broker:55555`.

## 5. Kiểm tra trước khi chạy thật

```text
docker compose config
docker compose pull broker
docker compose build
docker compose up -d broker
```

`config` kiểm tra Compose syntax và nội suy; không chứng minh broker chấp nhận schema. `pull` xác minh truy cập registry/platform; không chứng minh app compatible. Smoke test ở chương 06 mới kiểm tra API thực tế.

Nếu có nhiều project chiếm cổng 55555, đổi **host port** ở mapping và dùng `--broker 127.0.0.1:<port>` khi chạy app từ host. App trong Compose vẫn dùng port 55555 của broker.

## 6. Quy tắc thư mục và môi trường

- Code/document ở OneDrive đọc bình thường; build Linux lớn nên đặt trên filesystem Linux để giảm overhead và tránh locking/sync.
- Dockerfile dùng Python 3.12 slim; base tag còn có thể đổi digest. Muốn tái tạo release đầy đủ phải pin thêm base digest, OS packages và dependency hashes.
- Requirements được pin để tái tạo bài lab, không phải cam kết các phiên bản sẽ luôn là bản mới nhất sau ngày kiểm tra.
- Không cần Eclipse IDE để chạy lab. VS Code, Eclipse CDT hoặc terminal đều có thể dùng; chọn theo ngôn ngữ và workflow của nhóm.

## Tiêu chí hoàn thành

Bạn chạy được offline policy và unit tests, giải thích được Python interpreter nào đang dùng, file code nào được generate và vì sao `localhost` trong container là một namespace khác.
