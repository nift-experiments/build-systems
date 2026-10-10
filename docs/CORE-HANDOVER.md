# Bounded Nift core handover — accepted build-systems series

No Nift core files were edited by this campaign. Frozen source: `635996b7ff5c725c81ac8ef57b1d146f7ceda642`; suite: `24671011425ef8bd0b9f05adb1c87682e9ca33b7`. Nift is a rebuilt v4.11.0 development snapshot, not an unspecified latest executable. The node uses GNU Make 4.4.1 and Ninja 1.13.2; exact binary/compiler identities are in [identity.json](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/identity.json).

## Measured no-op at 5,000 light translation units / j4

Every official sample executes zero actions. The same warm prepared graph contains 5,015 native actions. All observations, including warmups and long tails, remain. These are timing results from the C supervisor, independent of tracing.

| System | n | Wall median ms | CPU median ms | Maximum-child RSS MiB |
| --- | ---: | ---: | ---: | ---: |
| GNU Make | 100 | 269.004 | 268.618 | 11.625 |
| Ninja | 100 | 91.679 | 91.451 | 13.496 |
| Nift | 100 | 648.167 | 2120.372 | 12.301 |

## Separate syscall diagnostic

After collection, each participant rebuilt and audited an equivalent 5,000-unit fixture. Under `strace -f -c`, all three then executed zero native actions and retained identical output hashes. Tracing elapsed times are distorted and excluded from performance conclusions. Counts below describe this fixture only.

| System | newfstatat | statx | openat | read | execve | clone | clone3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GNU Make | 20050 | 0 | 5008 | 10457 | 1 | 0 | 0 |
| Ninja | 15041 | 0 | 8 | 207 | 1 | 0 | 0 |
| Nift | 365666 | 0 | 20077 | 10038 | 1 | 0 | 8 |

Raw diagnostics: [GNU Make](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/diagnostics/accepted-noop5000/make-strace.txt), [Ninja](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/diagnostics/accepted-noop5000/ninja-strace.txt), [Nift](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/diagnostics/accepted-noop5000/nift-strace.txt). [Correctness receipt](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/diagnostics/accepted-noop5000/validation.json).

## Leads, with limits

Compare metadata queries and per-item state loading with wall/CPU costs. Make reads compiler depfiles, Ninja its dependency database, and Nift tracked metadata plus explicit file sidecars. These supported state formats remain part of the experiment. More metadata calls support profiling path containment/existence checks and repeated state access; they do not identify a specific hot function or prove nonlinear complexity. CPU above elapsed time includes parallel work and merits checking how dependency checks use workers.

Use a focused profile and path-frequency trace in a separately authorized core investigation before changing implementation. Preserve invalidation, containment, prerequisite ordering, failure blocking, recovery and targeted-build contracts. Check other graph shapes before generalizing: this is a layered native DAG plus a separate independent-action graph.

[Variance review](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/variance-review.json) checks large tails against exact action traces and retains every observation. CPU far below wall time is consistent with waiting/off-CPU time but cannot distinguish host scheduling contention from I/O. Shared CPUs and synthetic workloads limit portable claims. Small-sample ranges are descriptive, not confidence intervals. No sample is deleted to improve a result.

Both provisional encodings remain separately rejected diagnostics. Their values are not pooled, and the older local syscall investigation is not substituted for the final encoding's counts.
