# 09 — Ankaios: lifecycle và orchestration trên xe

## 1. Tại sao cần orchestrator?

Ba process chạy bằng tay phù hợp khi học. Khi có nhiều workload, bạn cần một nơi mô tả app nào chạy ở node nào, dependency gì và làm gì sau crash. Đó là bài toán lifecycle/control plane.

Ankaios có server giữ desired state và agent chạy trên node thực thi; CLI `ank` xem và thay đổi state. Agent giao tiếp runtime như Podman/containerd. Server không tự chạy workload nên node chứa server vẫn cần agent nếu muốn chạy app tại đó. Xem [architecture v1.1.0](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/architecture.md).

## 2. Ba trạng thái cần phân biệt

- **Desired state:** “advisor image X cần chạy ở agent_A”.
- **Execution state:** runtime/agent báo workload đang running, failed hay pending.
- **Functional health:** advisor có nhận input mới và xuất kết quả đúng hay không.

Container Running không bảo đảm gRPC sẵn sàng, signal đã có dữ liệu hay policy đúng. Vì vậy code vẫn có deadline, freshness và lỗi kết nối. Compose `depends_on` cũng không tự đợi readiness khi chỉ dùng thứ tự startup: [Docker startup order](https://docs.docker.com/compose/how-tos/startup-order/).

## 3. Baseline manifest

File `project/config/ankaios.yaml` dành cho **Ankaios 1.1.0**, `apiVersion: v1`. Đừng lấy manifest `v0.1` trong bài cũ rồi trộn với binary mới.

```yaml
apiVersion: v1
workloads:
  advisor:
    agent: agent_A
    runtime: podman
    restartPolicy: ALWAYS
    dependencies:
      kuksa: ADD_COND_RUNNING
    runtimeConfig: |
      image: localhost/sdv-eclipse-lab:0.1.0
      commandOptions: ["--network", "host"]
      commandArgs: ["advisor", "--broker", "127.0.0.1:55555"]
```

`runtimeConfig` là **string chứa YAML khác**, nên phải đọc hai tầng. `commandOptions` là options của `podman run`; `commandArgs` là arguments cho command/entrypoint trong container. Nguồn: [startup configuration](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/reference/startup-configuration.md).

## 4. Thực hành một node Linux

Chuẩn bị Linux + Podman. Tải installer từ [release v1.1.0](https://github.com/eclipse-ankaios/ankaios/releases/tag/v1.1.0), đọc script và dùng tùy chọn version theo [installation](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/usage/installation.md). Chọn một user context thống nhất cho `ank-agent`, `ank` và Podman. Cài service mặc định có thể chạy root; rootless image store sẽ không tự chia sẻ với rootful service.

Từ `project/`, build app image bằng **cùng Podman context với agent**:

```bash
podman build -t localhost/sdv-eclipse-lab:0.1.0 .
sudo install -d /opt/sdv-eclipse-lab/config
sudo install -m 0644 config/vss.json /opt/sdv-eclipse-lab/config/vss.json
```

Lệnh `sudo` ở trên chỉ tạo config đọc được ở đường dẫn cố định. Nếu agent là root, hãy build/load image ở rootful Podman context tương ứng. Kiểm tra agent name là `agent_A` trong cấu hình agent. Dừng Compose trước để tránh broker khác giữ cổng 55555.

Sau khi server và agent hoạt động, dùng CLI cùng cấu hình kết nối/quyền của installation:

```bash
ank apply config/ankaios.yaml
ank get workloads
ank get state
```

Nếu installation yêu cầu quyền root, chạy CLI trong context tương ứng. Với cấu hình systemd mặc định, xem `journalctl -u ank-server -u ank-agent`. Xác nhận tên container bằng `podman ps`, rồi xem log thực; tên workload không nhất thiết là tên container runtime.

## 5. Vì sao dùng host network trong manifest này?

Đây là lựa chọn đơn giản cho **một node Linux**: broker bind `127.0.0.1`, app dùng cùng host namespace. Đây không phải manifest multi-node. Khi chuyển node, localhost không còn dùng được để nối giữa các node; phải thiết kế routing, DNS/address, firewall, identity/TLS và ACL.

Dependencies chỉ quản lý thứ tự và điều kiện lifecycle; không tạo mạng hay đảm bảo functional health. Không để cả Ankaios và một supervisor khác cùng giành quyền restart một workload mà chưa xác định ownership.

## 6. Thử crash và update

Kill container advisor của lab, quan sát restart policy. Dừng provider, quan sát workload advisor có thể vẫn Running nhưng output UNKNOWN. Thay image version, theo dõi desired/execution state và log app. Rollback phải trả về artifact đã biết cùng config/schema phù hợp; không chỉ đổi tên tag.

## Tiêu chí hoàn thành

Bạn giải thích được toàn bộ manifest, phân biệt running/healthy, chứng minh restart và recovery. YAML đã được parse cục bộ trong bộ tài liệu; lifecycle thực của Ankaios vẫn cần thực hiện trên Linux, ghi vào nhật ký và lưu log.
