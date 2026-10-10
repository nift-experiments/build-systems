# Build systems

GNU Make vs Ninja vs Nift as native-code build orchestrators. One canonical generated corpus, equivalent toolchain actions, exact rebuilt-set oracles, and retained observations. This experiment is allowed to show any participant losing.

Status: canonical native/tiny-action generators implemented; local action and output certification in progress. See the [local ledger](docs/LOCAL-CERTIFICATION.md). No official measurements, cloud node or Labs report yet.

See [methodology](docs/METHODOLOGY.md), [capability audit](docs/NIFT-CAPABILITIES.md) and [handover](HANDOVER.md). Canonical published evidence belongs in `nift-experiments/lab-evidence/benchmarks/build-systems/<series>/`. Local exploratory results stay separate. Existing evidence is immutable.

Implementation lives in `generators/`, `implementations/` and `scripts/`; `corpus/` holds compact manifest descriptions, not redundant generated trees. Disposable fixture trees belong in ignored `work/`.
