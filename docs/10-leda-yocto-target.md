# 10 — Leda, Yocto và triển khai lên thiết bị

## 1. OS image khác application image

OCI image đóng gói user-space của ứng dụng; nó dùng kernel của host. OS image chứa những phần như boot artifacts, kernel, root filesystem và system services tùy thiết kế. Build được container ARM64 chưa có nghĩa board sẽ boot hoặc có CAN driver.

Leda cung cấp recipes/reference distribution để học tích hợp các thành phần SDV trên Linux. Repository `eclipse-leda/leda` chủ yếu là **documentation**, còn `meta-leda` là Yocto/OpenEmbedded layers; không dùng “latest GitHub release” của docs repo làm version OS. Xem [Leda architecture](https://eclipse-leda.github.io/leda/docs/about/architecture/) và [meta-leda](https://github.com/eclipse-leda/meta-leda).

## 2. Các khái niệm Yocto cần biết

| Khái niệm | Nghĩa thực dụng |
| --- | --- |
| BitBake | Công cụ thực thi build tasks theo metadata |
| Recipe `.bb` | Cách fetch/configure/build/install một component |
| Layer | Nhóm recipes/config; thường có dependency giữa layer |
| BSP | Support cho board/SoC: kernel, bootloader, device tree... |
| MACHINE | Chọn target phần cứng |
| DISTRO | Chính sách/cấu hình distribution |
| Image recipe | Chọn nội dung root filesystem/image |
| SDK/sysroot | Toolchain và headers/libs để cross compile |
| sstate/download cache | Tái sử dụng output/tasks và nguồn đã fetch |

Đây là hệ thống build custom Linux; không phải chỉ `apt install` thêm package vào một distro sẵn có. Nguồn: [Yocto overview](https://docs.yoctoproject.org/overview-manual/yp-intro.html).

## 3. Chọn một trong hai đường target

**Đường A — Linux có sẵn trên board:** boot Ubuntu/Debian phù hợp board, kiểm tra kernel/network/container runtime rồi chạy lab. Đường này phù hợp để học app integration trước.

**Đường B — OS do mình build:** chọn board được BSP hỗ trợ, chọn branch Leda/Yocto/layer tương thích rồi tạo image. Lựa chọn branch phải đồng bộ; không ghép layer `main` với release Yocto bất kỳ.

Chỉ có một lệnh `bitbake` tổng quát sẽ không đủ tái tạo vì còn MACHINE, layer revisions và image recipe. Bộ này không đưa tên board/image không được xác minh để tránh lệnh copy-paste sai. Dùng build setup và supported target của commit Leda bạn chọn làm nguồn.

## 4. Quy trình port project lên ARM64

1. Xác nhận board boot ổn định, network/clock/storage và hardware access.
2. Ghi `uname -a`, `/etc/os-release`, `uname -m`, runtime version và free RAM/storage.
3. Build app image cho `linux/arm64` trên CI hoặc native trên board. Với cross build, kiểm tra wheel và binary architecture.
4. Pull broker bằng digest multiarch đã pin; registry có amd64/arm64/riscv64 không có nghĩa mọi distro/kernel đều đã được test.
5. Chạy real broker smoke và policy scenarios trên board.
6. Chạy soak/load/restart tests, đo CPU/RAM và thermal behavior.
7. Thay vcan bằng interface vật lý sau khi driver/mapping đã được xác nhận cho bench.

Nếu dùng Docker, ví dụ build image riêng là `docker buildx build --platform linux/arm64 -t sdv-eclipse-lab:0.1.0 --load .` khi builder hỗ trợ. Native build trên ARM64 cũng được. `--load` cho một platform khác có thể build thành công nhưng không chạy native trên laptop x86 nếu thiếu emulation; luôn xác nhận trên target thật.

## 5. Runtime cần gì?

Ghi yêu cầu kernel/cgroups/namespaces, filesystem mount, user ID, storage quota, log rotation, DNS, firewall và time sync. Với CAN adapter, cần host có interface và quyền truy cập phù hợp. Đừng cấp privileged cho mọi container chỉ để vượt qua một lỗi permission chưa hiểu.

Boot flow nên thể hiện thứ tự: system ready → container runtime → orchestrator → broker/provider → application readiness. Systemd service active và application functional health vẫn là hai khái niệm khác nhau.

## 6. OS update và app update

App update thay OCI artifact và config tương ứng. OS update thay rootfs/kernel/boot artifacts theo thiết kế slot/update framework. RAUC là một lựa chọn image-based update với bundle/signing và boot integration; cần cấu hình phù hợp bootloader/partition của target, không tự xuất hiện khi thêm dependency. Xem [RAUC basics](https://rauc.readthedocs.io/en/latest/basic.html).

Không thực hành flash/partition bằng một lệnh chung cho mọi board. Trong project thật, device target, backup và recovery procedure là phần của deployment plan.

## Tiêu chí hoàn thành

Tạo một target manifest gồm board, BSP, layer commits, MACHINE/DISTRO, kernel config, app/broker digest và test evidence. Chứng minh board restart xong app hoạt động và log không làm đầy storage.
