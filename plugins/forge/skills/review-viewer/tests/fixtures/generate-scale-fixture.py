#!/usr/bin/env python3
"""Generate independent spec and plan lifecycle Viewer scale fixtures."""

from __future__ import annotations

import html
import sys
from pathlib import Path

TASKS = 22
STEPS_PER_TASK = 5
REQUIREMENTS = 190
ACCEPTANCE = 105
MERMAID = 9
ROUTES = 8


def diagrams() -> list[str]:
    result = [
        """sequenceDiagram
    participant User
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
    return f"""# Scale Fixture Spec

Status: approved

## Overview

Scale fixture for an independent spec View.

## Requirements

{requirements}

## Behavior & Flows

{diagram_text}

## Data & Interfaces

Source-owned fixture data.

## Acceptance Criteria

{acceptance}

## Decisions & History

- Approved fixture.
"""


def build_plan() -> str:
    route_rows = "\n".join(
        f"| Expedition Route {route} | "
        + ", ".join(
            f"Task {task}" for task in range(1, TASKS + 1) if route_for_task(task) == route
        )
        + " |"
        for route in range(1, ROUTES + 1)
    )
    task_index = "\n".join(
        f"- [ ] Task {task}: `tasks/{task:03d}-fixture.md`" for task in range(1, TASKS + 1)
    )
    return f"""# Scale Fixture Plan

Status: active

**Related Specs:**
- `../../specs/001-scale/spec.md`: navigation link only

## Implementation Routes

| Route | Tasks |
|---|---|
{route_rows}

## Tasks

{task_index}

## Progress History

- Fixture created.
"""


def build_task(task: int) -> str:
    steps = "\n".join(
        f"- [ ] **Step {step}: Task {task} step {step}**"
        for step in range(1, STEPS_PER_TASK + 1)
    )
    return f"""### Task {task}: Fixture task {task}

**Route:** Expedition Route {route_for_task(task)}

{steps}
"""


def panel(panel_id: str, title: str, body: str) -> str:
    return f'<section class="tab-panel" id="{panel_id}" data-title="{title}">\n{body}\n</section>'


def build_spec_fragment() -> str:
    requirements = "\n".join(
        f'<tr id="R{number}"><td><a href="#R{number}">R{number}</a></td><td>Requirement {number}.</td></tr>'
        for number in range(1, REQUIREMENTS + 1)
    )
    diagram_blocks = []
    for index, source in enumerate(diagrams(), start=1):
        summary = (
            f'<div class="table-scroll" role="region" aria-label="Diagram {index} 모바일 요약">'
            '<table><thead><tr><th>Source</th><th>확인 관계</th></tr></thead>'
            f'<tbody><tr><td>Spec source</td><td>Diagram {index}</td></tr></tbody></table></div>'
        )
        diagram_blocks.append(
            f"""<div class="diagram-block" data-origin="Spec source">
<h3 id="spec-diagram-{index}">Diagram {index}에서 무엇을 확인할까?</h3>
<p><strong>이 화면에서 확인할 것:</strong> spec source 관계만 표시되는지 확인한다.</p>
<p>읽는 법: source의 actor와 화살표 순서를 그대로 따른다.</p>
{summary}<div class="diagram-scroll" aria-labelledby="spec-diagram-{index}"><pre class="mermaid">{html.escape(source)}</pre></div>
</div>"""
        )
    criteria = "\n".join(
        f'<label class="ac-item" id="AC{number}"><input type="checkbox" data-ac="AC{number}"> AC{number}</label>'
        for number in range(1, ACCEPTANCE + 1)
    )
    return "\n".join(
        (
            panel("overview", "개요", "<h2>스펙의 검토 규모는 얼마일까?</h2>"),
            panel(
                "requirements",
                "요구사항",
                f'<h2>어떤 요구사항을 추적할까?</h2><div class="table-scroll"><table><tbody>{requirements}</tbody></table></div>',
            ),
            panel("flows", "흐름", "<h2>어떤 동작을 확인할까?</h2>" + "".join(diagram_blocks)),
            panel("data", "데이터와 인터페이스", "<h2>spec.md가 어떤 정보를 소유할까?</h2>"),
            panel("acceptance", "승인 기준", "<h2>어떤 AC를 검토할까?</h2>" + criteria),
            panel("history", "변경 이력", "<h2>어떤 source에서 생성됐을까?</h2>"),
        )
    ) + "\n"


def build_plan_fragment() -> str:
    routes = []
    for route in range(1, ROUTES + 1):
        articles = []
        for task in range(1, TASKS + 1):
            if route_for_task(task) != route:
                continue
            steps = "".join(
                f'<label class="ac-item" id="Task{task}-Step{step}"><input type="checkbox" data-step="Task{task}-Step{step}"> Step {step}</label>'
                for step in range(1, STEPS_PER_TASK + 1)
            )
            articles.append(f'<article id="Task{task}"><h4><a href="#Task{task}">Task {task}</a></h4>{steps}</article>')
        routes.append(
            f'<section data-route="Expedition Route {route}" data-origin="Plan source"><h3>Expedition Route {route}</h3>{"".join(articles)}</section>'
        )
    route_map = (
        '<div data-origin="Derived view"><h3>Route membership은 어떻게 구성됐을까?</h3>'
        '<p><strong>이 화면에서 확인할 것:</strong> plan에 명시된 membership만 사용했는지 확인한다.</p>'
        '<p>읽는 법: Route 1부터 8까지 Task를 확인한다.</p></div>'
    )
    return "\n".join(
        (
            panel("overview", "개요", "<h2>계획의 실행 규모는 얼마일까?</h2>"),
            panel("requirements", "요구사항", "<h2>어떤 plan constraint를 적용할까?</h2><p>Related Specs는 link only다.</p>"),
            panel("flows", "흐름", "<h2>어떤 Route로 실행할까?</h2>" + "".join(routes) + route_map),
            panel("data", "데이터와 인터페이스", "<h2>plan source는 어떻게 나뉠까?</h2>"),
            panel("acceptance", "승인 기준", "<h2>Task를 어떤 검증으로 확인할까?</h2>"),
            panel("history", "변경 이력", "<h2>어떤 progress를 기록했을까?</h2>"),
        )
    ) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: generate-scale-fixture.py OUTPUT_DIR", file=sys.stderr)
        return 2
    output = Path(sys.argv[1])
    spec_dir = output / "specs" / "001-scale"
    plan_dir = output / "plans" / "001-scale"
    tasks_dir = plan_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(build_spec(), encoding="utf-8")
    (spec_dir / "fragment.html").write_text(build_spec_fragment(), encoding="utf-8")
    (plan_dir / "plan.md").write_text(build_plan(), encoding="utf-8")
    (plan_dir / "progress.md").write_text("# Progress\n\nNo completed Tasks.\n", encoding="utf-8")
    (plan_dir / "fragment.html").write_text(build_plan_fragment(), encoding="utf-8")
    for task in range(1, TASKS + 1):
        (tasks_dir / f"{task:03d}-fixture.md").write_text(build_task(task), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
