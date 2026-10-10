# Local certification ledger

These authoring runs are correctness/feasibility observations, **not official performance evidence**. They are not pooled and do not establish headline comparisons. Local caches, background work and CPU placement are uncontrolled.

- `local-cp3-100-light-j4`: initial harness failure from comparing a sorted trace with an unsorted expected list. Compiler work succeeded; this is a rejected oracle implementation, not a Make failure.
- `local-cp3b-100-light-j4`: 42 records passed across Make/Ninja/Nift. Native output hashes matched across systems per scenario; action sets matched for normal cases. Early generated hook error codes used a reserved prefix; failure exit/blocked descendants were correct, but later hooks use the valid `user.*` prefix.
- `local-cp4-1000-heavy-j4`: 42 records passed under the earlier profile/Make encoding. This authoring series predates the final depfile audit, rename handling and Make implicit-rule suppression.
- `local-cp4b-100-heavy-j4`: rejected rename setup because GNU Make's existing depfile still mentioned the old source name. The revised definition migration removes the affected object and obsolete depfile for all participants, outside build timing.
- `local-cp4c-100-heavy-j4`: rename setup attempted to remove Ninja's already-consumed depfile. The corrected cleanup tolerates an absent file. Existing records are retained; this setup failure is not a participant performance result.
- `local-cp5-100-heavy-j4`: 45 records passed: initial plus 14 scenarios per participant, including rename and deleted input. Compiler/Ninja-discovered include closures match every declared object input. Cross-participant generated files, objects, archives and executable hashes match for each successful scenario.

The competent Make encoding disables implicit built-in rules/variables and clears suffix rules because every action is explicitly supplied. The pre-correction Make observations must not be mixed with that method.

Deletion behavior legitimately differs: Make/Ninja reject the missing source before dispatch; Nift attempts its affected compile, which fails, and blocks the archive/link descendants. The failure oracle requires nonzero status and permits only that failed compile action. It does not require identical diagnostic exit codes or failure action counts.

The common `scripts/measure.c` supervisor is copied unchanged from the existing shell benchmark convention: timing starts just before fork/exec and ends after wait4. CPU time includes reaped descendants; Linux peak RSS is the wait4 maximum-child scope, **not aggregate simultaneous memory**. It will be used for controlled smoke and official observations after correctness certification.

Large-size runs, tiny-action certification, controlled worker checks, timing calibration and bounded diagnostics remain gates before provisioning. No cloud machine has been created and Nift core remains unchanged.

## Final generator and measurement gate

- `local-cp6-5000-light-j4`: all 45 records pass under the final light graph.
- `local-cp8-tiny100-j4`, `local-cp8-tiny1000-j2`, `local-cp8-tiny10000-j4`: all 18 records each pass. Tiny graphs are independent actions, not a native-code proxy.
- `local-cp10-final-heavy1000-j4`: all 45 records pass. The final heavy profile instantiates sixteen independent depth-128 templates per translation unit; earlier heavy profiles are diagnostic authoring runs only.
- `local-cp12-final-light1000-j2`, `local-cp12-final-heavy100-j1`: all 45 records each pass.
- `local-cp9b-rotated-smoke`: 216 observations pass their action/output oracles, but clean-rebuild pre-cleaned its output tree incorrectly. Retained as rejected boundary diagnostics, not official data.
- `local-cp11-corrected-smoke`: 216 observations pass with cleanup inside timing, at workers 1/2/4 for native and tiny graphs.

Official sampling is bounded rather than a complete Cartesian product: all native scenarios at 100/1,000 light, large 5,000/10,000 light no-op/leaf/full/global scaling, heavy 100/1,000 no-op/leaf/full/global at workers 1/2/4, and tiny 100/1,000/10,000. Worker comparisons explicitly use the same size/profile. No-op has 100 samples, ordinary increments 20, multi-second work 5–10, large builds 3; all warmups remain. Large-build spread must be disclosed rather than asserting confidence from three samples.

- `local-cp7-10000-light-j4`: all 45 records pass, including every native mutation and input-failure scenario.
- `local-cp13-final-harness-smoke`: all 54 rotated observations pass, including the final content-addressed definitions/oracles, mutation timestamp checks, and untimed targeted-build full followups. Workers 1/2/4 are explicitly checked.

- `local-cp14-heavy1000-j1` and `local-cp14-heavy1000-j2`: all 15 records each pass for initial/no-op/leaf/full/global, completing fixed-size worker certification.
- `local-cp15-metadata-rotation-smoke`: all 24 retained observations pass the final toolchain inventory, preconditions and graph-index scenario rotation.

Local gate accepted before provisioning: native sizes 100/1,000/5,000/10,000, final light/heavy profiles, worker limits 1/2/4, tiny sizes 100/1,000/10,000, exact include/action/output oracles, targeted followup and clean/rebuild boundary. Source patch tree reconstruction is verified. Runtime estimate and bounded syscall handover are committed. Official measurements remain a separate same-node cohort.

## CP16 — native-input-only comparator encoding

The first cloud run at suite `354899b` is rejected because it unnecessarily attached Nift content JSON markers to Make/Ninja edges. The corrected shared renderer keeps all real native inputs, commands and graph actions unchanged; representation metadata remains specific to each system.

Fresh complete correctness: `local-cp16-corrected-encoding-native100` and `local-cp16-corrected-encoding-heavy100` pass 45 records each, including full/global/generated and all failure/migration cases; `local-cp16-corrected-encoding-tiny100` passes 18 records.

Baseline-preserving encoding regression: native 1,000 light / j2, 5,000 and 10,000 light / j4, and 1,000 heavy / j4 each pass 30 records; tiny 1,000 / j2 and 10,000 / j4 each pass 15. The helper verifies identical action manifests and canonical input bytes, audits every object’s compiler include closure, requires zero actions after reencoding an already-built baseline, then replays sparse edits, native medium fan-out/targets/relinks/rename/deletion/unrelated inputs and tiny batch edits. Prior full/global/generated correctness remains applicable to unchanged native inputs; fresh 100-item matrices recheck those dirty paths. A helper initially looked for a newer workspace directory spelling; it now also recognizes the legacy ignored baseline path. No participant failure was involved.

The independent read-only audit checks exact rotation order and recomputes distribution statistics using Python’s inclusive quantiles. It is a publication check, not part of any timed command.
