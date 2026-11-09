# 19 — Nguồn chính thức, phiên bản và cách cập nhật

## 1. Baseline đã khảo sát ngày 09/11/2026

| Thành phần | Version/identity | Ý nghĩa và bằng chứng |
| --- | --- | --- |
| KUKSA Databroker | 0.7.1, release 26/08/2026 | [Release](https://github.com/eclipse-kuksa/kuksa-databroker/releases/tag/0.7.1); image index đã hỏi GHCR |
| KUKSA OCI index | `sha256:529d8c6d3cc223362667672978bcb8f92c4d356b25aedd336e7a2e004d7279bd` | Pin trong Compose và Ankaios manifest |
| KUKSA proto | `28bf76ae57085dad425eedd95bc7bd442e1314a7` | Submodule `proto` của broker tag 0.7.1 |
| KUKSA API | `kuksa.val.v2` | Proto và code của project |
| COVESA VSS | 6.1, release 17/09/2026 | [Release](https://github.com/COVESA/vehicle_signal_specification/releases/tag/v6.1); chọn 2 standard signals |
| Ankaios | 1.1.0, release 22/10/2026 | [Release](https://github.com/eclipse-ankaios/ankaios/releases/tag/v1.1.0); manifest `apiVersion: v1` |
| S-CORE `score` repository | v0.7.4, release 27/10/2026 | [Release](https://github.com/eclipse-score/score/releases/tag/v0.7.4); không gán version này cho mọi module |
| Velocitas Python SDK | v0.15.7, release 03/07/2025 | [Release](https://github.com/eclipse-velocitas/vehicle-app-python-sdk/releases/tag/v0.15.7); khảo sát, chưa migration |
| Leda | Chọn commit build/layers khi làm target | Docs repository không phải OS release artifact |
| Python | 3.12, Windows trong local validation | Xem `VALIDATION.md` và generated report |
| Python dependencies | grpcio/tools 1.85.1; protobuf 7.36.2 | Đã resolve/install; requirements có pin đầy đủ trực tiếp |

Phiên bản release repository, milestone toàn dự án, docs `main` và release của module là bốn loại thông tin khác nhau. Ví dụ website có thể nói mốc S-CORE 0.9 trong khi `score` repository có tag khác; không tự hợp nhất chúng thành một version. Khi build reference integration, manifest của commit được chọn mới quyết định module versions.

## 2. Kiến trúc và hệ sinh thái

- [Eclipse SDV](https://eclipsesdv.org/) — khái niệm, projects và integration initiatives.
- [Eclipse SDV project portfolio](https://eclipsesdv.org/projects/) — điểm tra cứu hệ sinh thái.
- [SDV Blueprints](https://github.com/eclipse-sdv-blueprints/blueprints) — use-case integration references.
- [Eclipse S-CORE project](https://projects.eclipse.org/projects/automotive.score) — scope chính thức.

## 3. Signal model và KUKSA

- [COVESA VSS docs](https://covesa.github.io/vehicle_signal_specification/) — signal syntax/catalog, license và extension.
- [VSS source 6.1](https://github.com/COVESA/vehicle_signal_specification/tree/v6.1) — source version dùng đối chiếu signal.
- [VSS tooling](https://github.com/COVESA/vss-tools) — parser và format conversion.
- [KUKSA architecture 0.7.1](https://github.com/eclipse-kuksa/kuksa-databroker/blob/0.7.1/doc/system-architecture.md).
- [KUKSA user guide 0.7.1](https://github.com/eclipse-kuksa/kuksa-databroker/blob/0.7.1/doc/user_guide.md).
- [KUKSA protocol comparison 0.7.1](https://github.com/eclipse-kuksa/kuksa-databroker/blob/0.7.1/doc/protocol.md).
- [Pinned VAL v2 proto](https://github.com/eclipse-kuksa/kuksa-proto/tree/28bf76ae57085dad425eedd95bc7bd442e1314a7/kuksa/val/v2).
- [CAN provider](https://github.com/eclipse-kuksa/kuksa-can-provider) — kiểm tra compatibility trước khi tích hợp.

## 4. Middleware và development toolchain

- [SocketCAN — Linux kernel](https://docs.kernel.org/networking/can.html).
- [gRPC Python basics](https://grpc.io/docs/languages/python/basics/) và [core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/).
- [COVESA vsomeip](https://github.com/COVESA/vsomeip) và [CommonAPI core runtime](https://github.com/COVESA/capicxx-core-runtime).
- [Eclipse iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2).
- [Zenoh overview](https://zenoh.io/docs/overview/what-is-zenoh/).
- [uProtocol specifications](https://github.com/eclipse-uprotocol/up-spec).
- [Cyclone DDS](https://github.com/eclipse-cyclonedds/cyclonedds) và [eCAL](https://github.com/eclipse-ecal/ecal).
- [Velocitas concepts](https://eclipse.dev/velocitas/docs/concepts/) và [quickstart](https://eclipse.dev/velocitas/docs/tutorials/quickstart/quickstart/).

## 5. Lifecycle, image và core platform

- [Ankaios architecture v1.1.0](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/architecture.md).
- [Ankaios installation v1.1.0](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/usage/installation.md).
- [Ankaios startup configuration v1.1.0](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/reference/startup-configuration.md).
- [Ankaios inter-workload dependencies v1.1.0](https://github.com/eclipse-ankaios/ankaios/blob/v1.1.0/doc/docs/reference/inter-workload-dependencies.md).
- [Docker startup order](https://docs.docker.com/compose/how-tos/startup-order/).
- [Leda architecture](https://eclipse-leda.github.io/leda/docs/about/architecture/) và [meta-leda](https://github.com/eclipse-leda/meta-leda).
- [Yocto overview](https://docs.yoctoproject.org/overview-manual/yp-intro.html).
- [S-CORE development](https://eclipse-score.github.io/score/main/contribute/development/index.html).
- [S-CORE reference integration](https://github.com/eclipse-score/reference_integration).
- [Communication](https://github.com/eclipse-score/communication), [lifecycle](https://github.com/eclipse-score/lifecycle), [persistency](https://github.com/eclipse-score/persistency).
- [OpenBSW](https://github.com/eclipse-openbsw/openbsw) và [ThreadX](https://github.com/eclipse-threadx/threadx).

## 6. Cloud, diagnostics và delivery

- [Eclipse Mosquitto docs](https://mosquitto.org/documentation/), [Hono concepts](https://eclipse.dev/hono/docs/concepts/), [Ditto overview](https://eclipse.dev/ditto/intro-overview.html).
- [Eclipse Kanto](https://eclipse.dev/kanto/) — phương án edge stack để đánh giá.
- [OpenSOVD](https://github.com/eclipse-opensovd/opensovd).
- [SUMO](https://eclipse.dev/sumo/) — traffic simulation, không thay ECU HIL.
- [RAUC basics](https://rauc.readthedocs.io/en/latest/basic.html).
- [SLSA](https://slsa.dev/spec/v1.1/) và [Cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/).
- [ISO 26262-1:2018](https://www.iso.org/standard/68383.html) và [ISO/SAE 21434:2021](https://www.iso.org/standard/70918.html) — tra thuật ngữ/phạm vi, không thay tiêu chuẩn đầy đủ.

## 7. Evidence lưu trong thư mục

`research/` giữ repository metadata snapshot, một số tài liệu upstream đã đọc, broker OCI manifest và metadata/hash của VSS/proto. Đây là nguồn đối chiếu, không phải dependency runtime. Các lần fetch thất bại cũng có trong log nghiên cứu ban đầu; file URL/version đã chọn cuối cùng mới là baseline dùng trong code.

Nguồn chính thức có thể đổi sau ngày kiểm tra. Khi nâng cấp: chọn version → đọc changelog/proto → update dependency/schema → generate → run unit/real-broker tests → target tests → update manifest/report. Không thay hàng loạt thành `latest`.
