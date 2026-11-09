# Bundle Transitions

Read only for replacement or consolidation of existing approved bundles.

## Current-state Replacement and Consolidation

Use this subflow only when one or more `approved` or `implemented` sources must move to one new semantic bundle path so active sources contain current facts rather than completed migration history. It authorizes one-to-one replacement or a coordinated many-to-one `merged` consolidation. It does not authorize retirement without a target, split, incremental merge into a target already present in the baseline, partial source removal, or a same-diff transition chain.

1. Write and present the complete replacement as a Spec Delta before touching the current source. Keep it outside the final bundle path. Preserve completed execution details in a plan, ADR, or evidence file.
2. Confirm that concrete user authorization covers the exact replacement meaning and effects; reuse it when already given. Record source paths and baseline bundle SHA-256 values, the new target path, evidence path, reference updates, and application boundary in the existing plan or work record. A separate plan/evidence commit is not a prerequisite.
3. Identify the baseline commit and confirm that the relevant approved source bytes match it. Record the original checkout's HEAD, index, and user-file state needed to establish preservation. Unrelated uncommitted work does not block isolated candidate preparation. If relevant sources differ from the baseline, reconcile the intended baseline first without discarding user changes.
4. Create a registered isolated Git worktree at that baseline. Perform supersession mutations there and preserve the original checkout. Do not clean, stash, or overwrite user work to prepare the candidate.
5. In that worktree, append to `docs/specs/.bundle-transitions.json`, choose exactly one transition shape, and apply it atomically:
   - One baseline to one new target: append one `superseded` record.
   - Two or more baselines to one new target: append one coordinated `merged` record per baseline in the same candidate diff. Every record uses the exact baseline hash, one shared `toBundlePath`, and one shared `evidencePath`.
   Promote the replacement, remove every authorized source, update active relations and Markdown links, and preserve evidence. The transition uses `fromSourcePath`, `fromSourceSha256`, `disposition`, `toBundlePath`, `evidencePath`, and `reason`, never a document identifier.
6. Run baseline validation against the recorded commit and verify the exact candidate diff, source hashes, and preservation of the original checkout. Keep the candidate available for review without a commit; create a candidate commit only when committing is authorized and all gates pass.
7. On failure, leave the original checkout unchanged, report the failed condition, and correct or safely discard only task-owned candidate work. Candidate preparation creates no Visual Docs without an explicit request.
8. Before fast-forward promotion of a verified candidate commit, require the destination to be clean at the validated baseline and recheck candidate identity and source hashes. If user work or HEAD drift prevents that operation, keep the candidate ready and leave the destination untouched; do not reset or auto-stash it. Rebase and revalidate against changed relevant inputs before proposing another application. Candidate validation alone does not mean the transition was applied.

The transition manifest is durable audit data, but the replacement bundle remains the active source of truth. Existing transition records stay in canonical order as an exact prefix; a prior record never authorizes another deletion. A `merged` group must contain at least two exact active baseline sources and cannot be extended after the target becomes part of a baseline.

