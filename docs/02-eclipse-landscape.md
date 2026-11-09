# 02 — Bản đồ Eclipse và toàn bộ toolchain liên quan

## 1. Chọn theo bài toán

Đọc bảng này từ yêu cầu sang công cụ. “Thuộc Eclipse Foundation” không tự động có nghĩa “là thành phần bắt buộc của Eclipse SDV”, cũng không bảo đảm mọi dự án đã tương thích với nhau. Đây là danh mục có chọn lọc phục vụ kiến trúc trong giáo trình, không phải liệt kê mọi dự án đang tồn tại.

| Dự án | Làm gì? | Khi dùng | Có chạy trong demo? |
| --- | --- | --- | --- |
| [KUKSA](https://github.com/eclipse-kuksa/kuksa-databroker) | Vehicle signal abstraction/broker | App cần truy cập signal có schema | Có, bằng Compose |
| [Velocitas](https://eclipse.dev/velocitas/) | SDK/template/workflow cho Vehicle App | Chuẩn hóa cách nhóm phát triển app | Nhánh migration |
| [Ankaios](https://github.com/eclipse-ankaios/ankaios) | Orchestrate workload trên embedded nodes | Lifecycle và desired state nhiều workload | Có manifest, cần Linux |
| [Leda](https://eclipse-leda.github.io/leda/) | Recipes/reference distribution cho SDV | Học tích hợp OS và component | Nhánh target image |
| [S-CORE](https://projects.eclipse.org/projects/automotive.score) | Core stack hướng HPC automotive | Core services, quality/process và integration | Nhánh core riêng |
| [SDV Blueprints](https://github.com/eclipse-sdv-blueprints/blueprints) | Các ví dụ tích hợp theo use case | Tham khảo cách ghép thành hệ thống | Tài liệu tham khảo |
| [iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2) | IPC bằng shared memory/zero copy | Truyền dữ liệu lớn giữa process cùng máy | Bài nâng cao |
| [Zenoh](https://zenoh.io/docs/overview/what-is-zenoh/) | Pub/sub/query trên hệ phân tán | Luồng dữ liệu edge/robotics/vehicle | Bài nâng cao |
| [uProtocol](https://github.com/eclipse-uprotocol/up-spec) | Contract giao tiếp và abstraction transport | Thiết kế service giao tiếp xuyên môi trường | Bài nâng cao |
| [Cyclone DDS](https://github.com/eclipse-cyclonedds/cyclonedds) | DDS implementation | Hệ thống data-centric với QoS DDS | Tùy use case |
| [eCAL](https://github.com/eclipse-ecal/ecal) | Middleware/giao tiếp và tooling đo dữ liệu | Prototype, replay, integration | Tùy use case |
| [OpenBSW](https://github.com/eclipse-openbsw/openbsw) | Software platform cho automotive MCU | Node MCU và basic software | Nhánh ECU |
| [ThreadX](https://github.com/eclipse-threadx/threadx) | RTOS cho deeply embedded | Scheduler/timing trên MCU | Nhánh ECU |
| [OpenSOVD](https://github.com/eclipse-opensovd/opensovd) | Service-oriented vehicle diagnostics | Chẩn đoán compute và dịch vụ mới | Thiết kế mở rộng |
| [SUMO](https://eclipse.dev/sumo/) | Mô phỏng giao thông | Scenario fleet/traffic cấp hệ thống | Không thay HIL điện tử |
| [Kanto](https://eclipse.dev/kanto/) | Edge connectivity, container/update services | Chọn stack edge/IoT tích hợp | Phương án khác để đánh giá |
| [Mosquitto](https://mosquitto.org/documentation/) | MQTT broker | Telemetry pub/sub qua MQTT | Nhánh cloud |
| [Hono](https://eclipse.dev/hono/docs/concepts/) | Device connectivity/identity/multitenancy | Backend tiếp nhận nhiều thiết bị | Nhánh cloud |
| [Ditto](https://eclipse.dev/ditto/intro-overview.html) | Digital twin framework | Mô hình trạng thái xe phía backend | Nhánh cloud |

## 2. Công cụ ngoài Eclipse nhưng cần trong toolchain

| Nhóm | Công cụ | Artifact tạo ra |
| --- | --- | --- |
| Signal model | COVESA VSS, vss-tools | `.vspec`, overlay, `vss.json` |
| Vehicle network | SocketCAN, can-utils, DBC tooling | Frame log, DBC, mapping |
| SOME/IP | COVESA vsomeip, CommonAPI C++ | Service interface, proxy/stub, config |
| Build | CMake/Ninja, Cargo, Bazel/Bazelisk | Binary, test results |
| OS image | Yocto/OpenEmbedded, BitBake, BSP | Kernel, rootfs, SDK, image manifest |
| Packaging | OCI image, Docker/Podman/containerd | Image digest, runtime specification |
| CI | GitHub Actions hoặc CI nội bộ | Build/test/release evidence |
| Quality | Compiler warnings, sanitizers, static analysis | Findings và xử lý findings |
| Supply chain | SPDX/CycloneDX, Syft, Trivy, Cosign | SBOM, vulnerability report, signature |
| Debug | gdb, Wireshark, tcpdump, journalctl | Trace và bằng chứng root cause |
| Measurement | perf, tracing, cgroups metrics | CPU/RAM/latency distributions |
| OS update | RAUC hoặc giải pháp phù hợp BSP | Signed bundle, slot state |

VSS và vsomeip thuộc COVESA, không đổi thành Eclipse chỉ vì được dùng trong một project Eclipse. Yocto cũng là hệ sinh thái riêng. Xem [VSS](https://covesa.github.io/vehicle_signal_specification/), [vsomeip](https://github.com/COVESA/vsomeip), [Yocto introduction](https://docs.yoctoproject.org/overview-manual/yp-intro.html).

## 3. Luồng tạo sản phẩm

```text
Requirement + architecture
  → signal/service contracts
  → app + provider source
  → code generation + build
  → unit/contract/integration tests
  → OCI image + SBOM + signature
  → release manifest
  → orchestrator on target
  → logs/metrics/diagnostics
  → staged update + rollback evidence
```

Ở nhánh OS, source và layer configuration đi qua BitBake để tạo image. Ở nhánh core, feature/module source đi qua build và integration của S-CORE. Ba luồng này liên quan nhau nhưng có artifact và release cadence khác nhau.

## 4. Không cài mọi thứ cùng lúc

Baseline học đầu tiên chỉ cần Python. Mốc tiếp theo cần KUKSA và container engine. Chỉ thêm Ankaios khi bạn đã chạy được data plane. Chỉ thêm Yocto khi đã có nhu cầu kiểm soát OS image. Chỉ thêm middleware mới khi bạn chứng minh được yêu cầu mà lựa chọn hiện tại chưa đáp ứng.

Các dự án như Chariott/Ibeji xuất hiện trong tài liệu SDV cũ. Snapshot repository trong `research/repository-snapshot.json` ghi nhận repository chưa archived tại thời điểm kiểm tra, nhưng ngày push gần nhất cũ hơn một số dự án khác. Đó là tín hiệu cần đánh giá maintainer, issue, release và compatibility; không đủ để kết luận dự án đã chết hay production-ready. Vì vậy giáo trình không chọn chúng làm dependency baseline.

## Bài tập

Cho ba yêu cầu: đọc tốc độ xe; restart app sau crash; tạo rootfs cho board ARM64. Chọn một công cụ chính và một artifact kiểm chứng cho từng yêu cầu. Giải thích tại sao không dùng cùng một công cụ cho cả ba.
