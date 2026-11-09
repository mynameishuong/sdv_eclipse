# 11 — S-CORE: đi vào core software platform

## 1. S-CORE nằm ở đâu?

Eclipse Safe Open Vehicle Core hướng tới core stack cho SDV trên embedded HPC ECU. Hướng này liên quan các dịch vụ nền, integration và engineering evidence để xây platform, khác với việc viết một app đọc signal qua KUKSA. Phạm vi công bố ở [Eclipse project page](https://projects.eclipse.org/projects/automotive.score).

Không có cơ sở để nói demo KUKSA trong giáo trình “đã chạy trên S-CORE”. Muốn nối hai phía, phải chọn deployment target, API boundary, ownership và validation riêng. S-CORE cũng không được mặc định là một Linux distribution, hypervisor hay bản AUTOSAR Adaptive thay thế tương đương.

## 2. Đọc repository theo trách nhiệm

| Điểm bắt đầu | Bạn cần tìm |
| --- | --- |
| [score](https://github.com/eclipse-score/score) | Tài liệu platform, process/method/tooling và entrypoint |
| [reference_integration](https://github.com/eclipse-score/reference_integration) | Các module được ghép, version, build/run examples |
| [communication](https://github.com/eclipse-score/communication) | Communication APIs, bindings, shared-memory support và tests |
| [lifecycle](https://github.com/eclipse-score/lifecycle) | Quản lý vòng đời process/execution theo module design |
| [persistency](https://github.com/eclipse-score/persistency) | Dữ liệu lưu bền và contract khôi phục/lỗi |
| [S-CORE docs](https://eclipse-score.github.io/score/main/) | Handbook, requirements, architecture, modules, releases |

Tên module và maturity có thể thay đổi theo release. Module có tài liệu safety không có nghĩa mọi API, OS, compiler và configuration đã được đánh giá trong use case của bạn.

## 3. Feature, module, binding và integration

Ví dụ communication: feature nói về khả năng trao đổi dữ liệu cần cung cấp; module là phần hiện thực; binding quyết định cơ chế vận chuyển như IPC; integration ghép đúng versions và cấu hình trên target.

Một API frontend ổn định có thể tách khỏi binding cụ thể. Khi đọc, tìm đường đi requirement → architectural decision → component/API → implementation → test. Mục tiêu là hiểu **bảo đảm nào thực sự được cung cấp và dưới assumption nào**, không chỉ tìm một hàm `send()`.

Tham khảo [communication architecture](https://eclipse-score.github.io/reference_integration/main/process_methods_tools/score_platform/features/communication/architecture/index.html). Link `main` dùng để tra cứu; reproducible build phải checkout/tag và lưu manifest dependency.

## 4. Bài đầu: build documentation và đọc traceability

Tag `score v0.7.4` là baseline khảo sát của **repository score**, không suy diễn thành phiên bản đồng bộ của mọi module hay mốc marketing. Chuẩn bị Linux theo [development instructions](https://eclipse-score.github.io/score/main/contribute/development/index.html), đọc `.bazelversion`, `.bazelrc`, `MODULE.bazel` và setup của tag.

```bash
git clone --branch v0.7.4 --depth 1 https://github.com/eclipse-score/score.git score-study
cd score-study
bazel run //:help
bazel run //:docs
```

Các target trên có trong README của tag; cần Bazel/toolchain đúng setup và internet cho dependencies chưa cache. `//:docs` tạo documentation, **không build một vehicle runtime hoàn chỉnh**. Sau đó chọn một requirements/architecture/test chain và ghi lại các ID liên kết.

## 5. Bài tiếp: module và reference integration

Chọn một release/commit của `reference_integration`, đọc dependency manifest và build instructions **trong chính commit đó**. Không tự đổi module lên latest. Chạy một example upstream nhỏ nhất theo instructions; lưu lệnh, stdout/stderr, versions và target.

Đề bài tự phát triển: producer phát thermal status có sequence/timestamp; consumer phát hiện duplicate/stale. Giữ scalar values giống project advisory nhưng dùng API/example communication được release đó hỗ trợ. Chỉ viết bridge sang KUKSA sau khi producer/consumer độc lập đã chạy và semantics được xác định.

## 6. Core services cần suy nghĩ gì?

- **Lifecycle:** startup order, state transition, shutdown deadline và crash recovery.
- **Communication:** ownership buffer, discovery, queue size, ordering và timeout.
- **Persistency:** atomicity theo contract, dữ liệu hỏng, power interruption và schema migration.
- **Health/monitoring:** alive chưa chắc đúng deadline; cần thiết kế phản ứng với quá tải.
- **Execution environment:** OS/toolchain support, memory/CPU budget và isolation assumptions.

Đây là checklist đánh giá kiến trúc của người học, không phải tuyên bố mọi mục đều được mọi module/release implement.

## 7. Ranh giới safety

Chỉ được nói điều đã có evidence: module version, target, compiler, safety manual/assumptions, requirements coverage và test kết quả. Sử dụng C++/Rust, đạt unit test hay có nhãn safety trong docs chưa chứng minh safety cho một chức năng của xe.

## Tiêu chí hoàn thành

Build docs, giải thích một feature/module, chạy một example trong reference integration và truy vết ít nhất một requirement tới test. Kèm một ADR giải thích liệu có cần bridge KUKSA hay app nên dùng service trực tiếp. Không cần nhồi S-CORE vào cùng demo chỉ để có đủ logo.
