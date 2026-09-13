# Previously held-out export review

This source was withheld from implementation examples in the 2026-09-13 evaluation. A fresh agent used the released skill workflow to write composition.json. Another fresh agent read only the visible explanation, excluding evidence disclosures and source details, and answered all six prewritten questions correctly. This is an agent evaluation, not a human usability study.

To reproduce, copy report-export.md to docs/specs/report-export/report-export.md in an isolated Git repository with a baseline commit. Copy composition.json to .forge/visual-docs/export-review/composition.json. Build with --kind spec --spec docs/specs/report-export --view-id export-review --locale ko --audience operations --offline --composition .forge/visual-docs/export-review/composition.json. Prepare again if source/schema has changed and reconsider evidence; do not blindly update the fingerprint.

Expected answers:

1. Missing required information: do not enqueue; request completion.
2. At most three attempts including the original. The prose specifies temporary errors while Requirements use a broader error phrase; do not silently choose one scope.
3. Cancellation between file completion and URL publication is unspecified.
4. URL retention is undecided.
5. CSV or PDF.
6. Clarify required fields, retry error scope, intermediate cancellation and retention.

The source has ordinary prose and no Mermaid. The author chose comparison tables and an explicit retry example, preserving gaps instead of inventing policy. The fixture is now retained for regression and is no longer an unseen evaluation source.
