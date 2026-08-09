---
schema: forge/project-map@1
---
# Demo Project

## Project Overview

Forge 문서를 사람이 이해하기 쉬운 화면으로 제공한다.

## Key Capabilities

- Spec 계약 탐색
- 프로젝트 구조 책임 탐색

## Specs

- bundle: docs/specs/semantic-spec-bundles/

## Structure

### docs/

**Purpose:** 사람이 읽는 프로젝트 문서를 보관한다.

**Owns:** Canonical Spec과 Project Map source를 소유한다.

**Entry Points:**
- docs/project/project-map.md

**Depends On:**
- plugins/forge/

**Related Specs:**
- docs/specs/semantic-spec-bundles/

**Governing Statements:**
- [Every declared member enters the review source set exactly once](../specs/semantic-spec-bundles/member-loading-and-provenance.md#every-declared-member-enters-the-review-source-set-exactly-once)
