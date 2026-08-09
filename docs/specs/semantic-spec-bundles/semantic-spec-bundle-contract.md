---
schema: forge/spec@3
role: root
status: approved
language: ko
kind: system
areas: ["forge","specs"]
components: ["writing-specs","spec-docs"]
relatedSpecs: [{"path":"docs/specs/review-viewer-lifecycle/","relation":"relatedTo"}]
---

# 의미 기반 Spec Bundle 계약

## Documents

- root: [의미 기반 Spec Bundle 계약](semantic-spec-bundle-contract.md)
- contract: [문서 작성과 파일 구성](authoring-and-file-organization.md)
- contract: [문장 추적성과 검증](statement-traceability-and-validation.md)
- contract: [Lifecycle Consumer와 Migration](lifecycle-consumers-and-migration.md)
- history: [결정과 변경 이력](decisions-and-change-history.md)

## Overview

Forge의 spec과 plan은 Markdown을 유일한 기본 산출물과 source of truth로 유지해야 한다. 하나의 Canonical Spec은 의미가 드러나는 directory 안에 관련 Markdown을 묶은 Spec Bundle이다. Bundle metadata, full-statement traceability와 lifecycle gate는 기계적으로 검증하되, 서로 다른 feature·workflow·API·architecture·policy·migration 문서를 하나의 파일이나 화면 순서에 강제하지 않는다.

HTML은 일반적인 spec 작성, plan 작성, 승인, handoff, 실행 checkpoint 또는 lifecycle status 변경에서 생성하지 않는다. 사람이 보기 좋은 별도 화면이 필요할 때 사용자가 `review-viewer`를 명시적으로 요청해야만 `docs/specs/review-viewer-lifecycle/`의 계약에 따라 로컬 Review Viewer를 생성한다.

비목표:
- HTML을 spec의 편집 가능한 source of truth로 만들지 않는다.
- source에 없는 요구사항, 책임, 관계, 결정을 generated page에 추가하지 않는다.
- Markdown의 서술 순서를 Viewer layout에 맞추도록 강제하지 않는다.
- spec이나 plan 변경을 HTML 생성 요청으로 추론하지 않는다.
- source 옆 `index.html`, `view.html` 또는 repository catalog HTML을 상시 관리하지 않는다.
- Review Viewer 생성만으로 spec 승인 또는 구현 완료를 선언하지 않는다.

검토한 접근안:

| 접근안 | 장점 | 단점 | 결정 |
|---|---|---|---|
| Markdown-only lifecycle과 요청형 Review Viewer | 기본 작업은 source만 변경하고 필요한 검토에서만 HTML을 만든다 | 평상시에는 Markdown reader의 가독성에 의존한다 | 채택 |
| committed Spec Pages 상시 동기화 | 항상 HTML 탐색 화면이 존재한다 | source 변경마다 대형 generated diff와 runtime 중복이 생긴다 | 제외 |
| 문서마다 맞춤 HTML을 직접 작성 | 문서별 표현 자유도가 가장 높다 | 일관성·검증·유지보수 비용과 source drift가 커진다 | 제외 |
| 외부 문서 서비스로 동기화 | 검색과 공유 기능이 풍부하다 | 권한, 배포, 양방향 drift가 새 운영 의존성이 된다 | 제외 |

## Behavior & Flows

일반적인 spec·plan 작성과 요청형 Viewer 경계:

```mermaid
flowchart TD
    A["Spec Bundle 또는 plan.md 작성·변경"] --> B["Markdown source validation·자체 검토"]
    B -->|실패| C["source 오류 보고와 lifecycle 중단"]
    B -->|성공| D["Markdown으로 승인 또는 handoff"]
    D --> E{"사용자가 review-viewer를 명시적으로 요청했는가?"}
    E -->|아니오| F["HTML 0개"]
    E -->|예| G["요청형 Review Viewer 생성"]
```

Markdown source와 요청형 Review Viewer의 lifecycle:

```mermaid
flowchart LR
    S["Spec Bundle source of truth"] -. 사용자 명시 요청 .-> R["Review Viewer spec mode"]
    L["plan source 집합"] -. 사용자 명시 요청 .-> V["Review Viewer plan mode"]
    S -. Related Specs context .-> V
```

일괄 migration cutover:

```mermaid
flowchart TD
    A["legacy spec inventory와 mapping 고정"] --> B["새 구조를 staging에서 일괄 생성"]
    B --> C["전체 schema·R/AC·link validation"]
    C -->|실패| D["기존 구조 유지와 rollback"]
    C -->|성공| E["tracked generated HTML inventory 제거"]
    E -->|실패| D
    E -->|성공| F["instruction과 lifecycle consumer 동시 전환"]
    F --> G["legacy active format 제거"]
```

활성 spec supersession transaction:

```mermaid
flowchart TD
    A["current-state replacement를 draft로 작성"] --> B["사용자 승인"]
    B --> C["baseline identity·SHA와 evidence를 transition에 기록"]
    C --> D["old source 제거와 replacement bundle·reference 갱신"]
    D --> E["repository validation"]
    E -->|실패| F["기존 identity 유지"]
    E -->|성공| G["현재 spec과 별도 historical evidence를 함께 commit"]
```

## Data & Interfaces

`forge/spec@3` root metadata:

| Field | Type | 필수 | 제약 |
|---|---|---:|---|
| `schema` | string | 예 | 정확히 `forge/spec@3` |
| `role` | string | 예 | 정확히 `root` |
| `status` | enum | 예 | `draft`, `approved`, `implemented` |
| `language` | enum | 예 | v1은 BCP 47 tag `en`, `ko` |
| `kind` | enum | 예 | `feature`, `system`, `interface`, `policy` |
| `subtype` | string | 아니오 | lowercase kebab-case 의미 분류 |
| `areas` | string[] | 예 | 빈 목록 허용 |
| `components` | string[] | 예 | 빈 목록 허용 |
| `relatedSpecs` | relation[] | 예 | 빈 목록 허용, typed valid bundle path |

Title은 body의 단일 H1에서 파생하며 metadata field로 중복하지 않는다. Dependency-free frontmatter parser가 받는 canonical serialization은 다음과 같다.

```yaml
---
schema: forge/spec@3
role: root
status: draft
language: ko
kind: system
subtype: document-lifecycle
areas: ["forge"]
components: ["writing-specs", "spec-docs"]
relatedSpecs: [{"path": "docs/specs/review-viewer-lifecycle/", "relation": "relatedTo"}]
---
```

Scalar는 parser가 문자열로 취급하고 collection은 JSON array 또는 object 문법을 사용한다. 다른 YAML 기능은 v1 input이 아니다.

spec validation command contract:

```text
spec-docs validate --root docs/specs
```

| Command | 입력 | 출력 | 실패 조건 |
|---|---|---|---|
| `validate` | 모든 Spec Bundle | 정렬된 진단과 exit code | schema, layout, statement, relation, link 위반 |

문서 역할과 저장 정책:

| Artifact | 역할 | Git | 갱신 trigger |
|---|---|---:|---|
| `docs/specs/<semantic-bundle-name>/` | 영구 source of truth | 예 | 요구사항·상태 변경 |
| `docs/plans/PPP-<slug>/plan.md` | 작업 단위 실행 source | 예 | 계획·진행 변경 |
| `.forge/reviews/<review-id>/view.html` | 요청형 맥락 snapshot | 아니오 | 사용자 명시 요청 |

spec transition manifest:

```json
{
  "schema": "forge/spec-bundle-transitions@1",
  "transitions": [
    {
      "fromSourcePath": "docs/specs/old-semantic-name/",
      "fromSourceSha256": "64 lowercase hex characters",
      "disposition": "superseded",
      "toBundlePath": "docs/specs/current-semantic-name/",
      "evidencePath": "docs/evidence/current-semantic-name-migration.md",
      "reason": "현재 운영 계약과 완료된 실행 기록을 분리한다."
    }
  ]
}
```

동일한 baseline transition은 한 번만 적용한다. 이후 baseline에 `fromSourcePath`가 없으면 해당 record는 historical evidence로 남지만 새 삭제 권한을 만들지 않는다. 나중에 현재 replacement를 다시 교체할 때는 그 시점의 baseline bundle을 `fromSourcePath`로 사용하는 새 record를 별도 diff에 append한다.

## Requirements

### Canonical Spec은 `docs/specs/<semantic-bundle-name>/`에 저장되는 하나의 Spec Bundle이며, 이 디렉터리와 선언된 Markdown member 전체가 요구사항, 승인 상태, 관계와 변경 이력의 유일한 source of truth여야 한다.

### bundle root만 YAML frontmatter에서 `schema: forge/spec@3`, `role: root`, `status`, `language`, `kind`, 선택적인 `subtype`, `areas`, `components`, `relatedSpecs`를 선언해야 한다. `id`와 선언되지 않은 field는 허용하지 않아야 한다.

### `status`는 `draft`, `approved`, `implemented` 중 하나여야 하며 frontmatter의 값만 lifecycle gate token으로 사용하고 별도의 `Status:` body line을 중복 정본으로 유지하지 않아야 한다.

### `language`는 lifecycle tooling이 지원하는 BCP 47 tag `en`, `ko` 중 하나여야 한다. `kind`는 `feature`, `system`, `interface`, `policy` 중 하나여야 하고, `subtype`은 생략하거나 lowercase kebab-case 의미 분류를 사용해야 한다. `areas`, `components`, `relatedSpecs`는 빈 목록을 허용하되 항상 명시해야 한다. `relatedSpecs` 항목은 `id` 대신 normalized bundle directory `path`와 관계 종류를 선언해야 한다. Frontmatter는 dependency-free parser가 읽을 수 있도록 top-level `key: value`와 JSON-compatible 한 줄 collection만 허용해야 한다.

### `relatedSpecs`의 각 항목은 repository 안의 유효한 normalized bundle directory path와 관계 종류 `dependsOn`, `refines`, `supersedes`, `relatedTo` 중 하나를 선언해야 하며 self-reference와 해석할 수 없는 path를 허용하지 않아야 한다.
