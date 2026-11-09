# Third-party source and schema provenance

## KUKSA protobuf contracts

Files `proto/kuksa/val/v2/types.proto` and `val.proto` are unmodified upstream files from:

- Repository: https://github.com/eclipse-kuksa/kuksa-proto
- Commit: `28bf76ae57085dad425eedd95bc7bd442e1314a7`
- This is the `proto` git submodule commit of `eclipse-kuksa/kuksa-databroker` tag `0.7.1`.
- File headers specify Apache-2.0 and copyright Contributors to the Eclipse Foundation.
- SHA-256 `val.proto`: `5d78098dd3a7469f5dc15634a5c47557bf26faa4d01afd9714a0ad1cd5e0f94e`
- SHA-256 `types.proto`: `301f7cd69646506367e449585db51c0351dbbd8ef5f0bfb8ffc781bb3dbe8808`

`proto/LICENSE` contains the Apache 2.0 license from broker tag 0.7.1. `proto/NOTICE.upstream.md` is the broker repository notice retained as additional context; the proto repository at that commit has no separate root NOTICE/LICENSE file. Original file headers are preserved. Generated Python files are produced locally from these contracts.

## Selected COVESA VSS metadata

The `Vehicle.Speed` and `Vehicle.Powertrain.TractionBattery.StateOfCharge.Current` leaf definitions in `config/vss.json` are selected from COVESA VSS v6.1 `vss.json`:

https://github.com/COVESA/vehicle_signal_specification/releases/tag/v6.1

Upstream repository license: MPL-2.0, preserved in `config/VSS_LICENSE`. The surrounding branch descriptions are simplified for this learning lab. `Vehicle.Lab.*` definitions are project-specific additions, not standard VSS catalog signals. The complete corresponding upstream source remains available at the versioned repository link above; the schema file containing these selected definitions is distributed here in readable source form.

## Other references and dependencies

Upstream research documents in `../research/` retain their original content and project ownership. Python packages and container images have their own licenses; this notice does not replace their license information or SBOM. No license is imposed here on the user's new project code by the act of preparing this lab.
