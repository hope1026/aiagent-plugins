# Bundle Transitions

Read only for replacement or consolidation of existing approved bundles.

## Current-state Replacement and Consolidation

Use this subflow only when one or more `approved` or `implemented` sources must move to one new semantic bundle path so active sources contain current facts rather than completed migration history. It authorizes one-to-one replacement or a coordinated many-to-one `merged` consolidation. It does not authorize retirement without a target, split, incremental merge into a target already present in the baseline, partial source removal, or a same-diff transition chain.

1. Write and present the complete replacement as a Spec Delta before touching the current source. Keep it outside the final bundle path. Preserve completed execution details in a plan, ADR, or evidence file.
2. Obtain explicit approval. Then use the forge writing-plans skill to record every exact source path and baseline bundle SHA-256, the one new target bundle path, evidence path, reference updates, and release boundary.
3. Commit the approved Execution Plan and durable evidence first. Record the expected clean HEAD and a fingerprint of its HEAD, index, tracked, and untracked bytes. A dirty root blocks candidate creation; do not clean, stash, or overwrite user work.
4. Create a registered isolated Git worktree detached at the expected HEAD. Perform all supersession mutations there, never in the production root.
5. In that worktree, append to `docs/specs/.bundle-transitions.json`, choose exactly one transition shape, and apply it atomically:
   - One baseline to one new target: append one `superseded` record.
   - Two or more baselines to one new target: append one coordinated `merged` record per baseline in the same candidate diff. Every record uses the exact baseline hash, one shared `toBundlePath`, and one shared `evidencePath`.
   Promote the replacement, remove every authorized source, update active relations and Markdown links, and preserve evidence. The transition uses `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, and `reason`, never a document identifier.
6. Run baseline validation against the expected HEAD and exact expected-byte checks. Create one candidate commit only after every gate passes.
7. On any validation, expected-byte, or commit failure, discard the candidate worktree and prove that the production fingerprint is unchanged. When the user did not explicitly request a Visual Docs, the Visual Docs output count stays exactly zero.
8. Immediately before promotion, require the production root to remain at the expected clean HEAD with the exact recorded fingerprint. Apply only the verified candidate commit with a fast-forward operation. Any HEAD or byte drift refuses promotion without modifying the root.

The transition manifest is durable audit data, but the replacement bundle remains the active source of truth. Existing transition records stay in canonical order as an exact prefix; a prior record never authorizes another deletion. A `merged` group must contain at least two exact active baseline sources and cannot be extended after the target becomes part of a baseline.

