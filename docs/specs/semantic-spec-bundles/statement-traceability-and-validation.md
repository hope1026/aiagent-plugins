# 문장 추적성과 검증

## Requirements

### Requirement는 `Requirements` 아래 H3의 완전한 문장이어야 하고, Acceptance Criterion은 bundle이 `Acceptance Criteria`를 사용할 때 그 section 아래 H3의 완전한 문장이어야 하며, bundle path, member path와 exact heading이 사람이 읽는 identity여야 한다. `Acceptance Criteria` section이 있으면 하나 이상의 Acceptance statement를 포함해야 한다. Acceptance Criterion이 하나라도 있으면 각 Acceptance Criterion은 같은 bundle의 Requirement를 member path, heading anchor와 exact link text로 하나 이상 참조하고 모든 Requirement를 coverage해야 한다. Acceptance Criterion이 없으면 missing Acceptance나 coverage diagnostic을 만들지 않아야 한다.

### `writing-specs`는 new, change, clarify, sync 모든 mode에서 `forge/spec@3` Spec Bundle을 작성하고 approval request 전에 repository 전체 bundle validation을 실행해야 한다.

### validator는 root metadata, bundle·member layout, `Documents` 목록의 완전성, H1, 필수 `Requirements`와 `Decisions & History`, 선택적인 `Acceptance Criteria`의 section 일관성, statement uniqueness·reference·조건부 coverage, clarification gate, related bundle resolution, internal Markdown link, Mermaid syntax와 deterministic bundle hash를 검사해야 한다. 임의 서술 section의 이름이나 순서는 오류로 처리하지 않아야 한다.

### `approved` 또는 `implemented` bundle에 `[NEEDS CLARIFICATION]`가 하나라도 있거나 Requirement가 없거나 빈 `Acceptance Criteria` section이 있거나 Acceptance Criterion이 존재하는데 coverage가 불완전하면 validation은 실패해야 한다.

### validation 실패는 spec 작성·변경 완료, approval request와 plan handoff를 차단하고 bundle path, member path와 사람이 수정할 수 있는 오류 원인을 반환해야 한다. Validation 성공 또는 실패는 HTML 생성 trigger가 아니어야 한다.

### validator와 parser는 같은 bundle bytes에서 같은 결과를 반환하고 진단을 `(bundle path, member path, line, code)` 순서로 정렬하며 외부 network, machine locale 또는 agent 추론에 의존하지 않아야 한다.

### Requirement와 Acceptance Criterion의 exact heading은 종류별로 bundle 전체에서 unique해야 하고 Acceptance의 link text·member path·공통 parser가 계산한 anchor가 대상 Requirement와 모두 일치해야 한다.

### parser는 normalized bundle path, member path, statement kind와 exact heading으로 내부 key를 계산할 수 있지만 이 key와 hash를 source, plan, agent 설명과 Visual Docs의 주 식별자로 기록하거나 표시하지 않아야 한다.

### bundle hash는 normalized bundle path와 lexicographically 정렬한 member path·byte length·exact bytes의 length-framed serialization에 SHA-256을 적용해 결정적으로 계산해야 한다.

### `inspect` machine output은 `bundlePath`, `rootPath`, title, metadata, `bundleSha256`, member path·title·role·source SHA-256, statement kind·path·heading·line·reference와 진단을 반환해야 한다. 사람이 읽는 output은 title, path와 full statement만 identity로 사용해야 한다.

## Acceptance Criteria

### `Acceptance Criteria` section이 없는 Requirement-only fixture와 완전한 coverage를 가진 acceptance-bearing fixture를 validate하면 둘 다 성공한다. missing·duplicate root, undeclared·missing member, 숫자 prefix, 범용 filename, symlink·escape, missing Requirement, 빈 `Acceptance Criteria` section, duplicate statement, broken anchor, link text mismatch, acceptance-bearing missing coverage, invalid relation·Mermaid와 approved clarification fixture를 validate하면 정렬된 deterministic 진단과 non-zero exit가 나오고 approval과 plan handoff가 중단되지만 HTML은 생성되지 않는다.

검증하는 요구사항:

- [`writing-specs`는 new, change, clarify, sync 모든 mode에서 `forge/spec@3` Spec Bundle을 작성하고 approval request 전에 repository 전체 bundle validation을 실행해야 한다.](statement-traceability-and-validation.md#writing-specs는-new-change-clarify-sync-모든-mode에서-forgespec3-spec-bundle을-작성하고-approval-request-전에-repository-전체-bundle-validation을-실행해야-한다)
- [validator는 root metadata, bundle·member layout, `Documents` 목록의 완전성, H1, 필수 `Requirements`와 `Decisions & History`, 선택적인 `Acceptance Criteria`의 section 일관성, statement uniqueness·reference·조건부 coverage, clarification gate, related bundle resolution, internal Markdown link, Mermaid syntax와 deterministic bundle hash를 검사해야 한다. 임의 서술 section의 이름이나 순서는 오류로 처리하지 않아야 한다.](statement-traceability-and-validation.md#validator는-root-metadata-bundlemember-layout-documents-목록의-완전성-h1-필수-requirements와-decisions-history-선택적인-acceptance-criteria의-section-일관성-statement-uniquenessreference조건부-coverage-clarification-gate-related-bundle-resolution-internal-markdown-link-mermaid-syntax와-deterministic-bundle-hash를-검사해야-한다-임의-서술-section의-이름이나-순서는-오류로-처리하지-않아야-한다)
- [`approved` 또는 `implemented` bundle에 `[NEEDS CLARIFICATION]`가 하나라도 있거나 Requirement가 없거나 빈 `Acceptance Criteria` section이 있거나 Acceptance Criterion이 존재하는데 coverage가 불완전하면 validation은 실패해야 한다.](statement-traceability-and-validation.md#approved-또는-implemented-bundle에-needs-clarification가-하나라도-있거나-requirement가-없거나-빈-acceptance-criteria-section이-있거나-acceptance-criterion이-존재하는데-coverage가-불완전하면-validation은-실패해야-한다)
- [validation 실패는 spec 작성·변경 완료, approval request와 plan handoff를 차단하고 bundle path, member path와 사람이 수정할 수 있는 오류 원인을 반환해야 한다. Validation 성공 또는 실패는 HTML 생성 trigger가 아니어야 한다.](statement-traceability-and-validation.md#validation-실패는-spec-작성변경-완료-approval-request와-plan-handoff를-차단하고-bundle-path-member-path와-사람이-수정할-수-있는-오류-원인을-반환해야-한다-validation-성공-또는-실패는-html-생성-trigger가-아니어야-한다)
- [`writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 공통 bundle parser가 반환한 root metadata, member 목록, statement와 status를 사용해야 한다.](lifecycle-consumers-and-bundle-replacement.md#writing-plans-executing-plans-verifying-work와-다른-forge-lifecycle-skill은-공통-bundle-parser가-반환한-root-metadata-member-목록-statement와-status를-사용해야-한다)
- [validator와 parser는 같은 bundle bytes에서 같은 결과를 반환하고 진단을 `(bundle path, member path, line, code)` 순서로 정렬하며 외부 network, machine locale 또는 agent 추론에 의존하지 않아야 한다.](statement-traceability-and-validation.md#validator와-parser는-같은-bundle-bytes에서-같은-결과를-반환하고-진단을-bundle-path-member-path-line-code-순서로-정렬하며-외부-network-machine-locale-또는-agent-추론에-의존하지-않아야-한다)
- [하나의 bundle은 하나의 지속적인 계약 경계여야 하며 `areas`나 기술 분야가 같다는 이유로 서로 다른 spec을 같은 디렉터리에 넣지 않아야 한다.](authoring-and-file-organization.md#하나의-bundle은-하나의-지속적인-계약-경계여야-하며-areas나-기술-분야가-같다는-이유로-서로-다른-spec을-같은-디렉터리에-넣지-않아야-한다)
- [bundle의 모든 Markdown member는 root의 `Documents`에 `root`, `contract`, `acceptance`, `history`, `reference` role과 H1을 그대로 사용한 link로 정확히 한 번 선언되어야 하며 root role은 root file에 정확히 한 번만 사용해야 한다.](authoring-and-file-organization.md#bundle의-모든-markdown-member는-root의-documents에-root-contract-acceptance-history-reference-role과-h1을-그대로-사용한-link로-정확히-한-번-선언되어야-하며-root-role은-root-file에-정확히-한-번만-사용해야-한다)
- [bundle directory와 Markdown filename은 lowercase kebab-case의 의미 이름을 사용해야 한다. Basename이 숫자 prefix로 시작하거나 `spec.md`, `index.md`, `document.md`, `requirements.md`, `acceptance-criteria.md`, `history.md`이면 거부하고, root filename은 directory와 같을 필요가 없어야 한다.](authoring-and-file-organization.md#bundle-directory와-markdown-filename은-lowercase-kebab-case의-의미-이름을-사용해야-한다-basename이-숫자-prefix로-시작하거나-specmd-indexmd-documentmd-requirementsmd-acceptance-criteriamd-historymd이면-거부하고-root-filename은-directory와-같을-필요가-없어야-한다)
- [Requirement와 Acceptance Criterion의 exact heading은 종류별로 bundle 전체에서 unique해야 하고 Acceptance의 link text·member path·공통 parser가 계산한 anchor가 대상 Requirement와 모두 일치해야 한다.](statement-traceability-and-validation.md#requirement와-acceptance-criterion의-exact-heading은-종류별로-bundle-전체에서-unique해야-하고-acceptance의-link-textmember-path공통-parser가-계산한-anchor가-대상-requirement와-모두-일치해야-한다)
- [parser는 normalized bundle path, member path, statement kind와 exact heading으로 내부 key를 계산할 수 있지만 이 key와 hash를 source, plan, agent 설명과 Visual Docs의 주 식별자로 기록하거나 표시하지 않아야 한다.](statement-traceability-and-validation.md#parser는-normalized-bundle-path-member-path-statement-kind와-exact-heading으로-내부-key를-계산할-수-있지만-이-key와-hash를-source-plan-agent-설명과-visual-docs의-주-식별자로-기록하거나-표시하지-않아야-한다)
- [bundle hash는 normalized bundle path와 lexicographically 정렬한 member path·byte length·exact bytes의 length-framed serialization에 SHA-256을 적용해 결정적으로 계산해야 한다.](statement-traceability-and-validation.md#bundle-hash는-normalized-bundle-path와-lexicographically-정렬한-member-pathbyte-lengthexact-bytes의-length-framed-serialization에-sha-256을-적용해-결정적으로-계산해야-한다)
- [`inspect` machine output은 `bundlePath`, `rootPath`, title, metadata, `bundleSha256`, member path·title·role·source SHA-256, statement kind·path·heading·line·reference와 진단을 반환해야 한다. 사람이 읽는 output은 title, path와 full statement만 identity로 사용해야 한다.](statement-traceability-and-validation.md#inspect-machine-output은-bundlepath-rootpath-title-metadata-bundlesha256-member-pathtitlerolesource-sha-256-statement-kindpathheadinglinereference와-진단을-반환해야-한다-사람이-읽는-output은-title-path와-full-statement만-identity로-사용해야-한다)
- [bundle은 root를 포함해 기본 1–5개 Markdown으로 작성해야 한다. 독립적인 계약·검토 경계, 별도 책임·runtime flow, API·정책·상태 전이, 변경 소유권 또는 200줄을 넘는 복합 주제가 있을 때 분리하고, 10개를 넘으면 spec 경계 분리를 먼저 검토해야 한다.](authoring-and-file-organization.md#bundle은-root를-포함해-기본-15개-markdown으로-작성해야-한다-독립적인-계약검토-경계-별도-책임runtime-flow-api정책상태-전이-변경-소유권-또는-200줄을-넘는-복합-주제가-있을-때-분리하고-10개를-넘으면-spec-경계-분리를-먼저-검토해야-한다)

### Approved bundle을 읽는 `writing-plans`와 implemented status를 기록하는 `verifying-work` fixture가 공통 parser의 root frontmatter status, bundle·member path와 full statement만으로 lifecycle gate를 적용한다.

검증하는 요구사항:

- [`writing-plans`, `executing-plans`, `verifying-work`와 다른 Forge lifecycle skill은 공통 bundle parser가 반환한 root metadata, member 목록, statement와 status를 사용해야 한다.](lifecycle-consumers-and-bundle-replacement.md#writing-plans-executing-plans-verifying-work와-다른-forge-lifecycle-skill은-공통-bundle-parser가-반환한-root-metadata-member-목록-statement와-status를-사용해야-한다)
- [`inspect` machine output은 `bundlePath`, `rootPath`, title, metadata, `bundleSha256`, member path·title·role·source SHA-256, statement kind·path·heading·line·reference와 진단을 반환해야 한다. 사람이 읽는 output은 title, path와 full statement만 identity로 사용해야 한다.](statement-traceability-and-validation.md#inspect-machine-output은-bundlepath-rootpath-title-metadata-bundlesha256-member-pathtitlerolesource-sha-256-statement-kindpathheadinglinereference와-진단을-반환해야-한다-사람이-읽는-output은-title-path와-full-statement만-identity로-사용해야-한다)
