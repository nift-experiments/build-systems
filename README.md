# Build systems

GNU Make vs Ninja vs Nift as native-code build orchestrators. One canonical generated corpus, equivalent toolchain actions, exact rebuilt-set oracles, and retained observations. This experiment is allowed to show any participant losing.

Status: canonical native/tiny-action generators and local correctness/feasibility gates passed. Official same-node measurement is next. See the [local ledger](docs/LOCAL-CERTIFICATION.md). No official measurements, cloud node or Labs report yet.

See [methodology](docs/METHODOLOGY.md), [capability audit](docs/NIFT-CAPABILITIES.md) and [handover](HANDOVER.md). Canonical published evidence belongs in `nift-experiments/lab-evidence/benchmarks/build-systems/<series>/`. Local exploratory results stay separate. Existing evidence is immutable.

Implementation lives in `generators/`, `implementations/` and `scripts/`; `corpus/` holds compact manifest descriptions, not redundant generated trees. Disposable fixture trees belong in ignored `work/`.

## Run the frozen protocol

```sh
python3 scripts/certify.py --size 100 --profile light --jobs 4 --results /tmp/local-certification
NIFT_SOURCE_SHA=635996b7ff5c725c81ac8ef57b1d146f7ceda642 python3 scripts/campaign.py --plan docs/official-plan.json --output /tmp/official-build-systems --cpus 0,1,2,3
python3 scripts/validate_campaign.py /tmp/official-build-systems --official
python3 scripts/summarize.py /tmp/official-build-systems
```

Use the actual available CPU IDs and frozen source-built Nift, not merely the environment variable. Publication requires all documented gates and machine/toolchain provenance. Existing campaign directories are never overwritten.
