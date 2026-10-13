# Candidate refresh readiness

Candidate: `main` at `7f7e487c47a87e871dfef53345e2b71288008bff`. The local core checkout and its untracked material are excluded. Historical measurements and review documents remain unchanged.

The copied plan is byte-identical to the accepted plan: 17 graph configurations, 97 scenario/configuration cells, 291 participant cells, 8,880 measured observations and 468 warmups (9,348 total). The native graph retains light/heavy compiler work, 100/1,000/5,000/10,000 sizes, 1/2/4 workers; tiny independent-action graphs retain their prior matrix. No adaptive stopping or discarded outliers.

Current pre-refresh suite HEAD: `b0fcbfe830e9766d18591f40049bd2d0d7d99201`; accepted measured suite: `24671011425ef8bd0b9f05adb1c87682e9ca33b7`. Freeze a new suite SHA after these additive readiness files are committed. The runner already accepts absolute `NIFT` and records `NIFT_SOURCE_SHA`, executable hash, actual toolchain and machine inventory.

Retain GNU Make **4.4.1**, Ninja **1.13.2**, and the shared Ubuntu 24.04 compiler/package policy. Ubuntu's default Make/Ninja packages may differ: do not silently use them. Install Make 4.4.1 from its official release source and Ninja 1.13.2 from its official release/source; retain source/download SHA-256, configuration commands and resulting executable hashes. Make must appear first on PATH because the harness does not expose a MAKE override. `NINJA` can be absolute. Record actual G++/ld/ar versions rather than assuming their old patches survived package updates. Old/new results are cross-node trends, not controlled A/B.

## Isolated candidate bootstrap

Run on the dedicated host, from the suite checkout. Do not reuse local work/nift-source symlinks.

```sh
mkdir -p work
 git clone https://github.com/nift-dev/nift.git work/nift-source
 git -C work/nift-source checkout --detach 7f7e487c47a87e871dfef53345e2b71288008bff
 test "$(git -C work/nift-source rev-parse HEAD)" = 7f7e487c47a87e871dfef53345e2b71288008bff
 test -z "$(git -C work/nift-source status --porcelain)"
 make -C work/nift-source -j4
 export NIFT="$PWD/work/nift-source/nift"
 export NIFT_SOURCE_SHA=7f7e487c47a87e871dfef53345e2b71288008bff
 "$NIFT" --version
 sha256sum "$NIFT"
```

Install `build-essential git python3 autoconf automake libtool pkg-config` as needed and retain package inventory. Build with the campaign's shared default release configuration; retain Makefile hash, compiler output and effective flags. CLI default at this candidate is C++17/-O2/pthread; do not substitute a benchmark-specific optimization. Relevant libraries are built/recorded by the shared campaign artifact protocol where needed.

## Correctness and run gates

Use unique output directories; do not overwrite old results. Certification includes exact executed action sets, output/application hashes, compiler include-closure checks, unrelated-input no-op, renaming, deletion/failure and targeted-build follow-up. Certify native light/heavy 1/2/4-worker configurations and tiny graphs before official collection. Larger graph setup/parity is also verified by the official harness before its first timed case.

```sh
python3 scripts/certify.py --size 100 --profile light --jobs 4 --results work/refresh-cert-light100-j4
python3 scripts/certify.py --size 100 --profile heavy --jobs 4 --results work/refresh-cert-heavy100-j4
python3 scripts/certify.py --kind tiny --size 100 --jobs 4 --scenarios noop leaf batch10 batch10pct full --results work/refresh-cert-tiny100-j4
# Repeat native light/heavy and tiny certification with --jobs 1 and 2 and distinct result paths.
python3 scripts/campaign.py --plan docs/refresh-7f7e487-20261013/plan.json --output /opt/results/build-systems-20261013-candidate-7f7e487 --cpus 0,1,2,3
python3 scripts/validate_campaign.py /opt/results/build-systems-20261013-candidate-7f7e487 --official
python3 scripts/audit_campaign.py /opt/results/build-systems-20261013-candidate-7f7e487
python3 scripts/summarize.py /opt/results/build-systems-20261013-candidate-7f7e487
```

CPU IDs must match actual affinity inventory. Native compiler work is unchanged. Worker override/depfile/new targeting capabilities are separate capability probes, not silent baseline adapter changes. Capture targeted no-op metadata/syscall diagnostics after official observations if warranted. Correctness against this candidate is **pending**, not inherited from the historical run.
