"""Deterministic six-panel renderer for requested Forge Review Viewers."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
import re
import sys
from typing import Iterable, Mapping

from review_sources import (
    PlanDocument,
    ReviewBundle,
    ReviewSource,
)


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_DIR / "assets/viewer-template.html"
FRESHNESS_RUNTIME_PATH = SKILL_DIR / "assets/viewer-freshness.mjs"
WRITING_SPECS_SCRIPTS = SKILL_DIR.parent / "writing-specs" / "scripts"
WRITING_SPECS_ASSETS = SKILL_DIR.parent / "writing-specs" / "assets"
MERMAID_PATH = WRITING_SPECS_ASSETS / "mermaid.min.js"
MERMAID_CHECKSUM_PATH = WRITING_SPECS_ASSETS / "mermaid.sha256"
MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.16.0/dist/mermaid.min.js"
PANELS = ("overview", "requirements", "flows", "data", "acceptance", "history")


def _load_shared_markdown_renderer():
    module_path = WRITING_SPECS_SCRIPTS / "markdown_render.py"
    if not module_path.is_file():
        raise RuntimeError(f"writing-specs sibling Markdown renderer not found: {module_path}")
    value = str(WRITING_SPECS_SCRIPTS)
    if value not in sys.path:
        sys.path.insert(0, value)
    from markdown_render import render_markdown

    return render_markdown


render_markdown = _load_shared_markdown_renderer()


LABELS = {
    "en": {
        "spec_title": "What should this specification review confirm?",
        "plan_title": "How will this plan execute and prove its outcome?",
        "generated": "Generated",
        "nav": "Review sections",
        "diagram": "Diagram",
        "mermaid_error": "Diagram could not be rendered",
        "freshness": "Freshness",
        "source_picker": "Verify this source locally",
        "tabs": ("Overview", "Requirements", "Flows", "Data & Interfaces", "Acceptance", "History"),
        "read_order": "Read summary first, then visual flow, source detail, and acceptance evidence.",
        "check": "What to confirm",
        "read": "How to read",
        "source": "Source",
        "role": "Role",
        "namespace": "Namespace",
        "path": "Path",
        "hash": "SHA-256",
        "state": "State",
        "error": "Issue",
        "reviewed": "Reviewed",
        "empty": "No source-owned content is present for this view.",
        "diagram_question": "Diagram {number}: what relationship should be confirmed?",
        "diagram_confirm": "{origin} relationships and provenance match the selected source.",
        "diagram_read": "Follow the nodes and arrows in the order recorded by the source.",
        "actor": "Actor",
        "source_interaction": "Source-declared interaction",
        "source_path": "Source path",
        "sends": "Sends “{message}” to {actor}",
        "receives": "Receives “{message}” from {actor}",
        "declared_actor": "Declared as an actor without a message edge.",
        "requirements_aria": "Requirements",
        "requirement": "Requirement",
        "count_scope": "Source set / metric",
        "count": "Count",
        "counts_aria": "Review counts",
        "spec_overview": "What is in this review snapshot?",
        "spec_requirements": "Which source-owned requirements should be compared?",
        "spec_flows": "Which source flows should be inspected?",
        "spec_data": "Which data and interface contracts are source-owned?",
        "spec_acceptance": "Which acceptance evidence should be reviewed?",
        "spec_history": "Where did this snapshot come from?",
        "plan_overview": "What outcome and execution scale should be reviewed?",
        "plan_requirements": "Which constraints and product context govern this plan?",
        "plan_flows": "How do explicit Routes, dependencies, and source flows connect?",
        "plan_data": "Where are runtime and interface responsibilities declared?",
        "plan_acceptance": "Which explicit trace and evidence should be reviewed?",
        "plan_history": "Which sources and checkpoints produced this snapshot?",
        "goal": "Goal",
        "plan_title_label": "Plan title",
        "goal_missing": "No canonical Goal was recorded by the plan source.",
        "status_label": "Status",
        "source_completion": "Reviewed source completion",
        "steps_checked": "Steps checked in Markdown",
        "task_detail": "Source-owned Task and Step detail",
        "route_empty": "No explicit Route metadata.",
        "route_question": "Route Map: which explicit Route owns each Task?",
        "task_route": "Route",
        "explicit_trace": "Explicit trace",
        "unselected": "unselected",
        "route_scope_heading": "Explicit Route scope",
        "route_id": "Route ID",
        "route_title": "Source title",
        "route_tasks": "Task scope",
        "route_dependencies": "Route prerequisites",
        "coverage_confirm": "Only source-qualified Task trace and verification evidence appear.",
        "coverage_read": "Follow a context R or AC to its Task, Steps, and recorded command.",
        "explicit_item": "Explicit R/AC",
        "task": "Task",
        "steps": "Steps",
        "verification": "Verification",
        "coverage_summary": "{tasks} source Tasks · {steps} source Steps.",
        "task_steps_aria": "Source Steps for {task}",
        "runtime_empty": "No source-owned runtime or interface section was selected.",
        "runtime_confirm": "Runtime and interface statements remain owned by the plan source.",
        "runtime_read": "Inspect only the plan sections shown with their source provenance.",
        "detail_empty": "No source-owned detail.",
        "source_state_heading": "Source plan status and checkbox state",
        "source_state_note": "Read-only source Markdown state; reviewer checkboxes are stored separately in this browser.",
        "source_plan_status": "Source plan status",
        "source_check_state": "Source checkbox state",
        "checked": "checked",
        "unchecked": "unchecked",
        "provenance_aria": "Source provenance",
        "metadata_heading": "Snapshot metadata",
        "metadata_field": "Field",
        "metadata_value": "Value",
        "metadata_aria": "Snapshot metadata",
        "responsibility_aria": "Runtime responsibility summary",
    },
    "ko": {
        "spec_title": "이 스펙 검토에서 무엇을 확인해야 할까?",
        "plan_title": "이 계획은 어떻게 실행되고 결과를 증명할까?",
        "generated": "생성",
        "nav": "검토 섹션",
        "diagram": "다이어그램",
        "mermaid_error": "다이어그램을 렌더링하지 못했습니다",
        "freshness": "최신성",
        "source_picker": "이 source를 로컬에서 검증",
        "tabs": ("개요", "요구사항", "흐름", "데이터와 인터페이스", "승인 기준", "변경 이력"),
        "read_order": "요약을 먼저 보고 시각 흐름, source 상세, acceptance evidence 순서로 읽습니다.",
        "check": "이 화면에서 확인할 것",
        "read": "읽는 법",
        "source": "Source",
        "role": "Role",
        "namespace": "Namespace",
        "path": "Path",
        "hash": "SHA-256",
        "state": "상태",
        "error": "문제",
        "reviewed": "검토함",
        "empty": "이 화면에 표시할 source-owned 내용이 없습니다.",
        "diagram_question": "다이어그램 {number}: 어떤 관계를 확인할까?",
        "diagram_confirm": "{origin} 관계와 provenance가 선택한 source와 일치하는지 확인합니다.",
        "diagram_read": "source에 기록된 순서대로 노드와 화살표를 읽습니다.",
        "actor": "Actor",
        "source_interaction": "Source에 기록된 interaction",
        "source_path": "Source path",
        "sends": "{actor}에게 “{message}” 전송",
        "receives": "{actor}에게서 “{message}” 수신",
        "declared_actor": "message edge 없이 actor로 선언됨",
        "requirements_aria": "요구사항",
        "requirement": "요구사항",
        "count_scope": "Source set / 항목",
        "count": "수량",
        "counts_aria": "검토 수량",
        "spec_overview": "이 검토 snapshot에는 무엇이 들어 있을까?",
        "spec_requirements": "어떤 source-owned 요구사항을 비교할까?",
        "spec_flows": "어떤 source flow를 확인할까?",
        "spec_data": "어떤 데이터와 interface 계약을 source가 소유할까?",
        "spec_acceptance": "어떤 acceptance evidence를 검토할까?",
        "spec_history": "이 snapshot은 어디에서 왔을까?",
        "plan_overview": "어떤 목표와 실행 규모를 검토할까?",
        "plan_requirements": "어떤 constraint와 제품 context가 이 계획을 지배할까?",
        "plan_flows": "명시된 Route와 dependency, source flow는 어떻게 연결될까?",
        "plan_data": "runtime과 interface 책임은 어디에 선언됐을까?",
        "plan_acceptance": "어떤 명시적 trace와 evidence를 검토할까?",
        "plan_history": "어떤 source와 checkpoint가 이 snapshot을 만들었을까?",
        "goal": "목표",
        "plan_title_label": "계획 제목",
        "goal_missing": "plan source에 정본 목표가 기록되지 않았습니다.",
        "status_label": "상태",
        "source_completion": "Source 진행 상태",
        "steps_checked": "Markdown에서 체크된 Step",
        "task_detail": "Source-owned Task와 Step 상세",
        "route_empty": "명시된 Route metadata가 없습니다.",
        "route_question": "Route Map: 각 Task는 어떤 명시적 Route에 속할까?",
        "task_route": "Route",
        "explicit_trace": "명시적 trace",
        "unselected": "선택 안 됨",
        "route_scope_heading": "명시적 Route 적용 범위",
        "route_id": "Route ID",
        "route_title": "Source 제목",
        "route_tasks": "Task 범위",
        "route_dependencies": "Route 선행 조건",
        "coverage_confirm": "Source-qualified Task trace와 verification evidence만 표시되는지 확인합니다.",
        "coverage_read": "context R 또는 AC에서 Task, Step, 기록된 command 순서로 읽습니다.",
        "explicit_item": "명시적 R/AC",
        "task": "Task",
        "steps": "Step",
        "verification": "검증",
        "coverage_summary": "Source Task {tasks}개 · Source Step {steps}개.",
        "task_steps_aria": "{task}의 Source Step",
        "runtime_empty": "선택된 source에 runtime 또는 interface section이 없습니다.",
        "runtime_confirm": "runtime과 interface 문장이 plan source에 의해 소유되는지 확인합니다.",
        "runtime_read": "source provenance와 함께 표시된 plan section만 읽습니다.",
        "detail_empty": "Source-owned 상세가 없습니다.",
        "source_state_heading": "Source plan 상태와 checkbox 상태",
        "source_state_note": "읽기 전용 source Markdown 상태이며 reviewer checkbox는 이 브라우저에 별도로 저장됩니다.",
        "source_plan_status": "Source plan 상태",
        "source_check_state": "Source checkbox 상태",
        "checked": "체크됨",
        "unchecked": "체크 안 됨",
        "provenance_aria": "Source provenance",
        "metadata_heading": "Snapshot metadata",
        "metadata_field": "항목",
        "metadata_value": "값",
        "metadata_aria": "Snapshot metadata",
        "responsibility_aria": "Runtime 책임 요약",
    },
}

ORIGINS = {
    "primary_spec": "Current spec source",
    "comparison_spec": "Comparison source",
    "primary_plan": "Plan source",
    "plan_progress": "Plan source",
    "plan_task": "Plan source",
    "related_spec_context": "Related spec context",
}


def _source_sequence(bundle: ReviewBundle) -> tuple[ReviewSource, ...]:
    return (*bundle.primary, *bundle.comparison, *bundle.context)


def _json_for_html(value: object) -> str:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def _manifest(
    bundle: ReviewBundle,
    *,
    review_id: str,
    locale: str,
    generated_at: str,
    checkpoint: str,
    commit: str | None,
    rebuild_command: str,
    source_base: str,
    offline: bool,
) -> dict[str, object]:
    return {
        "review_id": review_id,
        "mode": bundle.mode,
        "locale": locale,
        "generated_at": generated_at,
        "checkpoint": checkpoint,
        "commit": commit,
        "rebuild_command": rebuild_command,
        "source_base": source_base,
        "offline": offline,
        "counts": _plain(bundle.counts),
        "freshness": "unverified",
        "sources": [
            {
                "role": source.role,
                "namespace": source.namespace,
                "path": source.path,
                "sha256": source.sha256,
                "requirements": list(source.requirements),
                "acceptance": list(source.acceptance),
                "status": source.status,
            }
            for source in _source_sequence(bundle)
        ],
    }


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _source_group(role: str) -> str:
    if role == "comparison_spec":
        return "comparison"
    if role == "related_spec_context":
        return "context"
    return "primary"


def _source_summary(bundle: ReviewBundle, labels: Mapping[str, object]) -> str:
    aggregate_order = ("primary", "comparison", "context")
    aggregates = "".join(
        '<span class="freshness-aggregate" '
        f'data-freshness-group="{group}">{html.escape(group)} '
        '<strong class="freshness-state freshness-unverified">unverified</strong></span>'
        for group in aggregate_order
    )
    rows = []
    for source in _source_sequence(bundle):
        key = f"{source.namespace}:{source.path}"
        escaped_key = html.escape(key, quote=True)
        rows.append(
            '<li class="source-row" '
            f'data-source-key="{escaped_key}" data-source-path="{html.escape(source.path, quote=True)}" '
            f'data-source-group="{_source_group(source.role)}">'
            f'<span class="source-role">{html.escape(source.role)}</span> '
            f'<code>{html.escape(source.namespace)}</code> '
            f'<code>{html.escape(source.path)}</code> '
            '<span class="freshness-state freshness-unverified" data-source-state>unverified</span>'
            '<span class="source-error" data-source-error aria-live="polite"></span>'
            f'<label class="source-picker-label">{html.escape(str(labels["source_picker"]))}'
            f'<input type="file" accept=".md,text/markdown" data-source-picker data-source-key="{escaped_key}"></label>'
            '</li>'
        )
    return (
        '<details class="source-summary">'
        f'<summary>{html.escape(str(labels["freshness"]))}: '
        '<span class="freshness-state freshness-unverified" data-freshness-overall>unverified</span></summary>'
        f'<div class="freshness-aggregates">{aggregates}</div>'
        f'<ul>{"".join(rows)}</ul></details>'
    )


def _panel(panel_id: str, title: str, body: str) -> str:
    return (
        f'<section class="tab-panel" id="{panel_id}" data-title="{html.escape(title, quote=True)}" '
        f'role="tabpanel" aria-labelledby="tab-{panel_id}">\n{body}\n</section>'
    )


def _provenance(source: ReviewSource) -> str:
    return (
        '<p class="provenance">'
        f'<span>{html.escape(ORIGINS[source.role])}</span> · '
        f'<code>{html.escape(source.path)}</code> · '
        f'<code>{html.escape(source.namespace)}</code></p>'
    )


def _strip_mermaid(text: str) -> str:
    lines = text.splitlines()
    result: list[str] = []
    index = 0
    while index < len(lines):
        match = re.fullmatch(r" {0,3}(`{3,}|~{3,})mermaid[ \t]*", lines[index])
        if match is None:
            result.append(lines[index])
            index += 1
            continue
        marker = match.group(1)
        index += 1
        while index < len(lines):
            if re.fullmatch(rf" {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*", lines[index]):
                index += 1
                break
            index += 1
    return "\n".join(result).strip("\n")


def _sequence_evidence(
    source: str,
) -> tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str, str], ...]]:
    actors: dict[str, str] = {}
    messages: list[tuple[str, str, str]] = []
    for line in source.splitlines():
        match = re.fullmatch(r"\s*(?:actor|participant)\s+(\S+)(?:\s+as\s+(.+))?\s*", line)
        if match:
            actors.setdefault(match.group(1), match.group(2) or match.group(1))
            continue
        message = re.fullmatch(
            r"\s*([A-Za-z0-9_-]+)\s*[-.ox<>=]+\s*([A-Za-z0-9_-]+)\s*:\s*(\S.*)",
            line,
        )
        if message:
            sender, receiver, text = message.groups()
            actors.setdefault(sender, sender)
            actors.setdefault(receiver, receiver)
            messages.append((sender, receiver, text))
    return tuple(actors.items()), tuple(messages)


def _responsibility_summary(source: str, path: str, labels: Mapping[str, object]) -> str:
    actors, messages = _sequence_evidence(source)
    if not actors:
        return ""
    names = dict(actors)
    rows = []
    for actor_id, actor_name in actors:
        interactions: list[str] = []
        for sender, receiver, message in messages:
            if sender == actor_id:
                interactions.append(
                    str(labels["sends"]).format(
                        message=message, actor=names.get(receiver, receiver)
                    )
                )
            if receiver == actor_id:
                interactions.append(
                    str(labels["receives"]).format(
                        message=message, actor=names.get(sender, sender)
                    )
                )
        summary = "<br>".join(html.escape(value) for value in interactions)
        if not summary:
            summary = html.escape(str(labels["declared_actor"]))
        rows.append(
            f'<tr><td>{html.escape(actor_name)}</td><td>{summary}</td>'
            f'<td><code>{html.escape(path)}</code></td></tr>'
        )
    return (
        '<div class="table-scroll responsibility-summary" role="region" tabindex="0" '
        f'aria-label="{html.escape(str(labels["responsibility_aria"]), quote=True)}"><table><thead><tr>'
        f'<th>{html.escape(str(labels["actor"]))}</th>'
        f'<th>{html.escape(str(labels["source_interaction"]))}</th>'
        f'<th>{html.escape(str(labels["source_path"]))}</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _diagram(
    source_text: str,
    *,
    origin: str,
    path: str,
    index: int,
    labels: Mapping[str, object],
    title: str | None = None,
) -> str:
    digest = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    diagram_id = f"diagram-{index}-{digest[:10]}"
    question = title or str(labels["diagram_question"]).format(number=index)
    wide = bool(re.match(r"\s*(sequenceDiagram|flowchart\s+LR|graph\s+LR)", source_text))
    summary = _responsibility_summary(source_text, path, labels)
    return (
        f'<article class="diagram-card" data-origin="{html.escape(origin, quote=True)}" '
        f'data-source-path="{html.escape(path, quote=True)}" data-mermaid-sha256="{digest}">'
        f'<h3 id="{diagram_id}">{html.escape(question)}</h3>'
        f'<p><strong>{html.escape(str(labels["check"]))}:</strong> '
        f'{html.escape(str(labels["diagram_confirm"]).format(origin=origin))}</p>'
        f'<p><strong>{html.escape(str(labels["read"]))}:</strong> '
        f'{html.escape(str(labels["diagram_read"]))}</p>'
        f'{_provenance_text(origin, path)}{summary}'
        f'<div class="diagram-scroll{" is-wide" if wide else ""}" role="region" '
        f'aria-labelledby="{diagram_id}" tabindex="0"><pre class="mermaid">'
        f'{html.escape(source_text, quote=False)}</pre></div></article>'
    )


def _provenance_text(origin: str, path: str) -> str:
    return (
        f'<p class="provenance"><span>{html.escape(origin)}</span> · '
        f'<code>{html.escape(path)}</code></p>'
    )


def _source_diagrams(bundle: ReviewBundle, labels: Mapping[str, object]) -> str:
    rendered: list[str] = []
    index = 1
    for source in _source_sequence(bundle):
        if source.document is None:
            continue
        for block in source.document.mermaid:
            rendered.append(
                _diagram(
                    block.text,
                    origin=ORIGINS[source.role],
                    path=source.path,
                    index=index,
                    labels=labels,
                )
            )
            index += 1
    return "".join(rendered)


def _spec_requirements(source: ReviewSource, labels: Mapping[str, object]) -> str:
    document = source.document
    if document is None or not hasattr(document, "requirements"):
        return ""
    selected = set(source.requirements)
    rows = []
    for requirement in document.requirements:
        if requirement.id not in selected:
            continue
        target = f"{source.namespace}-{requirement.id}"
        rows.append(
            f'<tr id="{html.escape(target, quote=True)}"><td><a href="#{html.escape(target, quote=True)}">'
            f'{html.escape(requirement.id)}</a></td><td>{html.escape(requirement.text)}</td></tr>'
        )
    if not rows:
        return ""
    return (
        f'<article class="source-block" data-origin="{html.escape(ORIGINS[source.role], quote=True)}">'
        f'<h3>{html.escape(getattr(document, "title", source.namespace))}</h3>{_provenance(source)}'
        f'<div class="table-scroll" role="region" tabindex="0" aria-label="{html.escape(str(labels["requirements_aria"]), quote=True)}">'
        f'<table><thead><tr><th>ID</th><th>{html.escape(str(labels["requirement"]))}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
        '</div></article>'
    )


def _source_item_selected(source: ReviewSource, item_id: str) -> bool:
    selected = source.acceptance if item_id.startswith("AC") else source.requirements
    return item_id in selected


def _source_item_reference(
    source: ReviewSource,
    item_id: str,
    labels: Mapping[str, object],
    *,
    qualified: bool,
) -> str:
    document = source.document
    metadata = getattr(document, "metadata", None)
    spec_id = getattr(metadata, "id", source.namespace.removeprefix("context--"))
    label = f"{spec_id}:{item_id}" if qualified else item_id
    if _source_item_selected(source, item_id):
        target = f"{source.namespace}-{item_id}"
        return (
            f'<a href="#{html.escape(target, quote=True)}">'
            f'{html.escape(label)}</a>'
        )
    return (
        '<span class="trace-unselected" data-relation-state="unselected">'
        f'{html.escape(label)} ({html.escape(str(labels["unselected"]))})</span>'
    )


def _context_reference(
    bundle: ReviewBundle,
    reference: SpecItemRef,
    labels: Mapping[str, object],
) -> str:
    namespace = f"context--{reference.spec_id}"
    source = next(
        (candidate for candidate in bundle.context if candidate.namespace == namespace),
        None,
    )
    if source is None:
        label = f"{reference.spec_id}:{reference.item_id}"
        return (
            '<span class="trace-unselected" data-relation-state="unselected">'
            f'{html.escape(label)} ({html.escape(str(labels["unselected"]))})</span>'
        )
    return _source_item_reference(
        source,
        reference.item_id,
        labels,
        qualified=True,
    )


def _spec_acceptance(source: ReviewSource, review_id: str, labels: Mapping[str, object]) -> str:
    document = source.document
    if document is None or not hasattr(document, "acceptance"):
        return ""
    selected = set(source.acceptance)
    items = []
    for criterion in document.acceptance:
        if criterion.id not in selected:
            continue
        target = f"{source.namespace}-{criterion.id}"
        requirement_links = ", ".join(
            _source_item_reference(
                source,
                requirement,
                labels,
                qualified=False,
            )
            for requirement in criterion.requirements
        )
        storage = f"{review_id}:{source.namespace}:ac:{criterion.id}"
        items.append(
            f'<article class="review-item" id="{html.escape(target, quote=True)}">'
            f'<label class="ac-item"><input type="checkbox" data-review-check data-kind="ac" '
            f'data-namespace="{html.escape(source.namespace, quote=True)}" data-item="{html.escape(criterion.id, quote=True)}" '
            f'data-storage-key="{html.escape(storage, quote=True)}">'
            f'<span><strong>{html.escape(criterion.id)}</strong> ({requirement_links}): '
            f'{html.escape(criterion.text)}</span></label></article>'
        )
    if not items:
        return ""
    return (
        f'<article class="source-block" data-origin="{html.escape(ORIGINS[source.role], quote=True)}">'
        f'<h3>{html.escape(getattr(document, "title", source.namespace))}</h3>{_provenance(source)}'
        f'{"".join(items)}</article>'
    )


def _section(source: ReviewSource, name: str) -> str:
    document = source.document
    sections = getattr(document, "sections", {}) if document is not None else {}
    value = sections.get(name, "")
    if not value:
        return ""
    rendered = render_markdown(_strip_mermaid(value))
    if not rendered:
        return ""
    return (
        f'<article class="source-block" data-origin="{html.escape(ORIGINS[source.role], quote=True)}">'
        f'{_provenance(source)}{rendered}</article>'
    )


def _user_experience(source: ReviewSource, document: PlanDocument) -> str:
    canonical = {"user experience", "사용자 경험"}
    rendered: list[str] = []
    for name, value in document.sections.items():
        if name.casefold() not in canonical:
            continue
        body = render_markdown(_strip_mermaid(value))
        if not body:
            continue
        rendered.append(
            '<article class="source-block" data-origin="Plan source" '
            f'data-plan-user-experience="{html.escape(name, quote=True)}">'
            f'<h3>{html.escape(name)}</h3>{_provenance(source)}{body}</article>'
        )
    return "".join(rendered)


def _governance_sections(source: ReviewSource, document: PlanDocument) -> str:
    tokens = ("constraint", "policy", "제약", "정책")
    rendered: list[str] = []
    for name, value in document.sections.items():
        if name.startswith(("task:", "progress:")):
            continue
        if not any(token in name.casefold() for token in tokens):
            continue
        body = render_markdown(_strip_mermaid(value))
        if not body:
            continue
        rendered.append(
            '<article class="source-block" data-origin="Plan source" '
            f'data-plan-governance-section="{html.escape(name, quote=True)}">'
            f'<h3>{html.escape(name)}</h3>{_provenance(source)}{body}</article>'
        )
    return "".join(rendered)


def _count_rows(counts: Mapping[str, object], prefix: tuple[str, ...] = ()) -> Iterable[tuple[str, int]]:
    for key, value in counts.items():
        path = (*prefix, str(key))
        if isinstance(value, Mapping):
            yield from _count_rows(value, path)
        elif type(value) is int:
            yield (" / ".join(path), value)


def _metric_strip(bundle: ReviewBundle) -> str:
    """Render the scannable counts that precede the detailed count table."""

    cells = "".join(
        f'<div class="metric"><dt>{html.escape(label)}</dt><dd>{value}</dd></div>'
        for label, value in _count_rows(bundle.counts)
    )
    if not cells:
        return ""
    return f'<dl class="metric-strip">{cells}</dl>'


def _count_table(bundle: ReviewBundle, labels: Mapping[str, object]) -> str:
    rows = "".join(
        f'<tr><td>{html.escape(label)}</td><td>{value}</td></tr>'
        for label, value in _count_rows(bundle.counts)
    )
    return (
        '<div class="table-scroll" role="region" tabindex="0" '
        f'aria-label="{html.escape(str(labels["counts_aria"]), quote=True)}">'
        f'<table class="count-table"><thead><tr><th>{html.escape(str(labels["count_scope"]))}</th>'
        f'<th>{html.escape(str(labels["count"]))}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    )


def _spec_panels(bundle: ReviewBundle, review_id: str, labels: Mapping[str, object]) -> dict[str, str]:
    sources = (*bundle.primary, *bundle.comparison)
    overview = (
        f'<h2>{html.escape(str(labels["spec_overview"]))}</h2>'
        f'<p>{html.escape(str(labels["read_order"]))}</p>'
        f'{_metric_strip(bundle)}{_count_table(bundle, labels)}'
        + "".join(_section(source, "Overview") for source in sources)
    )
    requirements = (
        f'<h2>{html.escape(str(labels["spec_requirements"]))}</h2>'
        + "".join(_spec_requirements(source, labels) for source in sources)
    )
    flows = f'<h2>{html.escape(str(labels["spec_flows"]))}</h2>' + _source_diagrams(bundle, labels)
    data = (
        f'<h2>{html.escape(str(labels["spec_data"]))}</h2>'
        + "".join(_section(source, "Data & Interfaces") for source in sources)
    )
    acceptance = (
        f'<h2>{html.escape(str(labels["spec_acceptance"]))}</h2>'
        + "".join(_spec_acceptance(source, review_id, labels) for source in sources)
    )
    history = (
        f'<h2>{html.escape(str(labels["spec_history"]))}</h2>'
        + _history_table(bundle, labels)
        + "".join(_section(source, "Decisions & History") for source in sources)
    )
    return dict(zip(PANELS, (overview, requirements, flows, data, acceptance, history)))


def _primary_plan(bundle: ReviewBundle) -> tuple[ReviewSource, PlanDocument]:
    source = bundle.primary[0]
    if not isinstance(source.document, PlanDocument):
        raise ValueError("plan bundle primary source must contain a PlanDocument")
    return source, source.document


def _route_scope(
    source: ReviewSource,
    document: PlanDocument,
    labels: Mapping[str, object],
) -> str:
    if not document.routes:
        return ""
    rows: list[str] = []
    for route in document.routes:
        tasks = " · ".join(
            f'<a href="#{html.escape(source.namespace + "-" + task_id, quote=True)}">'
            f'{html.escape(task_id)}</a>'
            for task_id in route.task_ids
        ) or "—"
        dependencies = " · ".join(
            f'<code>{html.escape(dependency)}</code>'
            for dependency in route.dependencies
        ) or "—"
        rows.append(
            f'<tr data-route-scope="{html.escape(route.id, quote=True)}">'
            f'<td><code>{html.escape(route.id)}</code></td>'
            f'<td>{html.escape(route.title)}</td><td>{tasks}</td>'
            f'<td>{dependencies}</td></tr>'
        )
    return (
        '<article class="source-block" data-origin="Plan source" data-route-scope-table>'
        f'<h3>{html.escape(str(labels["route_scope_heading"]))}</h3>{_provenance(source)}'
        '<div class="table-scroll" role="region" tabindex="0" '
        f'aria-label="{html.escape(str(labels["route_scope_heading"]), quote=True)}">'
        f'<table><thead><tr><th>{html.escape(str(labels["route_id"]))}</th>'
        f'<th>{html.escape(str(labels["route_title"]))}</th>'
        f'<th>{html.escape(str(labels["route_tasks"]))}</th>'
        f'<th>{html.escape(str(labels["route_dependencies"]))}</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></article>'
    )


def _route_map(document: PlanDocument, path: str, labels: Mapping[str, object]) -> str:
    if not document.routes:
        return (
            '<section class="signature-view"><h3>Route Map</h3>'
            f'<p>{html.escape(str(labels["route_empty"]))}</p></section>'
        )
    lines = ["flowchart LR"]
    for route_index, route in enumerate(document.routes, 1):
        route_node = f"route_{route_index}"
        lines.append(f'    {route_node}["{_mermaid_label(route.id)}"]')
        for task_id in route.task_ids:
            task_node = f"task_{task_id[4:]}"
            lines.append(f'    {task_node}["{task_id}"]')
            lines.append(f"    {route_node} --> {task_node}")
    for dependency in document.dependencies:
        lines.append(f"    task_{dependency.from_task[4:]} --> task_{dependency.to_task[4:]}")
    return (
        '<section class="signature-view"><h3>Route Map</h3>'
        + _diagram(
            "\n".join(lines),
            origin="Derived view",
            path=path,
            index=9001,
            labels=labels,
            title=str(labels["route_question"]),
        )
        + '</section>'
    )


def _mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', "'").replace("[", "(").replace("]", ")")


def _task_index(
    bundle: ReviewBundle,
    source: ReviewSource,
    document: PlanDocument,
    review_id: str,
    labels: Mapping[str, object],
) -> str:
    articles = []
    for task in document.tasks:
        task_target = f"{source.namespace}-{task.id}"
        trace = [
            _context_reference(bundle, reference, labels)
            for reference in (*task.requirements, *task.acceptance)
        ]
        steps = []
        for step in task.steps:
            target = f"{source.namespace}-{step.id}"
            storage = f"{review_id}:{source.namespace}:step:{step.id}"
            steps.append(
                f'<label class="ac-item" id="{html.escape(target, quote=True)}">'
                f'<input type="checkbox" data-review-check data-kind="step" '
                f'data-namespace="{html.escape(source.namespace, quote=True)}" data-item="{html.escape(step.id, quote=True)}" '
                f'data-storage-key="{html.escape(storage, quote=True)}">'
                f'<span>{html.escape(step.id)} — {html.escape(step.text)}</span></label>'
            )
        articles.append(
            f'<article class="task-card" id="{html.escape(task_target, quote=True)}" '
            f'data-route="{html.escape(task.route or "", quote=True)}">'
            f'<h3><a href="#{html.escape(task_target, quote=True)}">{html.escape(task.id)}: {html.escape(task.title)}</a></h3>'
            f'<p>{html.escape(str(labels["task_route"]))}: <code>{html.escape(task.route or "—")}</code></p>'
            f'<p>{html.escape(str(labels["explicit_trace"]))}: {" · ".join(trace) if trace else "—"}</p>'
            f'{"".join(steps)}</article>'
        )
    return "".join(articles)


def _coverage_table(
    bundle: ReviewBundle,
    source: ReviewSource,
    document: PlanDocument,
    labels: Mapping[str, object],
) -> str:
    rows = []
    total_steps = sum(len(task.steps) for task in document.tasks)
    for task in document.tasks:
        task_target = f"{source.namespace}-{task.id}"
        refs = (*task.requirements, *task.acceptance)
        verification = [
            evidence for evidence in document.verification if task.id in evidence.task_ids
        ]
        command = " | ".join(item.command for item in verification) or "—"
        step_links = " · ".join(
            f'<a href="#{html.escape(source.namespace + "-" + step.id, quote=True)}">'
            f'{html.escape(step.id)}</a>'
            for step in task.steps
        ) or "—"
        step_cell = (
            '<span class="coverage-steps" '
            f'data-step-count="{len(task.steps)}" '
            f'aria-label="{html.escape(str(labels["task_steps_aria"]).format(task=task.id), quote=True)}">'
            f'{step_links}</span>'
        )
        for ref in refs or (None,):
            if ref is None:
                reference = "—"
            else:
                reference = _context_reference(bundle, ref, labels)
            rows.append(
                f'<tr><td>{reference}</td><td><a href="#{html.escape(task_target, quote=True)}">{html.escape(task.id)}</a></td>'
                f'<td>{step_cell}</td><td><code>{html.escape(command)}</code></td></tr>'
            )
    return (
        '<section class="signature-view" data-origin="Derived view"><h3>AC Coverage</h3>'
        f'<p><strong>{html.escape(str(labels["check"]))}:</strong> {html.escape(str(labels["coverage_confirm"]))}</p>'
        f'<p><strong>{html.escape(str(labels["read"]))}:</strong> {html.escape(str(labels["coverage_read"]))}</p>'
        f'<p>{html.escape(str(labels["coverage_summary"]).format(tasks=len(document.tasks), steps=total_steps))}</p>'
        '<div class="table-scroll" role="region" tabindex="0" aria-label="AC Coverage">'
        f'<table><thead><tr><th>{html.escape(str(labels["explicit_item"]))}</th>'
        f'<th>{html.escape(str(labels["task"]))}</th><th>{html.escape(str(labels["steps"]))}</th>'
        f'<th>{html.escape(str(labels["verification"]))}</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></section>'
    )


def _runtime_atlas(
    bundle: ReviewBundle, document: PlanDocument, labels: Mapping[str, object]
) -> str:
    source = bundle.primary[0]
    english = re.compile(
        r"(?<![a-z0-9])(?:runtime|architecture|data|interfaces?|flows?|"
        r"servers?|authority|files?|remotes?|transactions?)(?![a-z0-9])",
        re.IGNORECASE,
    )
    korean = (
        "런타임", "아키텍처", "데이터", "인터페이스", "흐름",
        "서버", "권위", "파일", "리모트", "원격", "트랜잭션",
    )
    section_names = [
        name
        for name in document.sections
        if (english.search(name) or any(token in name for token in korean))
        and not name.startswith(("task:", "progress:"))
    ]
    body = "".join(
        f'<article data-runtime-section="{html.escape(name, quote=True)}">'
        f'<h4>{html.escape(name)}</h4>{render_markdown(_strip_mermaid(document.sections[name]))}</article>'
        for name in section_names
        if _strip_mermaid(document.sections[name])
    )
    if not body:
        body = f'<p>{html.escape(str(labels["runtime_empty"]))}</p>'
    return (
        '<section class="signature-view" data-origin="Plan source"><h3>Runtime Atlas</h3>'
        f'{_provenance(source)}'
        f'<p><strong>{html.escape(str(labels["check"]))}:</strong> {html.escape(str(labels["runtime_confirm"]))}</p>'
        f'<p><strong>{html.escape(str(labels["read"]))}:</strong> {html.escape(str(labels["runtime_read"]))}</p>'
        f'{body}</section>'
    )


def _main_task_detail(source: ReviewSource, document: PlanDocument) -> str:
    canonical = {"tasks", "작업", "태스크"}
    sections = [
        (name, value)
        for name, value in document.sections.items()
        if name.casefold() in canonical and _strip_mermaid(value)
    ]
    if not sections:
        return ""
    body = "".join(
        f'<h4>{html.escape(name)}</h4>{render_markdown(_strip_mermaid(value))}'
        for name, value in sections
    )
    key = f"{source.namespace}:{source.path}"
    return (
        '<details class="source-block source-detail" '
        f'data-main-task-detail="{html.escape(key, quote=True)}">'
        f'<summary><span>{html.escape(ORIGINS[source.role])}</span> · '
        f'<code>{html.escape(source.path)}</code> · '
        f'<code>{html.escape(source.namespace)}</code></summary>{body}</details>'
    )


def _auxiliary_detail(
    source: ReviewSource, document: PlanDocument, labels: Mapping[str, object]
) -> str:
    prefix = "progress" if source.role == "plan_progress" else "task"
    raw = document.sections.get(f"{prefix}:{source.path}", "")
    body = render_markdown(_strip_mermaid(raw)) if raw else ""
    detail = body or f'<p>{html.escape(str(labels["detail_empty"]))}</p>'
    key = f"{source.namespace}:{source.path}"
    return (
        f'<details class="source-block source-detail" data-source-detail="{html.escape(key, quote=True)}">'
        f'<summary><span>{html.escape(ORIGINS[source.role])}</span> · '
        f'<code>{html.escape(source.path)}</code> · <code>{html.escape(source.namespace)}</code></summary>'
        f'{detail}</details>'
    )


def _task_source_paths(
    source: ReviewSource,
    document: PlanDocument,
) -> Mapping[str, str]:
    paths: dict[str, str] = {}
    for path in document.task_paths:
        raw = document.sections.get(f"task:{path}", "")
        for match in re.finditer(r"^### Task ([0-9]+):", raw, re.MULTILINE):
            paths[f"Task{match.group(1)}"] = path
    return {
        task.id: paths.get(task.id, source.path)
        for task in document.tasks
    }


def _source_state_summary(
    source: ReviewSource,
    document: PlanDocument,
    labels: Mapping[str, object],
) -> str:
    task_paths = _task_source_paths(source, document)
    rows: list[str] = []
    for task in document.tasks:
        path = task_paths[task.id]
        if not task.steps:
            rows.append(
                f'<tr><td><a href="#{html.escape(source.namespace + "-" + task.id, quote=True)}">'
                f'{html.escape(task.id)}</a></td><td><code>{html.escape(path)}</code></td>'
                '<td>—</td><td>—</td></tr>'
            )
            continue
        for step in task.steps:
            state = "checked" if step.checked else "unchecked"
            target = f"{source.namespace}-{step.id}"
            rows.append(
                f'<tr><td><a href="#{html.escape(source.namespace + "-" + task.id, quote=True)}">'
                f'{html.escape(task.id)}</a></td><td><code>{html.escape(path)}</code></td>'
                f'<td><a href="#{html.escape(target, quote=True)}">{html.escape(step.id)}</a></td>'
                f'<td><span data-source-check-state="{state}">'
                f'{html.escape(str(labels[state]))}</span></td></tr>'
            )
    return (
        '<article class="source-block" data-origin="Plan source" data-source-state-summary>'
        f'<h3>{html.escape(str(labels["source_state_heading"]))}</h3>{_provenance(source)}'
        f'<p>{html.escape(str(labels["source_state_note"]))}</p>'
        f'<p><strong>{html.escape(str(labels["source_plan_status"]))}:</strong> '
        f'<code>{html.escape(document.status or "—")}</code></p>'
        '<div class="table-scroll" role="region" tabindex="0" '
        f'aria-label="{html.escape(str(labels["source_state_heading"]), quote=True)}">'
        f'<table><thead><tr><th>{html.escape(str(labels["task"]))}</th>'
        f'<th>{html.escape(str(labels["source_path"]))}</th>'
        f'<th>{html.escape(str(labels["steps"]))}</th>'
        f'<th>{html.escape(str(labels["source_check_state"]))}</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></article>'
    )


def _plan_panels(bundle: ReviewBundle, review_id: str, labels: Mapping[str, object]) -> dict[str, str]:
    plan_source, document = _primary_plan(bundle)
    completed = sum(step.checked for task in document.tasks for step in task.steps)
    total = sum(len(task.steps) for task in document.tasks)
    overview = (
        f'<h2>{html.escape(str(labels["plan_overview"]))}</h2>'
        f'<p><strong>{html.escape(str(labels["plan_title_label"]))}:</strong> {html.escape(document.title)}</p>'
        f'<p><strong>{html.escape(str(labels["goal"]))}:</strong> '
        f'{html.escape(document.goal or str(labels["goal_missing"]))}</p>'
        f'<p><strong>{html.escape(str(labels["status_label"]))}:</strong> {html.escape(document.status or "unrecorded")} · '
        f'<strong>{html.escape(str(labels["source_completion"]))}:</strong> {completed}/{total} '
        f'{html.escape(str(labels["steps_checked"]))}.</p>'
        f'<p>{html.escape(str(labels["read_order"]))}</p>'
        f'{_metric_strip(bundle)}{_count_table(bundle, labels)}'
        + _user_experience(plan_source, document)
    )
    constraint_sections = _governance_sections(plan_source, document)
    context_blocks = "".join(_spec_requirements(source, labels) for source in bundle.context)
    requirements = (
        f'<h2>{html.escape(str(labels["plan_requirements"]))}</h2>'
        f'{_provenance(plan_source)}{constraint_sections}'
        + _route_scope(plan_source, document, labels)
        + context_blocks
    )
    flows = (
        f'<h2>{html.escape(str(labels["plan_flows"]))}</h2>'
        + _route_map(document, plan_source.path, labels)
        + _source_diagrams(bundle, labels)
    )
    data = (
        f'<h2>{html.escape(str(labels["plan_data"]))}</h2>'
        + _runtime_atlas(bundle, document, labels)
        + _main_task_detail(plan_source, document)
        + f'<h3>{html.escape(str(labels["task_detail"]))}</h3>'
        + _task_index(bundle, plan_source, document, review_id, labels)
    )
    acceptance = (
        f'<h2>{html.escape(str(labels["plan_acceptance"]))}</h2>'
        + _coverage_table(bundle, plan_source, document, labels)
        + "".join(_spec_acceptance(source, review_id, labels) for source in bundle.context)
    )
    progress = _section(plan_source, "Progress History")
    auxiliary = "".join(
        _auxiliary_detail(source, document, labels) for source in bundle.primary[1:]
    )
    history = (
        f'<h2>{html.escape(str(labels["plan_history"]))}</h2>'
        + _source_state_summary(plan_source, document, labels)
        + _history_table(bundle, labels)
        + progress
        + auxiliary
    )
    return dict(zip(PANELS, (overview, requirements, flows, data, acceptance, history)))


def _history_table(bundle: ReviewBundle, labels: Mapping[str, object]) -> str:
    rows = "".join(
        '<tr>'
        f'<td>{html.escape(source.role)}</td><td><code>{html.escape(source.namespace)}</code></td>'
        f'<td><code>{html.escape(source.path)}</code></td><td><code>{html.escape(source.sha256)}</code></td>'
        '</tr>'
        for source in _source_sequence(bundle)
    )
    return (
        f'<div class="table-scroll" role="region" tabindex="0" aria-label="{html.escape(str(labels["provenance_aria"]), quote=True)}">'
        '<table><thead><tr><th>Role</th><th>Namespace</th><th>Path</th><th>SHA-256</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def _review_metadata(
    bundle: ReviewBundle,
    *,
    locale: str,
    generated_at: str,
    checkpoint: str,
    commit: str | None,
    rebuild_command: str,
    source_base: str,
    offline: bool,
    labels: Mapping[str, object],
) -> str:
    values = (
        ("mode", bundle.mode),
        ("locale", locale),
        ("generated_at", generated_at),
        ("checkpoint", checkpoint),
        ("commit", commit or "—"),
        ("rebuild_command", rebuild_command),
        ("source_base", source_base),
        ("offline", "true" if offline else "false"),
    )
    rows = "".join(
        f'<tr><th scope="row">{html.escape(field)}</th><td><code>{html.escape(value)}</code></td></tr>'
        for field, value in values
    )
    return (
        '<article class="source-block" data-review-metadata>'
        f'<h3>{html.escape(str(labels["metadata_heading"]))}</h3>'
        '<div class="table-scroll" role="region" tabindex="0" '
        f'aria-label="{html.escape(str(labels["metadata_aria"]), quote=True)}">'
        f'<table><thead><tr><th>{html.escape(str(labels["metadata_field"]))}</th>'
        f'<th>{html.escape(str(labels["metadata_value"]))}</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'{_count_table(bundle, labels)}</article>'
    )


def bundle_needs_mermaid(bundle: ReviewBundle) -> bool:
    """Return whether the snapshot renders at least one diagram."""

    if bundle.mermaid:
        return True
    if bundle.mode != "plan":
        return False
    _, document = _primary_plan(bundle)
    return bool(document.routes)


def _offline_mermaid() -> str:
    source = MERMAID_PATH.read_bytes()
    expected = None
    for line in MERMAID_CHECKSUM_PATH.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*") == MERMAID_PATH.name:
            expected = parts[0]
            break
    actual = hashlib.sha256(source).hexdigest()
    if expected is None or actual != expected:
        raise ValueError("vendored Mermaid checksum verification failed")
    text = source.decode("utf-8")
    if "</script" in text.lower():
        raise ValueError("vendored Mermaid contains an unsafe inline script terminator")
    return f'<script data-mermaid-delivery="offline">\n{text}\n</script>'


def _mermaid_loader(offline: bool, bundle: ReviewBundle) -> str:
    if not bundle_needs_mermaid(bundle):
        return ""
    if offline:
        return _offline_mermaid()
    return (
        '<script data-mermaid-delivery="cdn" '
        f'src="{html.escape(MERMAID_URL, quote=True)}"></script>'
    )


def _fill_template(template: str, values: Mapping[str, str]) -> str:
    placeholders = set(re.findall(r"\{\{([A-Z][A-Z0-9_]*)\}\}", template))
    missing = placeholders - set(values)
    extra = set(values) - placeholders
    if missing or extra:
        raise ValueError(
            f"viewer template contract mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
        )
    return re.sub(
        r"\{\{([A-Z][A-Z0-9_]*)\}\}",
        lambda match: values[match.group(1)],
        template,
    )


def render_review(
    bundle: ReviewBundle,
    review_id: str,
    locale: str,
    generated_at: str,
    checkpoint: str,
    commit: str | None,
    rebuild_command: str,
    source_base: str,
    offline: bool,
) -> str:
    """Render one deterministic Review Viewer from validated source models."""

    if bundle.mode not in {"spec", "plan"}:
        raise ValueError("Review Viewer mode must be spec or plan")
    if locale not in LABELS:
        raise ValueError("Review Viewer locale must be en or ko")
    if source_base != "../../../":
        raise ValueError("Review Viewer source_base must be ../../../")
    if not _source_sequence(bundle):
        raise ValueError("Review Viewer requires at least one source")
    labels = LABELS[locale]
    title = str(labels[f"{bundle.mode}_title"])
    panels = (
        _spec_panels(bundle, review_id, labels)
        if bundle.mode == "spec"
        else _plan_panels(bundle, review_id, labels)
    )
    panels["history"] += _review_metadata(
        bundle,
        locale=locale,
        generated_at=generated_at,
        checkpoint=checkpoint,
        commit=commit,
        rebuild_command=rebuild_command,
        source_base=source_base,
        offline=offline,
        labels=labels,
    )
    tabs = labels["tabs"]
    assert isinstance(tabs, tuple)
    content = "\n".join(
        _panel(panel_id, tabs[index], panels[panel_id])
        for index, panel_id in enumerate(PANELS)
    )
    manifest = _manifest(
        bundle,
        review_id=review_id,
        locale=locale,
        generated_at=generated_at,
        checkpoint=checkpoint,
        commit=commit,
        rebuild_command=rebuild_command,
        source_base=source_base,
        offline=offline,
    )
    status = bundle.primary[0].status or getattr(bundle.primary[0].document, "status", "") or bundle.mode
    values = {
        "LANG": locale,
        "TITLE": html.escape(title),
        "STATUS": html.escape(status),
        "GENERATED_LABEL": html.escape(str(labels["generated"])),
        "GENERATED": html.escape(generated_at),
        "SOURCE_SUMMARY": _source_summary(bundle, labels),
        "NAV_LABEL": html.escape(str(labels["nav"]), quote=True),
        "TAB_OVERVIEW": html.escape(tabs[0]),
        "TAB_REQUIREMENTS": html.escape(tabs[1]),
        "TAB_FLOWS": html.escape(tabs[2]),
        "TAB_DATA": html.escape(tabs[3]),
        "TAB_ACCEPTANCE": html.escape(tabs[4]),
        "TAB_HISTORY": html.escape(tabs[5]),
        "CONTENT": content,
        "SOURCE_MANIFEST": _json_for_html(manifest),
        "FRESHNESS_RUNTIME": FRESHNESS_RUNTIME_PATH.read_text(encoding="utf-8"),
        "MERMAID": _mermaid_loader(offline, bundle),
        "DIAGRAM_LABEL": html.escape(str(labels["diagram"]), quote=True),
        "MERMAID_ERROR": html.escape(str(labels["mermaid_error"]), quote=True),
    }
    result = _fill_template(TEMPLATE_PATH.read_text(encoding="utf-8"), values)
    return result.rstrip("\n") + "\n"
