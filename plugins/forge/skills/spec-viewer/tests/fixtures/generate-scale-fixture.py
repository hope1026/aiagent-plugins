#!/usr/bin/env python3
"""Generate the lifecycle Viewer scale fixture in a temporary directory."""

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
    R{number}[Expedition Route {number}] --> T{number}[Task {number}]
    T{number} --> AC{number}[AC{number}]"""
        )
    return result


def build_spec() -> str:
    requirement_lines = "\n".join(
        f"- R{number}. Requirement {number}." for number in range(1, REQUIREMENTS + 1)
    )
    diagram_lines = "\n\n".join(
        f"```mermaid\n{source}\n```" for source in diagrams()
    )
    acceptance_lines = "\n".join(
        f"- AC{number} (R{((number - 1) % REQUIREMENTS) + 1}): Acceptance {number}."
        for number in range(1, ACCEPTANCE + 1)
    )
    return f"""# Scale Fixture Spec

Status: approved

## Overview

Scale fixture for lifecycle review.

## Requirements

{requirement_lines}

## Behavior & Flows

{diagram_lines}

## Data & Interfaces

Source-owned fixture data.

## Acceptance Criteria

{acceptance_lines}

## Decisions & History

- Approved fixture.
"""


def route_for_task(task: int) -> int:
    return min(ROUTES, ((task - 1) * ROUTES // TASKS) + 1)


def build_plan() -> str:
    route_rows = "\n".join(
        f"| Expedition Route {route} | "
        + ", ".join(
            f"Task {task}" for task in range(1, TASKS + 1) if route_for_task(task) == route
        )
        + " |"
        for route in range(1, ROUTES + 1)
    )
    tasks: list[str] = []
    for task in range(1, TASKS + 1):
        requirement = ((task - 1) % REQUIREMENTS) + 1
        criterion = ((task - 1) % ACCEPTANCE) + 1
        steps = "\n".join(
            f"- [ ] **Step {step}: Task {task} step {step}**"
            for step in range(1, STEPS_PER_TASK + 1)
        )
        tasks.append(
            f"""### Task {task}: Fixture task {task} (R{requirement} · AC{criterion})

**Route:** Expedition Route {route_for_task(task)}

{steps}"""
        )
    return f"""# Scale Fixture Plan

**Spec:** `spec.md`

## Implementation Routes

| Route | Tasks |
|---|---|
{route_rows}

## Tasks

{chr(10).join(chr(10) + task for task in tasks)}
"""


def build_fragment() -> str:
    overview = f"""<section class="tab-panel" id="overview" data-title="개요">
<h2>전체 구현 경로가 요구사항을 어떻게 충족할까?</h2>
<p><strong>이 화면에서 확인할 것:</strong> source count와 검토 순서를 확인한다.</p>
<div class="table-scroll"><table><thead><tr><th>Task</th><th>Step</th><th>R</th><th>AC</th><th>Mermaid</th><th>Route</th></tr></thead><tbody><tr><td>{TASKS}</td><td>{TASKS * STEPS_PER_TASK}</td><td>{REQUIREMENTS}</td><td>{ACCEPTANCE}</td><td>{MERMAID}</td><td>{ROUTES}</td></tr></tbody></table></div>
</section>"""
    requirement_rows = "\n".join(
        f'<tr id="R{number}"><td><a href="#R{number}">R{number}</a></td><td>Requirement {number}.</td></tr>'
        for number in range(1, REQUIREMENTS + 1)
    )
    requirements = f"""<section class="tab-panel" id="requirements" data-title="요구사항">
<h2>어떤 요구사항을 추적할까?</h2>
<div class="table-scroll"><table><thead><tr><th>ID</th><th>Requirement</th></tr></thead><tbody>{requirement_rows}</tbody></table></div>
</section>"""

    route_sections: list[str] = []
    for route in range(1, ROUTES + 1):
        task_articles: list[str] = []
        for task in range(1, TASKS + 1):
            if route_for_task(task) != route:
                continue
            steps = "".join(
                f'<label class="ac-item" id="Task{task}-Step{step}"><input type="checkbox" data-step="Task{task}-Step{step}"> Step {step}</label>'
                for step in range(1, STEPS_PER_TASK + 1)
            )
            task_articles.append(
                f'<article id="Task{task}"><h4><a href="#Task{task}">Task {task}</a></h4>{steps}</article>'
            )
        route_sections.append(
            f'<section data-route="Expedition Route {route}" data-origin="Plan source"><h3>Expedition Route {route}</h3>{"".join(task_articles)}</section>'
        )
    derived_route_map = (
        '<div class="route-map" data-origin="Derived view"><h3>Route 순서는 어떻게 계산됐을까?</h3>'
        '<p><strong>이 화면에서 확인할 것:</strong> plan에 명시된 Route membership만 사용했는지 확인한다.</p>'
        '<p>읽는 법: Expedition Route 1부터 8까지 순서대로 Task membership을 확인한다.</p><ol>'
        + "".join(
            f'<li>Expedition Route {route}: '
            + ", ".join(
                f'Task {task}' for task in range(1, TASKS + 1) if route_for_task(task) == route
            )
            + "</li>"
            for route in range(1, ROUTES + 1)
        )
        + "</ol></div>"
    )

    diagram_blocks: list[str] = []
    for index, source in enumerate(diagrams(), start=1):
        summary = (
            f'<div class="table-scroll" role="region" aria-label="Diagram {index} 모바일 요약">'
            f'<table><thead><tr><th>Source</th><th>확인 관계</th></tr></thead><tbody><tr><td>Spec source</td><td>Diagram {index} node와 edge</td></tr></tbody></table></div>'
        )
        if index == 1:
            summary = """<div class="table-scroll" role="region" aria-label="Runtime 책임 모바일 요약"><table><thead><tr><th>Actor</th><th>Responsibility</th></tr></thead><tbody><tr><td>User</td><td>검토 시작</td></tr><tr><td>Viewer</td><td>source evidence 표시</td></tr><tr><td>Source</td><td>결정 소유</td></tr></tbody></table></div>"""
        diagram_blocks.append(
            f"""<div class="diagram-block" data-origin="Spec source">
<h3 id="diagram-{index}-title">Diagram {index}에서 무엇을 확인할까?</h3>
<p><strong>이 화면에서 확인할 것:</strong> source에 명시된 관계만 표시하는지 확인한다.</p>
<p>읽는 법: actor와 화살표를 source 순서대로 따른다.</p>
{summary}<div class="diagram-scroll" aria-labelledby="diagram-{index}-title"><pre class="mermaid">{html.escape(source)}</pre></div>
</div>"""
        )
    flows = f"""<section class="tab-panel" id="flows" data-title="흐름">
<h2>어떤 Route 순서로 구현할까?</h2>
{"".join(route_sections)}
{derived_route_map}
{"".join(diagram_blocks)}
</section>"""

    data = """<section class="tab-panel" id="data" data-title="데이터와 인터페이스">
<h2>누가 어떤 정보를 소유할까?</h2>
<div class="table-scroll"><table><thead><tr><th>Source</th><th>Responsibility</th></tr></thead><tbody><tr><td>spec.md</td><td>R·AC·Mermaid</td></tr><tr><td>plan.md</td><td>Route·Task·Step</td></tr></tbody></table></div>
</section>"""

    criteria: list[str] = []
    for criterion in range(1, ACCEPTANCE + 1):
        requirement = ((criterion - 1) % REQUIREMENTS) + 1
        task = ((criterion - 1) % TASKS) + 1
        criteria.append(
            f'<label class="ac-item" id="AC{criterion}"><input type="checkbox" data-ac="AC{criterion}"><span><strong>AC{criterion}</strong> <a href="#R{requirement}">R{requirement}</a> → <a href="#Task{task}">Task {task}</a> → <a href="#Task{task}-Step1">Step 1</a> → fixture verification</span></label>'
        )
    acceptance = f"""<section class="tab-panel" id="acceptance" data-title="승인 기준">
<h2>어떤 evidence로 완료를 확인할까?</h2>
{"".join(criteria)}
</section>"""
    history = """<section class="tab-panel" id="history" data-title="변경 이력">
<h2>어떤 source에서 다시 만들 수 있을까?</h2>
<p>source path, hash, count, freshness, rebuild command는 shell manifest에 표시된다.</p>
</section>"""
    return "\n".join((overview, requirements, flows, data, acceptance, history)) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: generate-scale-fixture.py OUTPUT_DIR", file=sys.stderr)
        return 2
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    (output / "spec.md").write_text(build_spec(), encoding="utf-8")
    (output / "plan.md").write_text(build_plan(), encoding="utf-8")
    (output / "fragment.html").write_text(build_fragment(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
