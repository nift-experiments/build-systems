# Build systems

GNU Make vs Ninja vs Nift as native-code build orchestrators. One canonical generated corpus, equivalent toolchain actions, exact rebuilt-set oracles, and retained observations. This experiment is allowed to show any participant losing.

Status: accepted same-node collection and independent audit complete: 9,348 observations, 291 cells, 17 graph configurations. All action/output gates passed. [Canonical evidence](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/README.md) retains every sample and both rejected encodings. Publication and lifecycle receipts follow in that series. See [official results](docs/OFFICIAL-RESULTS.md) and the [local ledger](docs/LOCAL-CERTIFICATION.md).

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
