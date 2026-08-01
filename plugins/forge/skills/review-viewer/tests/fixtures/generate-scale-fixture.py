#!/usr/bin/env python3
"""Generate structured scale sources without any manual HTML fragment."""

from __future__ import annotations

from pathlib import Path
import sys


TASKS = 22
STEPS_PER_TASK = 5
REQUIREMENTS = 190
ACCEPTANCE = 105
MERMAID = 9
ROUTES = 8


def diagrams() -> list[str]:
    result = [
        """sequenceDiagram
    actor User
    participant Viewer
    participant Source
    User->>Viewer: open review
    Viewer->>Source: show source-owned evidence
    Source-->>User: traceable decision"""
    ]
    for number in range(2, MERMAID + 1):
        result.append(
            f"""flowchart LR
    R{number}[Requirement group {number}] --> AC{number}[Acceptance {number}]"""
        )
    return result


def route_for_task(task: int) -> int:
    return min(ROUTES, ((task - 1) * ROUTES // TASKS) + 1)


def build_spec() -> str:
    requirements = "\n".join(
        f"- R{number}. Requirement {number}." for number in range(1, REQUIREMENTS + 1)
    )
    diagram_text = "\n\n".join(f"```mermaid\n{source}\n```" for source in diagrams())
    acceptance = "\n".join(
        f"- AC{number} (R{((number - 1) % REQUIREMENTS) + 1}): Acceptance {number}."
        for number in range(1, ACCEPTANCE + 1)
    )
    return f"""---
schema: forge/spec@1
id: 001-scale
status: approved
language: en
kind: system
areas: ["forge"]
components: ["review-viewer"]
relatedSpecs: []
---
# Scale Fixture Spec

## Overview

Scale fixture for source-qualified Review Viewer counts.

## Requirements

{requirements}

## Behavior & Flows

{diagram_text}

## Data & Interfaces

Source-owned fixture data.

## Acceptance Criteria

{acceptance}

## Decisions & History

- 2026-08-01 [DECISION] Preserve structured scale evidence.
"""


def _item_list(prefix: str, count: int) -> str:
    return ", ".join(f"{prefix}{number}" for number in range(1, count + 1))


def build_plan() -> str:
    task_index = "\n".join(
        f"- [ ] Task {task}: `tasks/{task:03d}-fixture.md`" for task in range(1, TASKS + 1)
    )
    return f"""# Scale Fixture Plan

Status: active

**Related Specs:**
- id: 001-scale
  path: docs/specs/001-scale/spec.md
  requirements: [{_item_list("R", REQUIREMENTS)}]
  acceptance: [{_item_list("AC", ACCEPTANCE)}]

**Goal:** Exercise exact source-owned counts and namespaced traceability.

## Global Constraints

- Context source does not alter Route membership.

## Runtime Responsibility

| Actor | Responsibility |
|---|---|
| Viewer | Present selected source evidence. |
| Source | Own requirements and execution detail. |

## Flow

```mermaid
flowchart LR
    Plan[Plan source] --> Tasks[Split Task sources]
```

## Tasks

{task_index}

## Progress History

- 2026-08-01: scale fixture created.
"""


def build_task(task: int) -> str:
    requirement = ((task - 1) % REQUIREMENTS) + 1
    acceptance = ((task - 1) % ACCEPTANCE) + 1
    dependency = "none" if task == 1 else f"Task {task - 1}"
    steps = "\n".join(
        f"- [ ] **Step {step}: Task {task} step {step}**"
        for step in range(1, STEPS_PER_TASK + 1)
    )
    return f"""### Task {task}: Fixture task {task} (001 R{requirement}, AC{acceptance})

- Route: expedition-route-{route_for_task(task)}
- Dependencies: {dependency}

{steps}

Run: `python3 verify-task-{task}.py`

Expected: Task {task} evidence is observable
"""


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: generate-scale-fixture.py REPOSITORY_ROOT", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    spec_dir = root / "docs/specs/001-scale"
    plan_dir = root / "docs/plans/001-scale"
    tasks_dir = plan_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(build_spec(), encoding="utf-8")
    (plan_dir / "plan.md").write_text(build_plan(), encoding="utf-8")
    (plan_dir / "progress.md").write_text(
        "# Progress\n\nCheckpoint: scale-ready\n", encoding="utf-8"
    )
    for task in range(1, TASKS + 1):
        (tasks_dir / f"{task:03d}-fixture.md").write_text(
            build_task(task), encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
