# Invalid Mermaid fallback plan

Status: active

**Related Specs:** None — browser fallback fixture changes no product behavior

**Goal:** Keep one invalid source diagram isolated from the other panels.

## Global Constraints

- Preserve the original invalid Mermaid text.

## Flow

```mermaid
flowchart LR
    A[Source] -->
```

## Tasks

### Task 1: Exercise fallback

- Route: fallback
- Dependencies: none

- [ ] **Step 1: Open the invalid diagram**

Run: `bash tests/run-review-viewer-browser.sh`

Expected: the source and error remain visible

## Progress History

- 2026-08-01: fixture created.
