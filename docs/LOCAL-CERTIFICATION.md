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
