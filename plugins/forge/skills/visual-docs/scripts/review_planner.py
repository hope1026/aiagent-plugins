"""Validated presentation planning for requested Visual Docs."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

from review_ir import SemanticIR


INTENTS = frozenset(("review", "approval", "implementation", "comparison", "execution", "status"))
AUDIENCES = frozenset(("mixed", "product", "engineering", "operations"))
KINDS = frozenset(("brief", "plan", "spec", "project"))
EXPORT_MODES = frozenset(("standalone",))
DISCLOSURES = frozenset(("open", "collapsed", "summary"))

PROFILE_COMPONENTS: Mapping[str, tuple[str, ...]] = {
    "generic": ("summary", "outline", "source-detail", "provenance"),
    "brief.summary": ("brief-overview", "brief-scope", "brief-done", "source-detail"),
    "spec.system": (
        "system-overview",
        "runtime-responsibility",
        "interface-table",
        "acceptance-coverage",
        "spec-navigator",
    ),
    "spec.workflow": ("state-map", "exception-matrix", "acceptance-coverage", "source-detail"),
    "spec.api": ("interface-table", "sequence", "exception-matrix", "source-detail"),
    "spec.architecture": ("relation-graph", "runtime-atlas", "decision-matrix", "source-detail"),
    "spec.policy": ("decision-matrix", "acceptance-coverage", "source-detail"),
    "spec.migration": ("change-route", "dependency-map", "verification", "source-detail"),
    "plan.execution": ("route-map", "dependency-map", "runtime-atlas", "verification", "source-detail"),
    "plan.status": ("progress", "blockers", "next-actions", "source-detail"),
    "project.handbook": (
        "project-overview",
        "spec-index",
        "structure-responsibility",
        "developer-information",
    ),
    "project.structure": ("structure-responsibility", "developer-information"),
    "project.spec-detail": ("spec-index", "developer-information"),
    "comparison": ("delta-matrix", "acceptance-coverage", "provenance", "source-detail"),
}

_INTENT_COMPONENTS: Mapping[tuple[str, str], tuple[str, ...]] = {
    ("spec.workflow", "implementation"): (
        "runtime-atlas",
        "state-map",
        "acceptance-coverage",
        "source-detail",
    ),
    ("spec.workflow", "review"): (
        "summary",
        "state-map",
        "acceptance-coverage",
        "source-detail",
    ),
}

_COMPONENT_ENTITY_TYPES: Mapping[str, frozenset[str]] = {
    "system-overview": frozenset(),
    "runtime-responsibility": frozenset(("interface",)),
    "state-map": frozenset(("mermaid",)),
    "sequence": frozenset(("mermaid",)),
    "interface-table": frozenset(("interface",)),
    "exception-matrix": frozenset(("acceptance", "decision")),
    "relation-graph": frozenset(("requirement", "acceptance", "task")),
    "route-map": frozenset(("task",)),
    "dependency-map": frozenset(("task",)),
    "runtime-atlas": frozenset(("interface", "task", "mermaid")),
    "progress": frozenset(("task", "step")),
    "blockers": frozenset(("task", "step")),
    "next-actions": frozenset(("task", "step")),
    "acceptance-coverage": frozenset(("requirement", "acceptance", "task", "step")),
    "decision-matrix": frozenset(("decision",)),
    "change-route": frozenset(("task", "decision")),
    "verification": frozenset(("acceptance", "step")),
    "delta-matrix": frozenset(("requirement", "acceptance")),
    "brief-overview": frozenset(("brief-goal",)),
    "brief-scope": frozenset(("brief-scope", "brief-out-of-scope")),
    "brief-done": frozenset(("brief-done-check",)),
    "project-overview": frozenset(("project-overview", "project-capabilities")),
    "capability-map": frozenset(("project-capabilities",)),
    "spec-index": frozenset(
        ("requirement", "acceptance", "mermaid", "decision", "interface")
    ),
    "structure-responsibility": frozenset(("project-structure",)),
}
_KEY_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")


@dataclass(frozen=True)
class ViewContext:
    kind: str
    spec_kind: str
    subtype: str | None
    intent: str
    audience: str
    locale: str
    export_mode: str

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"unsupported document kind: {self.kind}")
        if self.intent not in INTENTS:
            raise ValueError(f"unsupported review intent: {self.intent}")
        if self.audience not in AUDIENCES:
            raise ValueError(f"unsupported review audience: {self.audience}")
        if self.export_mode not in EXPORT_MODES:
            raise ValueError(f"unsupported export mode: {self.export_mode}")


@dataclass(frozen=True)
class ComponentPlan:
    component: str
    refs: tuple[str, ...]
    orientation_key: str
    disclosure: str


@dataclass(frozen=True)
class PresentationPlan:
    profile: str
    primary_question_key: str
    components: tuple[ComponentPlan, ...]


@dataclass(frozen=True, order=True)
class PlanDiagnostic:
    code: str
    message: str


def _decode_presentation_plan(
    payload: Mapping[str, object]
) -> tuple[PresentationPlan | None, tuple[PlanDiagnostic, ...]]:
    if "authored_copy" in payload:
        return None, (
            PlanDiagnostic(
                "VIEW_PLAN_AUTHORED_COPY",
                "Presentation Plans cannot contain authored copy or markup.",
            ),
        )
    if set(payload) != {"profile", "primary_question_key", "components"}:
        return None, (
            PlanDiagnostic(
                "VIEW_PLAN_SCHEMA", "Presentation Plan fields do not match the strict schema."
            ),
        )
    profile = payload.get("profile")
    question = payload.get("primary_question_key")
    raw_components = payload.get("components")
    if (
        not isinstance(profile, str)
        or not isinstance(question, str)
        or not isinstance(raw_components, (list, tuple))
    ):
        return None, (
            PlanDiagnostic(
                "VIEW_PLAN_SCHEMA", "Presentation Plan field types are invalid."
            ),
        )
    components: list[ComponentPlan] = []
    for raw_component in raw_components:
        if not isinstance(raw_component, Mapping) or set(raw_component) != {
            "component",
            "refs",
            "orientation_key",
            "disclosure",
        }:
            return None, (
                PlanDiagnostic(
                    "VIEW_PLAN_SCHEMA", "Component fields do not match the strict schema."
                ),
            )
        component = raw_component.get("component")
        refs = raw_component.get("refs")
        orientation = raw_component.get("orientation_key")
        disclosure = raw_component.get("disclosure")
        if (
            not isinstance(component, str)
            or not isinstance(refs, (list, tuple))
            or not all(isinstance(reference, str) for reference in refs)
            or not isinstance(orientation, str)
            or not isinstance(disclosure, str)
        ):
            return None, (
                PlanDiagnostic(
                    "VIEW_PLAN_SCHEMA", "Component field types are invalid."
                ),
            )
        components.append(
            ComponentPlan(component, tuple(refs), orientation, disclosure)
        )
    return PresentationPlan(profile, question, tuple(components)), ()


def select_presentation_plan(ir: SemanticIR, context: ViewContext) -> PresentationPlan:
    has_comparison = any(document.role == "comparison_spec" for document in ir.documents)
    if context.intent == "comparison" or has_comparison:
        profile = "comparison"
    elif context.kind == "brief":
        profile = "brief.summary"
    elif context.kind == "plan":
        profile = "plan.status" if context.intent == "status" else "plan.execution"
    elif context.kind == "project":
        if context.subtype == "structure":
            profile = "project.structure"
        elif context.subtype == "spec-detail":
            profile = "project.spec-detail"
        else:
            profile = "project.handbook"
    elif context.subtype in {"workflow", "api", "architecture", "policy", "migration"}:
        profile = f"spec.{context.subtype}"
    elif context.spec_kind == "policy":
        profile = "spec.policy"
    elif context.spec_kind == "system":
        profile = "spec.system"
    else:
        profile = "generic"

    component_ids = _INTENT_COMPONENTS.get(
        (profile, context.intent), PROFILE_COMPONENTS[profile]
    )
    entities = [entity for document in ir.documents for entity in document.entities]
    blocks = [block for document in ir.documents for block in document.blocks]
    represented_blocks: set[str] = set()
    components: list[ComponentPlan] = []
    for component_id in component_ids:
        if component_id == "spec-navigator":
            refs = tuple(block.key for block in blocks)
        elif component_id in {"source-detail", "developer-information"}:
            refs = tuple(
                block.key for block in blocks if block.key not in represented_blocks
            )
        elif component_id == "spec-index":
            declared_namespaces = {
                document.namespace
                for document in ir.documents
                if document.role == "declared_spec"
            }
            refs = tuple(
                block.key
                for block in blocks
                if block.source_namespace in declared_namespaces
            )
            represented_blocks.update(refs)
        else:
            entity_types = _COMPONENT_ENTITY_TYPES.get(component_id, frozenset())
            selected = [
                entity for entity in entities if entity.entity_type in entity_types
            ]
            refs = tuple(entity.key for entity in selected)
            represented_blocks.update(entity.block_key for entity in selected)
        if component_id in {"source-detail", "developer-information", "spec-navigator"}:
            represented_blocks.update(refs)
        components.append(
            ComponentPlan(
                component=component_id,
                refs=refs,
                orientation_key=f"{component_id}.orientation",
                disclosure=(
                    "collapsed"
                    if component_id in {"source-detail", "developer-information"}
                    else "open"
                ),
            )
        )
    return PresentationPlan(
        profile=profile,
        primary_question_key=f"{profile}.{context.intent}",
        components=tuple(components),
    )


def validate_presentation_plan(
    ir: SemanticIR, plan: PresentationPlan | Mapping[str, object]
) -> tuple[PlanDiagnostic, ...]:
    if isinstance(plan, Mapping):
        decoded, decoding_diagnostics = _decode_presentation_plan(plan)
        if decoded is None:
            return decoding_diagnostics
        plan = decoded

    diagnostics: list[PlanDiagnostic] = []
    if plan.profile not in PROFILE_COMPONENTS:
        diagnostics.append(
            PlanDiagnostic("VIEW_PLAN_PROFILE", f"Unknown profile: {plan.profile}")
        )
    if _KEY_RE.fullmatch(plan.primary_question_key) is None:
        diagnostics.append(
            PlanDiagnostic(
                "VIEW_PLAN_AUTHORED_COPY",
                "primary_question_key must be a registered identifier, not authored copy.",
            )
        )

    blocks = {
        block.key: block for document in ir.documents for block in document.blocks
    }
    entities = {
        entity.key: entity for document in ir.documents for entity in document.entities
    }
    allowed_components = {
        component
        for components in PROFILE_COMPONENTS.values()
        for component in components
    } | {
        component
        for components in _INTENT_COMPONENTS.values()
        for component in components
    }
    represented: set[str] = set()
    direct_block_owners: dict[str, str] = {}
    for component in plan.components:
        if component.component not in allowed_components:
            diagnostics.append(
                PlanDiagnostic(
                    "VIEW_PLAN_COMPONENT", f"Unknown component: {component.component}"
                )
            )
        if component.disclosure not in DISCLOSURES:
            diagnostics.append(
                PlanDiagnostic(
                    "VIEW_PLAN_DISCLOSURE",
                    f"Unknown disclosure: {component.disclosure}",
                )
            )
        if _KEY_RE.fullmatch(component.orientation_key) is None:
            diagnostics.append(
                PlanDiagnostic(
                    "VIEW_PLAN_AUTHORED_COPY",
                    "orientation_key must be a registered identifier, not authored copy.",
                )
            )
        for reference in component.refs:
            if reference in blocks:
                owner = direct_block_owners.get(reference)
                if owner is not None and owner != component.component:
                    diagnostics.append(
                        PlanDiagnostic(
                            "VIEW_PLAN_BLOCK_DUPLICATE",
                            f"Block {reference} is assigned to multiple components.",
                        )
                    )
                direct_block_owners[reference] = component.component
                represented.add(reference)
            elif reference in entities:
                represented.add(entities[reference].block_key)
            else:
                diagnostics.append(
                    PlanDiagnostic(
                        "VIEW_PLAN_DANGLING_REF", f"Unknown source reference: {reference}"
                    )
                )
    if set(blocks) - represented:
        diagnostics.append(
            PlanDiagnostic(
                "VIEW_PLAN_UNCOVERED_BLOCK",
                "Presentation Plan must cover every selected source block.",
            )
        )
    return tuple(sorted(set(diagnostics)))
