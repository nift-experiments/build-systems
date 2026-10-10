# Fairness contract — draft before timings

## Common work

One deterministic generator produces sources, graph manifest and Make/Ninja/Nift definitions. Initial native sizes: 100, 1,000, 5,000 and 10,000 translation units. Ten modules (or a documented proportional grouping), leaf-private headers, module headers, a shared global header, two tracked generated outputs, static archives and one executable. Lightweight and compiler-dominated profiles share topology. Compiler/linker flags and logical relative paths are identical. Response files avoid command-length disadvantages; archives use deterministic mode.

Make is nonrecursive with compiler depfiles. Ninja uses ordinary depfile edges. Nift uses tracked custom actions, explicit ordering and file invalidation. A common action wrapper records executed action identities and invokes the same underlying tool; it must not schedule actions or detect dirtiness. Tiny-action microbenchmarks use a separately labeled deterministic action graph and do not stand in for C++ throughput.

All oracles must verify generation, compilation, archive and link sets and final behavior. Exact output hashes are preferred; no normalization without a documented reason. Include-closure parity is checked against compiler depfiles. Correctness failures invalidate a case while preserving its observations.

## Scenarios

Clean full; warm no-op; leaf source edit; private header edit; module fan-out; shared-header fan-out; generated input edit; ten-source batch; 10% source batch; dirty targeted module; relink-only; clean then rebuild. Extra certification covers unrelated edits, deleted and renamed inputs. Mutations change bytes, not merely timestamps. Explicitly establish newer timestamps for timestamp-based participants without timing that preparation.

Workers: 1, 2 and 4, with the same allowed CPU set and maximum worker count. Targeted cases start with the same dirty closure because Nift forces a named target. Clean/full and clean-then-rebuild boundaries are explicitly distinct: the former times build only; the latter also times a common cleanup operation if that case is retained.

## Measurements

Restore fixture, apply mutation and validate preconditions outside timing; time the build command including graph load; check outputs and action traces afterwards. Preserve warmups, failures and every measured sample. No outlier deletion. Deterministic participant rotation and scenario rotation reduce temporal drift. CPU affinity is shared; worker limits are not silently unlimited.

Local feasibility selects bounded sample counts before official collection: at least 50–100 no-op/tiny cases, 20–30 modest incremental, 5–10 multi-second, 3–5 expensive full builds only if defensible variance. Retain wall time, CPU time, peak child-resource scope and action counts. Do not label maximum-child RSS as summed concurrent memory. Do not publish p99 from a handful of samples.

Clean output trees are not cold machines. Filesystem caches remain uncontrolled unless a separately documented fresh-node boundary applies. Fixture/source generation, installation and mutation are excluded from build timings.

## Gates and publication

No cloud resources before all local correctness gates and duration estimates pass. No core modifications. Capability failures stop the campaign with reproducible evidence. Official evidence uses frozen source, suite and toolchain identities on one inexpensive node. Existing Labs report designs/data stay untouched. Balanced workload-specific conclusions, exact tables beside graphs, no aggregate fastest-system badge. Teardown follows live publication/evidence verification.
