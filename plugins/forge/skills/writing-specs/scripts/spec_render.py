"""Deterministic builder and checker for committed Forge Spec Pages."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import html
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Mapping, Sequence

from markdown_render import anchor_slug, render_markdown
from spec_model import Diagnostic, SpecDocument
from spec_validate import validate_repository


GENERATOR_VERSION = "forge-spec-pages/1"
ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets"
PAGE_TEMPLATE_PATH = ASSET_ROOT / "spec-page-template.html"
CATALOG_TEMPLATE_PATH = ASSET_ROOT / "spec-catalog-template.html"
RUNTIME_PATH = ASSET_ROOT / "spec-pages-runtime.mjs"
MERMAID_PATH = ASSET_ROOT / "mermaid.min.js"
_PLACEHOLDER_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
_MANIFEST_RE = re.compile(
    rb'<script type="application/json" id="forge-spec-manifest">(.*?)</script>',
    re.DOTALL,
)
_GENERATED_PAGE_MARKER = b'data-forge-spec-page="forge/spec-page@1"'


class RenderFailure(RuntimeError):
    """Raised before writes when validated sources cannot be rendered safely."""


@dataclass(frozen=True)
class PageManifest:
    schema: str
    generator: str
    source_path: str
    source_sha256: str
    locale: str
    asset_fingerprint: str


def _diagnostic(path: Path, code: str, message: str) -> Diagnostic:
    return Diagnostic(path.as_posix(), 1, code, message)


def _finish_bytes(text: str) -> bytes:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"
    return normalized.encode("utf-8")


def _json_for_html(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def _json_attribute(values: Sequence[str]) -> str:
    return html.escape(_json_for_html(list(values)), quote=True)


def _fill_template(template: str, values: Mapping[str, str]) -> str:
    placeholders = set(_PLACEHOLDER_RE.findall(template))
    missing = sorted(placeholders - set(values))
    extra = sorted(set(values) - placeholders)
    if missing or extra:
        raise RenderFailure(
            "Template placeholder mismatch: "
            f"missing={','.join(missing) or 'none'} extra={','.join(extra) or 'none'}"
        )
    return _PLACEHOLDER_RE.sub(lambda match: values[match.group(1)], template)


def _read_template(path: Path) -> tuple[str, bytes]:
    try:
        content = path.read_bytes()
        return content.decode("utf-8"), content
    except (OSError, UnicodeDecodeError) as error:
        raise RenderFailure(f"Cannot read UTF-8 template '{path.name}': {error.__class__.__name__}") from error


def _framed_hash(items: Sequence[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for name, content in items:
        encoded_name = name.encode("utf-8")
        digest.update(len(encoded_name).to_bytes(8, "big"))
        digest.update(encoded_name)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _asset_fingerprint(
    page_bytes: bytes,
    catalog_bytes: bytes,
    runtime_bytes: bytes,
    mermaid_bytes: bytes,
) -> str:
    return _framed_hash(
        (
            (PAGE_TEMPLATE_PATH.name, page_bytes),
            (CATALOG_TEMPLATE_PATH.name, catalog_bytes),
            (RUNTIME_PATH.name, runtime_bytes),
            (MERMAID_PATH.name, mermaid_bytes),
        )
    )


def _labels(locale: str) -> dict[str, str]:
    if locale == "ko":
        return {
            "summary": "요약",
            "flows": "시각 흐름",
            "requirements": "요구사항",
            "data": "데이터와 인터페이스",
            "acceptance": "승인 기준",
            "history": "결정과 변경 이력",
            "source": "Markdown source",
            "page": "Spec Page",
            "catalog_title": "구조화 Spec 목록",
            "catalog_intro": "현재 Markdown source metadata에서 계산된 읽기 전용 catalog다.",
            "search": "Spec 검색",
            "status": "상태",
            "kind": "종류",
            "area": "영역",
            "component": "컴포넌트",
            "all": "전체",
            "related": "관련 Spec",
            "covered_by": "검증 AC",
            "uncovered": "미커버",
            "metric_active_requirements": "활성 요구사항",
            "metric_criteria": "승인 기준",
            "metric_uncovered": "미커버 요구사항",
            "metric_tombstones": "폐기 요구사항",
            "metric_diagrams": "다이어그램",
            "outline": "이 절의 목차",
            "derived_relations": "frontmatter relatedSpecs에서 파생한 관계",
        }
    return {
        "summary": "Summary",
        "flows": "Visual flow",
        "requirements": "Requirements",
        "data": "Data & Interfaces",
        "acceptance": "Acceptance evidence",
        "history": "Decisions & History",
        "source": "Markdown source",
        "page": "Spec Page",
        "catalog_title": "Structured Specs",
        "catalog_intro": "A read-only catalog calculated from current Markdown source metadata.",
        "search": "Search specs",
        "status": "Status",
        "kind": "Kind",
        "area": "Area",
        "component": "Component",
        "all": "All",
        "related": "Related specs",
        "covered_by": "Covered by",
        "uncovered": "Uncovered",
        "metric_active_requirements": "Active requirements",
        "metric_criteria": "Acceptance criteria",
        "metric_uncovered": "Uncovered requirements",
        "metric_tombstones": "Removed requirements",
        "metric_diagrams": "Diagrams",
        "outline": "In this section",
        "derived_relations": "Relations derived from frontmatter relatedSpecs",
    }


def _tag_list(values: Sequence[str]) -> str:
    if not values:
        return '<span class="empty-value">—</span>'
    return "".join(f'<span class="tag">{html.escape(value, quote=True)}</span>' for value in values)


def _metadata(document: SpecDocument) -> str:
    labels = _labels(document.metadata.language)
    related = []
    for relation in document.metadata.related_specs:
        related.append(
            '<a class="relation" '
            f'href="../{html.escape(relation.id, quote=True)}/index.html">'
            f'{html.escape(relation.id, quote=True)} '
            f'<span>{html.escape(relation.relation, quote=True)}</span></a>'
        )
    related_html = "".join(related) or '<span class="empty-value">—</span>'
    rows = (
        ("Status", f'<span class="status status-{html.escape(document.metadata.status)}">{html.escape(document.metadata.status)}</span>'),
        ("Kind", html.escape(document.metadata.kind)),
        ("Areas", _tag_list(document.metadata.areas)),
        ("Components", _tag_list(document.metadata.components)),
        (labels["related"], related_html),
        ("Source SHA-256", f'<code>{document.source_sha256}</code>'),
        ("Schema", f'<code>{html.escape(document.metadata.schema)}</code>'),
        ("Generator", f'<code>{GENERATOR_VERSION}</code>'),
    )
    return "\n".join(
        f'<div class="meta-row"><dt>{html.escape(label)}</dt><dd>{value}</dd></div>'
        for label, value in rows
    )


def _requirements(document: SpecDocument) -> str:
    index = coverage_index(document)
    labels = _labels(document.metadata.language)
    rows = []
    for requirement in document.requirements:
        if requirement.removed:
            covered = '<span class="empty-value">—</span>'
            flags = ' data-removed="true"'
        else:
            criteria = index.get(requirement.id, ())
            if criteria:
                covered = ", ".join(
                    f'<a href="#{criterion}">{criterion}</a>' for criterion in criteria
                )
                flags = ""
            else:
                covered = f'<span class="uncovered">{html.escape(labels["uncovered"])}</span>'
                flags = ' data-uncovered="true"'
        rows.append(
            f'<tr id="{requirement.id}"{flags}>'
            f'<th scope="row"><a href="#{requirement.id}">{requirement.id}</a></th>'
            f'<td>{render_markdown(requirement.text)}</td>'
            f'<td>{covered}</td></tr>'
        )
    return (
        '<div class="table-scroll" role="region" aria-label="Requirements" tabindex="0">'
        '<table><thead><tr>'
        '<th scope="col">ID</th>'
        f'<th scope="col">{html.escape(labels["requirements"])}</th>'
        f'<th scope="col">{html.escape(labels["covered_by"])}</th>'
        '</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _acceptance(document: SpecDocument) -> str:
    rows = []
    for criterion in document.acceptance:
        references = ", ".join(
            f'<a href="#{requirement_id}">{requirement_id}</a>'
            for requirement_id in criterion.requirements
        )
        rows.append(
            f'<tr id="{criterion.id}"><th scope="row"><a href="#{criterion.id}">{criterion.id}</a></th>'
            f'<td>{references}</td><td>{render_markdown(criterion.text)}</td></tr>'
        )
    return (
        '<div class="table-scroll" role="region" aria-label="Acceptance criteria" tabindex="0">'
        '<table><thead><tr><th scope="col">ID</th><th scope="col">R</th><th scope="col">Criterion</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def page_needs_mermaid(document: SpecDocument) -> bool:
    """Return whether the rendered page contains at least one diagram."""

    if document.mermaid:
        return True
    return bool(
        not document.sections["Behavior & Flows"].strip()
        and related_specs_diagram(document)
    )


def coverage_index(document: SpecDocument) -> dict[str, tuple[str, ...]]:
    """Map each active requirement ID to the criteria that cite it."""

    citations: dict[str, list[str]] = {
        requirement.id: []
        for requirement in document.requirements
        if not requirement.removed
    }
    for criterion in document.acceptance:
        for requirement_id in criterion.requirements:
            if requirement_id in citations:
                citations[requirement_id].append(criterion.id)
    return {key: tuple(value) for key, value in citations.items()}


def page_metrics(document: SpecDocument) -> dict[str, int]:
    """Return the scannable counts shown in the page header."""

    index = coverage_index(document)
    return {
        "active_requirements": len(index),
        "criteria": len(document.acceptance),
        "tombstones": sum(1 for item in document.requirements if item.removed),
        "diagrams": len(document.mermaid),
        "uncovered": sum(1 for criteria in index.values() if not criteria),
    }


_METRIC_ORDER = (
    "active_requirements",
    "criteria",
    "uncovered",
    "tombstones",
    "diagrams",
)


def _metrics_markup(document: SpecDocument) -> str:
    labels = _labels(document.metadata.language)
    metrics = page_metrics(document)
    cells = []
    for key in _METRIC_ORDER:
        alert = ' data-alert="true"' if key == "uncovered" and metrics[key] else ""
        cells.append(
            f'<div class="metric" data-metric="{key}"{alert}>'
            f'<dt>{html.escape(labels[f"metric_{key}"])}</dt>'
            f"<dd>{metrics[key]}</dd></div>"
        )
    return f'<dl class="metrics">{"".join(cells)}</dl>'


_SUBHEADING_RE = re.compile(r"^(#{3,6}) (\S.*)$")
_OUTLINE_THRESHOLD = 3


def section_outline(body: str) -> tuple[tuple[str, str], ...]:
    """Return (anchor, text) pairs when a section has enough subheadings."""

    headings: list[tuple[str, str]] = []
    used: dict[str, int] = {}
    in_fence = False
    for line in body.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = _SUBHEADING_RE.match(line)
        if match:
            text = match.group(2).strip()
            headings.append((anchor_slug(text, used), text))
    if len(headings) < _OUTLINE_THRESHOLD:
        return ()
    return tuple(headings)


def _outline_markup(document: SpecDocument, section: str) -> str:
    outline = section_outline(document.sections[section])
    if not outline:
        return ""
    labels = _labels(document.metadata.language)
    items = "".join(
        f'<li><a href="#{anchor}">{html.escape(text)}</a></li>' for anchor, text in outline
    )
    return (
        f'<nav class="section-outline" aria-label="{html.escape(labels["outline"], quote=True)}">'
        f'<p class="outline-label">{html.escape(labels["outline"])}</p>'
        f"<ol>{items}</ol></nav>"
    )


def related_specs_diagram(document: SpecDocument) -> str:
    """Build a Mermaid source from the declared relatedSpecs entries only."""

    relations = document.metadata.related_specs
    if not relations:
        return ""
    lines = ["flowchart LR", f'    current["{document.metadata.id}"]']
    for index, relation in enumerate(relations, start=1):
        node = f"related{index}"
        lines.append(f'    {node}["{relation.id}"]')
        lines.append(f"    current -->|{relation.relation}| {node}")
    return "\n".join(lines)


def _flows(document: SpecDocument) -> str:
    body = document.sections["Behavior & Flows"]
    if body.strip():
        return render_markdown(body)
    derived = related_specs_diagram(document)
    if not derived:
        return ""
    labels = _labels(document.metadata.language)
    return (
        '<div class="derived-view">'
        f'<p class="derived-label">Derived view · {html.escape(labels["derived_relations"])}</p>'
        '<div class="diagram-scroll">'
        f'<pre class="mermaid">{html.escape(derived)}</pre>'
        "</div></div>"
    )


def catalog_relations_diagram(documents: Sequence[SpecDocument]) -> str:
    """Build the repository relation graph from declared relatedSpecs only."""

    known = {document.metadata.id for document in documents}
    edges: list[tuple[str, str, str]] = []
    for document in documents:
        for relation in document.metadata.related_specs:
            if relation.id in known:
                edges.append((document.metadata.id, relation.relation, relation.id))
    if not edges:
        return ""
    nodes = sorted({node for source, _, target in edges for node in (source, target)})
    aliases = {node: f"spec{index}" for index, node in enumerate(nodes, start=1)}
    lines = ["flowchart LR"]
    for node in nodes:
        lines.append(f'    {aliases[node]}["{node}"]')
    for source, relation, target in edges:
        lines.append(f"    {aliases[source]} -->|{relation}| {aliases[target]}")
    return "\n".join(lines)


def render_spec_page(
    document: SpecDocument,
    template: str,
    asset_fingerprint: str,
    runtime: str | None = None,
    mermaid: str | None = None,
) -> bytes:
    if runtime is None:
        runtime, _ = _read_template(RUNTIME_PATH)
    if mermaid is None:
        mermaid, _ = _read_template(MERMAID_PATH)
    labels = _labels(document.metadata.language)
    manifest = PageManifest(
        schema="forge/spec-page@1",
        generator=GENERATOR_VERSION,
        source_path=document.path.as_posix(),
        source_sha256=document.source_sha256,
        locale=document.metadata.language,
        asset_fingerprint=asset_fingerprint,
    )
    nav_items = tuple(
        item
        for item in (
            ("overview", labels["summary"]),
            ("flows", labels["flows"]),
            ("requirements", labels["requirements"]),
            ("data", labels["data"]),
            ("acceptance", labels["acceptance"]),
            ("history", labels["history"]),
        )
        if item[0] != "flows" or _flows(document)
    )
    navigation = "".join(
        f'<a href="#{target}">{html.escape(label)}</a>' for target, label in nav_items
    )
    return _finish_bytes(
        _fill_template(
            template,
            {
                "LANG": document.metadata.language,
                "TITLE": html.escape(document.title, quote=True),
                "MANIFEST": _json_for_html(asdict(manifest)),
                "METADATA": _metadata(document),
                "METRICS": _metrics_markup(document),
                "NAVIGATION": navigation,
                "SOURCE_LABEL": labels["source"],
                "OVERVIEW_LABEL": labels["summary"],
                "OVERVIEW": _outline_markup(document, "Overview")
                + render_markdown(document.sections["Overview"]),
                "FLOWS_SECTION": (
                    f'<section id="flows"><h2>{html.escape(labels["flows"])}</h2>{flows}</section>'
                    if (flows := _flows(document))
                    else ""
                ),
                "REQUIREMENTS_LABEL": labels["requirements"],
                "REQUIREMENTS": _requirements(document),
                "DATA_LABEL": labels["data"],
                "DATA": _outline_markup(document, "Data & Interfaces")
                + render_markdown(document.sections["Data & Interfaces"]),
                "ACCEPTANCE_LABEL": labels["acceptance"],
                "ACCEPTANCE": _acceptance(document),
                "HISTORY_LABEL": labels["history"],
                "HISTORY": render_markdown(document.sections["Decisions & History"]),
                "MERMAID_RUNTIME": (
                    f"<script>{mermaid}</script>" if page_needs_mermaid(document) else ""
                ),
                "SPEC_PAGES_RUNTIME": runtime,
            },
        )
    )


def _option(values: Sequence[str], all_label: str) -> str:
    options = [f'<option value="">{html.escape(all_label)}</option>']
    options.extend(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
        for value in sorted(set(values))
    )
    return "".join(options)


def _catalog_source_hash(documents: Sequence[SpecDocument]) -> str:
    return _framed_hash(
        tuple(
            (document.path.as_posix(), document.source_sha256.encode("ascii"))
            for document in documents
        )
    )


def _render_catalog(
    documents: Sequence[SpecDocument],
    template: str,
    asset_fingerprint: str,
    spec_root: Path,
    runtime: str,
    mermaid: str,
) -> bytes:
    locale = "ko" if any(document.metadata.language == "ko" for document in documents) else "en"
    labels = _labels(locale)
    manifest = PageManifest(
        schema="forge/spec-catalog@1",
        generator=GENERATOR_VERSION,
        source_path=spec_root.as_posix(),
        source_sha256=_catalog_source_hash(documents),
        locale=locale,
        asset_fingerprint=asset_fingerprint,
    )
    entries: list[str] = []
    for document in documents:
        metadata = document.metadata
        related = "".join(
            f'<a href="{html.escape(relation.id, quote=True)}/index.html">'
            f'{html.escape(relation.id)} <span>{html.escape(relation.relation)}</span></a>'
            for relation in metadata.related_specs
        ) or '<span class="empty-value">—</span>'
        entries.append(
            '<article class="catalog-entry" '
            f'data-spec-id="{html.escape(metadata.id, quote=True)}" '
            f'data-status="{html.escape(metadata.status, quote=True)}" '
            f'data-kind="{html.escape(metadata.kind, quote=True)}" '
            f'data-areas="{_json_attribute(metadata.areas)}" '
            f'data-components="{_json_attribute(metadata.components)}" '
            f'data-related="{_json_attribute(tuple(item.id for item in metadata.related_specs))}">'
            f'<p class="catalog-id">{html.escape(metadata.id)}</p>'
            f'<h2><a href="{html.escape(metadata.id, quote=True)}/index.html">{html.escape(document.title)}</a></h2>'
            f'<p class="catalog-state"><span class="status status-{html.escape(metadata.status)}">{html.escape(metadata.status)}</span> '
            f'<span>{html.escape(metadata.kind)}</span></p>'
            f'<div class="catalog-tags">{_tag_list(metadata.areas)}{_tag_list(metadata.components)}</div>'
            f'<p class="catalog-relations">{html.escape(labels["related"])}: {related}</p>'
            '<p class="catalog-links">'
            f'<a href="{html.escape(metadata.id, quote=True)}/spec.md">{html.escape(labels["source"])}</a>'
            f'<a href="{html.escape(metadata.id, quote=True)}/index.html">{html.escape(labels["page"])}</a>'
            "</p></article>"
        )
    relations = catalog_relations_diagram(documents)
    if relations:
        relations_markup = (
            '<section class="shell relations" aria-label="Spec relations">'
            f'<p class="derived-label">Derived view · {html.escape(labels["derived_relations"])}</p>'
            '<div class="diagram-scroll">'
            f'<pre class="mermaid">{html.escape(relations)}</pre>'
            "</div></section>"
        )
        mermaid_markup = f"<script>{mermaid}</script>"
    else:
        relations_markup = ""
        mermaid_markup = ""
    values = {
        "LANG": locale,
        "TITLE": html.escape(labels["catalog_title"]),
        "INTRO": html.escape(labels["catalog_intro"]),
        "MANIFEST": _json_for_html(asdict(manifest)),
        "SEARCH_LABEL": html.escape(labels["search"]),
        "STATUS_LABEL": html.escape(labels["status"]),
        "KIND_LABEL": html.escape(labels["kind"]),
        "AREA_LABEL": html.escape(labels["area"]),
        "COMPONENT_LABEL": html.escape(labels["component"]),
        "STATUS_OPTIONS": _option([item.metadata.status for item in documents], labels["all"]),
        "KIND_OPTIONS": _option([item.metadata.kind for item in documents], labels["all"]),
        "AREA_OPTIONS": _option(
            [value for item in documents for value in item.metadata.areas], labels["all"]
        ),
        "COMPONENT_OPTIONS": _option(
            [value for item in documents for value in item.metadata.components], labels["all"]
        ),
        "ENTRIES": "\n".join(entries),
        "RELATIONS": relations_markup,
        "MERMAID_RUNTIME": mermaid_markup,
        "SPEC_PAGES_RUNTIME": runtime,
    }
    return _finish_bytes(_fill_template(template, values))


def expected_outputs(
    root: Path,
    documents: Sequence[SpecDocument],
) -> Mapping[Path, bytes]:
    """Return the complete absolute output map in path order without writing."""

    repository = root.resolve()
    ordered_documents = tuple(sorted(documents, key=lambda item: item.path.as_posix()))
    spec_roots = {document.path.parent.parent for document in ordered_documents}
    if len(spec_roots) > 1:
        raise RenderFailure("All documents must belong to one repository spec root.")
    spec_root = next(iter(spec_roots), Path("docs/specs"))
    try:
        resolved_spec_root = (repository / spec_root).resolve()
        resolved_spec_root.relative_to(repository)
    except ValueError as error:
        raise RenderFailure("The spec root must remain inside the repository root.") from error

    page_template, page_bytes = _read_template(PAGE_TEMPLATE_PATH)
    catalog_template, catalog_bytes = _read_template(CATALOG_TEMPLATE_PATH)
    runtime, runtime_bytes = _read_template(RUNTIME_PATH)
    mermaid, mermaid_bytes = _read_template(MERMAID_PATH)
    fingerprint = _asset_fingerprint(
        page_bytes,
        catalog_bytes,
        runtime_bytes,
        mermaid_bytes,
    )
    outputs: dict[Path, bytes] = {}
    for document in ordered_documents:
        output = (repository / document.path.parent / "index.html").resolve()
        try:
            output.relative_to(repository)
        except ValueError as error:
            raise RenderFailure("A generated page path escaped the repository root.") from error
        outputs[output] = render_spec_page(
            document,
            page_template,
            fingerprint,
            runtime,
            mermaid,
        )
    catalog_path = resolved_spec_root / "index.html"
    outputs[catalog_path] = _render_catalog(
        ordered_documents,
        catalog_template,
        fingerprint,
        spec_root,
        runtime,
        mermaid,
    )
    return {path: outputs[path] for path in sorted(outputs)}


def _shared_contract(content: bytes) -> tuple[str, str] | None:
    match = _MANIFEST_RE.search(content)
    if match is None:
        return None
    try:
        payload = json.loads(match.group(1).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
        return None
    generator = payload.get("generator")
    fingerprint = payload.get("asset_fingerprint")
    if not isinstance(generator, str) or not isinstance(fingerprint, str):
        return None
    return generator, fingerprint


def _expected_shared_contract(expected_catalog: bytes) -> tuple[str, str]:
    contract = _shared_contract(expected_catalog)
    if contract is None:
        raise RenderFailure("The generated catalog is missing a valid manifest.")
    return contract


def _normalize_changed(repository: Path, spec_root: Path, changed: Path) -> Path:
    candidate = changed.resolve() if changed.is_absolute() else (repository / changed).resolve()
    resolved_spec_root = (repository / spec_root).resolve()
    try:
        relative = candidate.relative_to(resolved_spec_root)
    except ValueError as error:
        raise RenderFailure("The changed source must remain inside the spec root.") from error
    if len(relative.parts) != 2 or relative.name != "spec.md":
        raise RenderFailure("The changed source must name an exact NNN-slug/spec.md path.")
    return candidate.relative_to(repository)


def _orphan_pages(spec_root: Path, expected: set[Path]) -> tuple[Path, ...]:
    resolved_root = spec_root.resolve()
    result: list[Path] = []
    for path in sorted(spec_root.glob("*/index.html")):
        try:
            lexical_parent = path.parent.relative_to(spec_root)
        except ValueError:
            continue
        if len(lexical_parent.parts) != 1 or path.parent.is_symlink():
            continue
        try:
            resolved_path = path.resolve()
            path.parent.resolve().relative_to(resolved_root)
            resolved_path.relative_to(resolved_root)
        except ValueError:
            continue
        if resolved_path in expected:
            continue
        try:
            content = path.read_bytes()
        except OSError:
            continue
        if _GENERATED_PAGE_MARKER in content:
            result.append(path)
    return tuple(result)


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _stage_bytes(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.stage.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        return Path(temporary)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def _backup_path(path: Path) -> Path:
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.backup.", dir=path.parent
    )
    os.close(descriptor)
    os.unlink(temporary)
    return Path(temporary)


def _cleanup_paths(paths: Sequence[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        try:
            if path.exists() or path.is_symlink():
                path.unlink()
        except OSError as error:
            errors.append(f"{path.name}: {error.__class__.__name__}")
    return errors


def _publish_transaction(
    replacements: Mapping[Path, bytes],
    deletions: Sequence[Path],
) -> None:
    ordered_replacements = tuple(sorted(replacements))
    replacement_set = set(ordered_replacements)
    ordered_deletions = tuple(sorted(set(deletions) - replacement_set))
    affected = ordered_replacements + ordered_deletions
    directories = tuple(sorted({path.parent for path in affected}))
    staged: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    published: set[Path] = set()

    try:
        for path in ordered_replacements:
            staged[path] = _stage_bytes(path, replacements[path])

        for path in affected:
            if not path.exists() and not path.is_symlink():
                continue
            backup = _backup_path(path)
            os.replace(path, backup)
            backups[path] = backup

        for path in ordered_replacements:
            os.replace(staged[path], path)
            published.add(path)

        for directory in directories:
            _fsync_directory(directory)
    except OSError as error:
        rollback_errors: list[str] = []
        for path in reversed(ordered_replacements):
            if path not in published:
                continue
            try:
                if path.exists() or path.is_symlink():
                    path.unlink()
            except OSError as rollback_error:
                rollback_errors.append(
                    f"remove {path.name}: {rollback_error.__class__.__name__}"
                )
        for path in reversed(affected):
            backup = backups.get(path)
            if backup is None or (not backup.exists() and not backup.is_symlink()):
                continue
            try:
                os.replace(backup, path)
            except OSError as rollback_error:
                rollback_errors.append(
                    f"restore {path.name}: {rollback_error.__class__.__name__}"
                )
        rollback_errors.extend(_cleanup_paths(tuple(staged.values())))
        rollback_errors.extend(_cleanup_paths(tuple(backups.values())))
        for directory in directories:
            try:
                _fsync_directory(directory)
            except OSError as rollback_error:
                rollback_errors.append(
                    f"fsync {directory.name}: {rollback_error.__class__.__name__}"
                )
        detail = f"Spec Page transaction failed: {error}"
        if rollback_errors:
            detail += "; rollback incomplete: " + ", ".join(rollback_errors)
        raise RenderFailure(detail) from error

    cleanup_errors = _cleanup_paths(tuple(backups.values()))
    cleanup_errors.extend(_cleanup_paths(tuple(staged.values())))
    for directory in directories:
        try:
            _fsync_directory(directory)
        except OSError as error:
            cleanup_errors.append(f"fsync {directory.name}: {error.__class__.__name__}")
    if cleanup_errors:
        raise RenderFailure(
            "Spec Page transaction committed but cleanup failed: "
            + ", ".join(cleanup_errors)
        )


def atomic_write(path: Path, content: bytes) -> None:
    _publish_transaction({path: content}, ())


def build_pages(
    repo_root: Path,
    spec_root: Path,
    changed: Path | None,
    offline: bool,
) -> tuple[Path, ...]:
    """Validate, compute every byte, then atomically replace selected pages."""

    if not offline:
        raise RenderFailure("Spec Pages must be built with offline assets.")
    repository = repo_root.resolve()
    relative_spec_root = spec_root
    if spec_root.is_absolute():
        try:
            relative_spec_root = spec_root.resolve().relative_to(repository)
        except ValueError as error:
            raise RenderFailure("The spec root must remain inside the repository root.") from error
    result = validate_repository(repository, relative_spec_root)
    if result.diagnostics:
        summary = "\n".join(
            f"{item.path}:{item.line}: {item.code} {item.message}"
            for item in result.diagnostics
        )
        raise RenderFailure(f"Spec repository validation failed:\n{summary}")

    outputs = expected_outputs(repository, result.documents)
    resolved_spec_root = (repository / relative_spec_root).resolve()
    catalog = resolved_spec_root / "index.html"
    expected_paths = set(outputs)
    orphans = _orphan_pages(resolved_spec_root, expected_paths)
    normalized_changed = (
        _normalize_changed(repository, relative_spec_root, changed)
        if changed is not None
        else None
    )

    full_build = normalized_changed is None
    if normalized_changed is not None:
        expected_contract = _expected_shared_contract(outputs[catalog])
        try:
            current_contract = _shared_contract(catalog.read_bytes())
        except OSError:
            current_contract = None
        full_build = current_contract != expected_contract

    deletions: tuple[Path, ...]
    if full_build:
        selected = tuple(outputs)
        deletions = orphans
    else:
        changed_page = repository / normalized_changed.parent / "index.html"
        selected = tuple(path for path in sorted((changed_page, catalog)) if path in outputs)
        deletions = (changed_page,) if changed_page.exists() and changed_page not in outputs else ()

    replacements: dict[Path, bytes] = {}
    for path in selected:
        content = outputs[path]
        try:
            current = path.read_bytes()
        except OSError:
            current = None
        if current != content:
            replacements[path] = content
    _publish_transaction(replacements, deletions)
    return selected


def check_pages(repo_root: Path, spec_root: Path) -> tuple[Diagnostic, ...]:
    """Compare regenerated expected bytes without modifying the repository."""

    repository = repo_root.resolve()
    relative_spec_root = spec_root
    if spec_root.is_absolute():
        try:
            relative_spec_root = spec_root.resolve().relative_to(repository)
        except ValueError:
            return (
                _diagnostic(
                    spec_root,
                    "SPEC_ROOT_PATH_ESCAPE",
                    "The spec root must remain inside the repository root.",
                ),
            )
    result = validate_repository(repository, relative_spec_root)
    if result.diagnostics:
        return result.diagnostics
    try:
        outputs = expected_outputs(repository, result.documents)
    except RenderFailure as error:
        return (
            _diagnostic(
                relative_spec_root,
                "SPEC_PAGE_RENDER",
                str(error),
            ),
        )

    diagnostics: list[Diagnostic] = []
    for path, expected in outputs.items():
        relative = path.relative_to(repository)
        try:
            actual = path.read_bytes()
        except OSError:
            diagnostics.append(
                _diagnostic(relative, "SPEC_PAGE_MISSING", "The generated Spec Page is missing.")
            )
            continue
        if actual != expected:
            diagnostics.append(
                _diagnostic(
                    relative,
                    "SPEC_PAGE_STALE",
                    "The generated Spec Page does not match regenerated expected bytes.",
                )
            )

    resolved_spec_root = (repository / relative_spec_root).resolve()
    for orphan in _orphan_pages(resolved_spec_root, set(outputs)):
        diagnostics.append(
            _diagnostic(
                orphan.relative_to(repository),
                "SPEC_PAGE_ORPHAN",
                "The generated Spec Page has no structured source.",
            )
        )
    return tuple(sorted(diagnostics))
