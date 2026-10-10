# Bounded build-orchestration diagnostic handover

No Nift core files were changed. Capability baseline: `635996b7ff5c725c81ac8ef57b1d146f7ceda642`, local v4.10.0 executable SHA recorded in `local-toolchain.json`.

## Local no-op, 5,000 translation units

The certified lightweight graph has 5,015 tracked actions and no dirty outputs. Each participant executed zero actions during `strace -f -c`. Reports are in `investigation/local-noop5000/`. Tracing elapsed times are instrumentation-distorted and **must not be treated as benchmark measurements**.

Observed Linux syscall counts:

| System | newfstatat | openat | read |
| --- | ---: | ---: | ---: |
| GNU Make | 25,065 | 5,036 | 10,487 |
| Ninja | 20,056 | 8 | 214 |
| Nift | 365,666 | 20,077 | 10,038 |

Nift performs substantially more metadata queries in this fixture. This supports investigating repeated path containment/existence checks and per-item state/sidecar loading, but the count alone does not identify a specific source function or prove nonlinear complexity. Profile the clean graph load/dirty-check path separately in the core workspace before proposing changes. Check sparse, fan-in/out and deep graphs too; this fixture is a layered native build, not all possible DAG shapes.

The comparison intentionally retains each participant's real state format: Make includes compiler depfiles, Ninja reads its dependency database, Nift uses tracked metadata and explicit file sidecars. A hidden replacement scheduler or shared bespoke dirty checker would defeat this experiment. Any optimization campaign must preserve invalidation, containment, failure blocking and recovery contracts and use its own authorization and certification.

Official timing and resource results are still pending; this is a diagnostic lead, not a portable performance claim.
