# Official same-node results

Accepted numeric evidence: [20261010-v4110-dev](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/README.md). Frozen suite `24671011425ef8bd0b9f05adb1c87682e9ca33b7`; source-built Nift v4.11.0 development snapshot `635996b7ff5c725c81ac8ef57b1d146f7ceda642`. GNU Make 4.4.1, Ninja 1.13.2, Ubuntu G++ 13.3.0 and GNU ld/ar 2.42 on one fresh shared 4-vCPU/8-GB Ubuntu 24.04 node.

The bounded 17-graph plan contains 291 cells and 9,348 retained observations including warmups. Native light sizes 100/1,000/5,000/10,000; heavy 100/1,000; tiny independent actions 100/1,000/10,000. Worker comparisons use 1/2/4 at fixed profiles/sizes. There are 100 no-op, 20 modest native incremental, 50 tiny leaf, 5–10 multi-second and 3 expensive full-build samples, with exact per-cell counts in the frozen plan. This is not a full Cartesian matrix.

## Representative medians

Milliseconds, except RSS in MiB. Participant order is Make / Ninja / Nift.

| Workload | Make ms | Ninja ms | Nift ms | n per system |
| --- | ---: | ---: | ---: | ---: |
| 10k light no-op | 669.667 | 179.837 | 1,278.913 | 100 |
| 10k light leaf | 2,235.871 | 1,659.979 | 2,959.917 | 20 |
| 10k light full | 63,976.579 | 66,028.577 | 69,612.512 | 3 |
| 1k heavy full / j4 | 16,207.376 | 16,643.082 | 17,631.333 | 5 |
| 10k independent actions full | 5,038.916 | 7,384.457 | 13,315.922 | 5 |

Ninja has the smallest large-native no-op and one-leaf medians here. Make has the lowest 10k light full-build and tiny fully-dirty medians. Full compiler work narrows the elapsed-time differences; these are descriptive results, not significance or universal ranking claims. Nift expresses the graph through supported tracked actions but pays more dependency-checking/dispatch overhead in these cases.

Every accepted observation passes the exact action-set and output-hash oracle; baseline compiler include closure is audited. The native DAG has N+15 actions: generation, N leaf objects, two other objects, ten deterministic archives and one executable. A named Nift target is forced; only dirty-module work is compared, followed by an untimed checked full build. Deleted-input failure is correctness evidence, not performance: Make/Ninja stop before dispatch; Nift's failed compile blocks archive/link. Independent tiny actions are an orchestration microbenchmark, not C++ throughput.

At 10k light full/j4, CPU medians are 231.147 / 239.760 / 258.563 seconds and maximum-child RSS is 469.988 / 469.867 / 469.988 MiB. Linux wait4 RSS is a high-water maximum across children, never a sum of simultaneously resident processes. At 5k no-op/j4, wall medians are 269.004 / 91.679 / 648.167 ms and CPU 268.618 / 91.451 / 2,120.372 ms.

All tails remain. Eight low-sample cells have a range above 25% of their median; eight higher-sample cells contain maxima over four times the median. Action traces remain correct. CPU below wall is consistent with off-CPU waiting but cannot distinguish I/O from shared-host scheduling. No outliers are deleted, and p95/p99 only appear at supported sample counts. Both provisional encoding attempts are separately rejected, never pooled.

[Independent audit](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/provenance/canonical-independent-audit.json), [variance review](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/variance-review.json), [core handover](https://github.com/nift-experiments/lab-evidence/blob/75c1588149a295702ec4006e25efc7ba4f05394f/benchmarks/build-systems/20261010-v4110-dev/CORE-HANDOVER.md). The bounded accepted strace diagnostic finds substantially more Nift metadata calls; it supplies profiling leads, not a hot-function or nonlinear-complexity proof. No Nift core files were edited by this campaign.
