# CP1 capability audit

Inspected Nift source SHA `635996b7ff5c725c81ac8ef57b1d146f7ceda642`, `docs/BUILD-SCRIPTS.md`, `src/ProjectRead.cpp` and `src/ProjectInfo.cpp`; current website Build Scripts, General build systems and User dependencies documentation.

- A tracked item declares one output and requires a content input. Its `build` field points to a project-local native `.f` script replacing rendering/minification. The script must leave a regular tracked output. Successful state is committed after post-build succeeds.
- `depends` names prerequisite tracked items and schedules their completion, including the prerequisite closure for a requested target. Independent ready branches execute concurrently, limited by `build-threads`.
- **Ordering is not invalidation.** Consumers must also declare prerequisite output paths in ordinary `.deps.json` file dependencies. Clean consumers are rechecked after prerequisites complete.
- Source content, selected scripts and explicit file dependencies participate in `modified`, `hash` or `hybrid` incremental modes. The initial comparison uses `modified`, matching Make/Ninja's ordinary timestamp invalidation, with actual content edits and verified timestamp preconditions.
- `nift build <name>` forces the requested target even if clean; prerequisite items can remain clean. Compare targeted **dirty/missing-output** closures, not a warm named-target no-op against Make/Ninja's unforced target behavior. Record forced-target behavior separately if measured.
- There is no declared multi-output tracked item. The canonical generated pipeline will use independently tracked header and source outputs with equivalent actions for all participants, rather than a hidden graph executor.
- Nift does not directly ingest compiler Make-format depfiles. Its explicit input dependencies must match the canonical include closure; audit that closure against compiler-generated `-MMD -MP` depfiles. Unexpected includes are certification failures, not an advantage from incomplete tracking.
- Deleted inputs must fail without committing downstream success; rename tests must update the common manifest and all definitions outside timing. No header discovery/parity claim extends beyond the certified generated corpus.

These contracts appear sufficient for the proposed graph. Local probes must establish actual generated-output invalidation and exact action sets before that conclusion is accepted.
