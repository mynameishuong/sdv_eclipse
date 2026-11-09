# 14 — CI/CD, supply chain và OTA

## 1. Release là một bộ artifacts

Một release tái tạo được cần source commit, signal schema, generated-contract provenance, dependency versions, image digest, build config và test results. Tag `latest` tiện khi khám phá nhưng không đủ xác định artifact đã kiểm tra.

Demo pin broker bằng OCI index digest và proto commit. App Dockerfile còn dùng base `python:3.12-slim`; requirements chưa có download hashes. Đây là baseline học có một phần pin, chưa phải hermetic/reproducible release đầy đủ.

## 2. Pipeline đề xuất

```text
Review requirements/contract change
  → static checks + pure policy tests
  → generate protobuf from pinned source
  → transport serialization tests
  → real broker integration smoke
  → multiarch image build
  → target tests + SBOM + vulnerability review
  → sign + publish immutable artifacts
  → staged rollout → observe → promote/rollback
```

Xem `project/ci/github-actions.example.yml`: đây là workflow mẫu để chạy tests và real broker smoke trên Linux CI nếu repo được đặt root tại `SDV_Eclipse`. Nó chưa được kích hoạt hay chạy trên tài khoản CI nào.

## 3. Các kiểm tra có ý nghĩa

- Schema change phải đi kèm compatibility review và contract tests.
- Real broker smoke chạy với image đã pin, không thay bằng fixture.
- Test trên ARM target bổ sung cho test x86; emulator không đại diện mọi kernel/driver/timing.
- Báo cáo CVE/SBOM phải có quyết định xử lý; chỉ sinh file chưa hoàn thành risk review.
- CI publish và deployment phải có quyền hạn tối thiểu, secrets được quản lý riêng.

SBOM mô tả thành phần; provenance mô tả artifact được build từ đâu/bằng gì; signature hỗ trợ kiểm tra người/identity ký. Khi verify còn phải kiểm tra identity/issuer/trust policy mong đợi. Nguồn: [SLSA specification](https://slsa.dev/spec/v1.1/), [Cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/).

## 4. App update theo bước

Giả sử release 0.2 chỉ thay rule/bugfix, giữ signal contract:

1. Build image mới, chạy scenario/fault tests và ghi digest.
2. Đánh giá tài nguyên/startup trên target; đặt health criteria trước rollout.
3. Chọn một bench node hoặc cohort nhỏ đủ điều kiện cập nhật.
4. Kiểm tra artifact identity, compatibility và update preconditions.
5. Dừng/chuyển workload theo thiết kế, deploy version mới.
6. Chỉ promote sau khi output đúng, fresh và health ổn định trong cửa sổ yêu cầu.
7. Rollback về **digest đã kiểm tra** nếu gate thất bại; ghi audit.

Ankaios thực thi thay đổi workload desired state; release decision, vehicle preconditions, signatures và fleet policy vẫn cần được xây hoặc tích hợp.

## 5. Schema/data migration làm rollback khó hơn

Nếu app 0.2 đổi unit °C thành K nhưng giữ path cũ, app 0.1 rollback sẽ hiểu sai dữ liệu. Đổi nghĩa dưới cùng path là contract bug. Nếu persistency migration không backward compatible, rollback binary có thể không đọc lại được dữ liệu.

Tách version của app, schema, config/calibration, OS và persistent data. Tạo compatibility matrix, migration plan và rollback boundary rõ ràng. Không xem “container cũ còn trên disk” là bằng chứng rollback hoàn chỉnh.

## 6. OS update

Với thiết kế A/B phù hợp, update inactive slot rồi boot và chỉ mark-good sau health criteria; bootloader/update framework phải có đường phục hồi khi boot lỗi. RAUC có cơ chế bundle/signing/boot integration nhưng partition/boot design của target là trách nhiệm integration: [RAUC basics](https://rauc.readthedocs.io/en/latest/basic.html).

Thử power interruption trong môi trường bench có kế hoạch phục hồi. Artifact tải thành công không chứng minh update chịu lỗi mất nguồn.

## Bài tập

Viết release manifest cho app 0.1.0: source commit, schema hash, broker digest, proto SHA, app digest, target/OS và test report. Thiết kế một rollout gate và một lỗi có chủ đích để chứng minh rollback cùng dữ liệu/config.
