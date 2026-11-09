# Eclipse SDV — từ beginner đến triển khai project

**Bắt đầu từ kiến trúc SDV, hiểu vai trò từng lớp, rồi tự chạy và mở rộng một hệ thống.** Tài liệu tiếng Việt; giữ tên kỹ thuật tiếng Anh để bạn đọc được source và tài liệu upstream. Ngày đối chiếu nguồn: **09/11/2026**.

Mở **[SÁCH ĐỌC TRÊN TRÌNH DUYỆT](START_HERE.html)** để đọc liền mạch, tìm kiếm nội dung và chuyển chương. Các file Markdown dưới đây là bản gốc để sửa và ghi chú.

## Hiểu đúng “Eclipse platform”

Trong bộ này, “platform” nghĩa là **hệ sinh thái Eclipse Software Defined Vehicle**. Eclipse SDV tập hợp nhiều building block và dự án tích hợp; bạn phải chọn và tích hợp thành platform cho sản phẩm của mình. Eclipse IDE/CDT là công cụ viết code, không phải runtime SDV. Nguồn định nghĩa: [Eclipse SDV](https://eclipsesdv.org/).

Hai hướng học bổ sung nhau:

- **Vehicle application:** VSS → KUKSA → app → OCI container → Ankaios → embedded Linux. Có code mẫu trong thư mục này.
- **Vehicle core/platform engineering:** E/E architecture → OS và isolation → middleware → S-CORE → integration, timing và quality evidence. Có hướng dẫn build/đọc source và bài tập nâng cao; không tuyên bố đã tích hợp S-CORE vào demo KUKSA.

## Thứ tự đọc

| Chương | Nội dung | Kết quả bạn cần đạt |
| --- | --- | --- |
| [00](docs/00-foundations.md) | SDV từ số 0 | Giải thích ECU, signal, service, deployment |
| [01](docs/01-sdv-architecture.md) | Kiến trúc SDV từ xe đến cloud | Vẽ được physical/logical/deployment architecture |
| [02](docs/02-eclipse-landscape.md) | Bản đồ Eclipse và toolchain | Chọn đúng dự án cho đúng lớp |
| [03](docs/03-vss-kuksa.md) | VSS và KUKSA VAL v2 | Hiểu schema, timestamp, read/publish/actuate |
| [04](docs/04-communication.md) | CAN, SOME/IP, DDS, Zenoh, iceoryx, uProtocol | Phân biệt semantics, transport và IPC |
| [05](docs/05-setup.md) | Chuẩn bị Windows/Linux | Tạo môi trường và generate protobuf |
| [06](docs/06-project-walkthrough.md) | Project mẫu từ đầu đến cuối | Chạy provider → broker → advisor |
| [07](docs/07-can-integration.md) | Thay simulator bằng SocketCAN | Hiểu mapping CAN/DBC → signal |
| [08](docs/08-velocitas.md) | Velocitas và app engineering | Đọc template, SDK, vehicle model và workflow |
| [09](docs/09-ankaios.md) | Orchestration bằng Ankaios | Hiểu desired state, agent và restart |
| [10](docs/10-leda-yocto-target.md) | Leda, Yocto, deploy target | Phân biệt OS image và app container |
| [11](docs/11-score-core.md) | S-CORE và core platform | Đọc feature/module/integration và build evidence |
| [12](docs/12-cloud-diagnostics.md) | Fleet, digital twin, diagnostics | Thiết kế connector, store-and-forward, DTC |
| [13](docs/13-security-safety.md) | Security, isolation, safety | Xác định trust boundary và giới hạn demo |
| [14](docs/14-ci-cd-ota.md) | CI/CD, supply chain, OTA | Thiết kế release, rollout, rollback |
| [15](docs/15-testing-debugging.md) | Testing, observability, debug | Phân biệt test fixture với broker thật |
| [16](docs/16-learning-roadmap.md) | Lộ trình beginner → expert | Hoàn thành theo năng lực và bằng chứng |
| [17](docs/17-capstone-spec.md) | Đặc tả project thực tế | Từ demo đến prototype trên board/HIL |
| [18](docs/18-glossary-faq.md) | Thuật ngữ và câu hỏi hay nhầm | Đọc được tài liệu upstream |
| [19](docs/19-sources-versions.md) | Nguồn và baseline phiên bản | Kiểm chứng, nâng cấp có kiểm soát |

## Project xuyên suốt: Battery Thermal Advisory

```text
Simulated ECU / SocketCAN provider
          │ Vehicle.Speed, SOC, battery temperature + source timestamp
          ▼
   Eclipse KUKSA Databroker 0.7.1  ◄── schema VSS + project extensions
          │ kuksa.val.v2 / gRPC
          ▼
   Thermal advisory app ──► Vehicle.Lab.AdvisoryMode
          │                NORMAL / WARN / CRITICAL / UNKNOWN
          └── JSON logs → người quan sát / cloud connector tương lai
```

Ứng dụng đưa ra **khuyến nghị mô phỏng**, không điều khiển BMS hay actuator thật. Các ngưỡng nhiệt độ là tham số giảng dạy. Project này giúp học kiến trúc và integration; qualification cho sản phẩm là công việc riêng.

## Chạy ngay, chưa cần Docker

Trong PowerShell, tại thư mục `SDV_Eclipse`:

```powershell
Set-Location .\project
python -m sdv_lab offline
```

Thấy chuỗi `NORMAL → WARN → CRITICAL → NORMAL → UNKNOWN`. Đây là policy chạy trong process; để chạy **Eclipse KUKSA thật**, làm theo [hướng dẫn project](project/README.md).

## Những gì đã chuẩn bị

- Code policy, simulator, KUKSA VAL v2 adapter, subscriber và SocketCAN lab.
- Compose dùng image KUKSA đã khóa digest; upstream proto khóa đúng commit của broker.
- Manifest Ankaios 1.1.0, signal contract, bài tập, project spec và mẫu nhật ký.
- Unit tests, test gRPC qua loopback và smoke test dành cho broker thật.
- [Báo cáo kiểm chứng](VALIDATION.md) ghi rõ kết quả đã chạy và những bước còn cần môi trường Linux/container.

Không cần học hết các dự án trước khi bắt đầu. Hoàn thành chương 00–07 trước; sau đó chọn nhánh app, platform hoặc integration ở chương 16.
# sdv_eclipse
