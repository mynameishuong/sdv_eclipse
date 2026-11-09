# 16 — Lộ trình từ beginner đến expert

## 1. Đi theo năng lực, không theo số trang đã đọc

Lịch tham khảo là 12–16 tuần, khoảng 6–10 giờ/tuần cho người đã biết lập trình cơ bản. Chưa biết Linux/CAN có thể cần thêm thời gian. “Expert” là định hướng năng lực; không có số tuần nào tự bảo đảm mức chuyên gia.

| Chặng | Đọc | Thực hành | Điều kiện qua chặng |
| --- | --- | --- | --- |
| A — Beginner | 00–02 | Vẽ architecture và chạy offline | Giải thích ECU/signal/service/control plane |
| B — Data/API | 03–06 | Generate proto, tests, broker smoke | Phân biệt value/timestamp, v1/v2, fixture/real |
| C — Integration | 04, 07 | vcan provider, negative data cases | Giải thích byte→unit→path và source freshness |
| D — App engineer | 08, 09 | Container, SDK evaluation, restart | Build artifact và lifecycle có evidence |
| E — Target engineer | 10, 15 | ARM/Linux target, resource/boot tests | Deployment và measurement tái tạo |
| F — Platform engineer | 11, 13 | S-CORE docs/example, isolation design | Requirement→architecture→code/test trace |
| G — Advanced project | 12–17 | Fleet connector, release/rollback, HIL | Chứng minh behavior khi có lỗi |

## 2. Kế hoạch học theo tuần

- **Tuần 1–2:** từ chức năng thermal advisory vẽ ba architecture views; học Linux process/network cơ bản, đọc pure policy.
- **Tuần 3–4:** VSS/KUKSA v2, real broker smoke, subscription, stale data và endpoint debugging.
- **Tuần 5–6:** CAN frame, endian/scale/counter, vcan, mapping vào provider.
- **Tuần 7–8:** đóng gói, lifecycle, Ankaios một node; đánh giá Velocitas bằng compatibility matrix.
- **Tuần 9–10:** triển khai target, tài nguyên, reboot, logging; chọn đường Leda/Yocto nếu cần kiểm soát OS.
- **Tuần 11–12:** S-CORE feature/module, build docs, một reference integration example và traceability.
- **Tuần 13–16:** chọn phần mở rộng capstone, chạy fault/soak/rollback, hoàn thiện project dossier.

Nếu chưa có Docker/Linux, vẫn làm được architecture, offline, policy và gRPC fixture trên Windows. Đánh dấu những lab phụ thuộc kernel/runtime là pending rồi quay lại; không đánh dấu hoàn thành chỉ từ việc đọc lệnh.

## 3. Chọn nhánh chuyên sâu

**Vehicle App engineer:** async/subscription, signal/service model, SDK, error handling, OCI, metrics và contract versioning. Đầu ra: app chạy được trên target, debug được stale/reconnect và có release artifact.

**Core Platform engineer:** Linux/RTOS, IPC/memory, lifecycle/persistency, scheduler, isolation, cross compile và S-CORE. Đầu ra: module/example có traceable requirement, measured behavior và integration assumptions.

**Vehicle Integration/Test engineer:** CAN/Ethernet, DBC, diagnostics, clocking, SIL/HIL, fault injection và CI. Đầu ra: mapping được kiểm thử, test rig và evidence đủ tái hiện lỗi.

**Connected Vehicle engineer:** device identity, telemetry, offline queue, digital twin, fleet operations và OTA policy. Đầu ra: connector chịu offline/duplicate và rollout/rollback có audit.

## 4. Cách đọc source hiệu quả

Mỗi repository, tìm theo thứ tự: README của tag → build/dependency manifest → public API → example nhỏ → test tương ứng → implementation → issue/ADR liên quan. Ghi version ngay khi bắt đầu. Đừng chỉ đọc `main` rồi chạy binary từ release cũ.

Với mỗi lớp tự hỏi: input/output là gì; ownership của data là ai; invariant nào phải giữ; lỗi nào có thể xảy ra; test nào chứng minh behavior đó? Năm câu này dùng được từ Python app tới core middleware.

## 5. Cách tự đánh giá mức độ

Bạn đã vượt beginner khi tự chạy lab và giải thích được luồng. Đã ở mức triển khai khi thay nguồn/target, viết contract và xử lý lỗi được. Năng lực expert thể hiện qua lựa chọn/tradeoff có bằng chứng, review thiết kế người khác, root-cause lỗi xuyên nhiều lớp và vận hành version changes lâu dài.

## Bài cuối

Chọn một nhánh chính, một nhánh bổ trợ. Tạo backlog theo [capstone spec](17-capstone-spec.md), mỗi task có acceptance criterion và evidence file. Chỉ đánh dấu Done sau khi người khác chạy lại hoặc review được kết quả.
