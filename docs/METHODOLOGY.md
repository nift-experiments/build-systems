# Fairness contract

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

## Bounded official matrix

`docs/official-plan.json` is the exact predeclared plan. Every native workload is measured at 100/1,000 light; 5,000/10,000 retain no-op, leaf, full and global-header scaling. Heavy 100/1,000 provide full/leaf/no-op worker comparisons (100 also global-header). Tiny graphs use 100/1,000/10,000 independent actions. Worker study is 1/2/4 at fixed profiles/sizes, not a claimed full Cartesian product. Three-sample large full-build spread is shown explicitly; no p95/p99 is inferred there. Optional 25k/50k cases are omitted to bound runtime.

## Frozen source provenance

The local v4.10.0 probe binary is not asserted to have been compiled from the later source checkout. Official Nift is rebuilt from tree `dc590bbb28b745d9005807af0d42f8e134860209`, commit `635996b7ff5c725c81ac8ef57b1d146f7ceda642`, reporting v4.11.0 development. The commit is initially local; `provenance/nift-frozen.patch` against public `2eaec7d70e9ce2e698d0ba23a605fb9cf85317ff` reconstructs the exact tree (verified with `git write-tree`). No core files are edited. Tool binaries, versions, OS/kernel/CPU/memory/filesystem and source/build identity accompany the official observations.

Official Make 4.4.1 and Ninja 1.13.2 are built from upstream releases, with source archive/commit and binary hashes retained. Ubuntu package inventory is supplementary and must not be mistaken for the shadowing `/usr/local/bin` participant binaries. The frozen Nift CLI is source-built before this measurement; Make used to build that CLI is not itself measured. Tiny ten-action increments at 100/1,000 actions receive 20 samples rather than five.

## Encoding correction before accepted collection

The first cloud run (`354899b`) included each Nift content/recipe JSON marker as an extra Make/Ninja file input, despite their generated commands not reading that file. It is rejected performance evidence: this needlessly enlarged their metadata-checking graph. Corrected Make/Ninja edges track the actual native inputs only. Nift retains its required tracked-item content and supported state format as an intrinsic representation cost. Native actions, compiler flags, explicit source/header/output dependencies and action/output oracles are unchanged. Build-definition generation and command/configuration edits remain outside the measured workload; no automatic compiler-flag-edit claim is made. The rejected observations remain separate and are never pooled with the accepted same-node run.
