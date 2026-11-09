# 08 — Velocitas: phát triển Vehicle App theo quy trình

## 1. Vai trò chính xác

Velocitas cung cấp toolchain cho containerized Vehicle Apps: project templates, SDK/model hỗ trợ truy cập vehicle abstraction, môi trường phát triển và workflow build/test/release. Nó giúp chuẩn hóa cách viết và đóng gói app; vehicle runtime và provider vẫn phải được cấu hình riêng. Xem [Velocitas](https://eclipse.dev/velocitas/) và [concepts](https://eclipse.dev/velocitas/docs/concepts/).

Trong lab hiện tại, ta dùng Python gRPC trực tiếp để nhìn rõ API. Khi đã hiểu data path, mới chuyển sang SDK/template để đánh giá giá trị của abstraction và workflow.

## 2. Những phần cần đọc

| Phần | Bạn tìm điều gì? | Artifact |
| --- | --- | --- |
| Vehicle model | Path/type được biểu diễn trong code thế nào | Generated model hoặc bindings |
| SDK | Async/subscription, errors, reconnect, lifecycle | App dùng API typed |
| App manifest | Dependency/permission metadata gì được khai báo | Manifest tương ứng template |
| Dev container | Tool phiên bản nào, broker nào được khởi động | Môi trường dev tái tạo |
| CI workflows | Test, multiarch build, scan, publish | Image và reports |
| Deployment | Image được runtime nào nhận | Deployment specification |

Không giả định một app manifest tự động thực thi ACL. Phải tìm nơi khai báo biến thành policy và nơi policy được runtime kiểm tra.

## 3. Compatibility trước migration

SDK Python release được khảo sát là `v0.15.7` ngày 03/07/2025; đó là release của **SDK repository**, không phải version chung cho mọi thành phần Velocitas. Tham khảo [SDK release](https://github.com/eclipse-velocitas/vehicle-app-python-sdk/releases/tag/v0.15.7).

Đọc `pyproject.toml`, dependencies và transport implementation của tag bạn chọn. Xác định SDK dùng `kuksa.val.v1`, v2 hay adapter nào; so khớp với broker và provider. Bộ này không tuyên bố SDK đó đã tương thích toàn bộ VAL v2 0.7.1.

## 4. Bài migration có thể thực hiện

1. Tạo một thư mục riêng từ template được [quickstart chính thức](https://eclipse.dev/velocitas/docs/tutorials/quickstart/quickstart/) dẫn tới. Ghi commit template và từng dependency.
2. Giữ `Policy` và các test nghiệp vụ. Đây là phần độc lập với SDK.
3. Viết adapter mới chuyển model/SDK value thành `Sample(value, timestamp)`.
4. Tạo test contract xác nhận datatype, missing value, timestamp và stale behavior.
5. Chạy cùng bốn scenario với baseline trực tiếp gRPC; so sánh output và failure behavior.
6. Build image, lưu digest; kiểm tra startup/shutdown/reconnect và tài nguyên trên target.

Nếu SDK không hỗ trợ API v2 bạn cần, chọn một baseline được upstream hỗ trợ để học riêng hoặc viết adapter v2 có kiểm thử. Không âm thầm trộn actuation/current-target semantics khác phiên bản.

## 5. Khi nào nên dùng?

Nếu cả nhóm cần template, typed vehicle model, dev environment và workflow chung, toolchain có thể giảm khác biệt giữa các app. Nếu bạn đang học contract hoặc viết provider đặc thù, gọi gRPC trực tiếp giúp quan sát rõ hơn. Quyết định dựa trên maintenance, API coverage và test evidence.

## Tiêu chí hoàn thành

Trình bày đường đi từ một dòng `read signal` trong app đến RPC thực và từ source đến OCI image. Ghi một bảng compatibility có các cột: template commit, SDK, API, broker, signal model và runtime. Migration chỉ được coi hoàn thành khi cùng requirement và fault cases đã pass.
