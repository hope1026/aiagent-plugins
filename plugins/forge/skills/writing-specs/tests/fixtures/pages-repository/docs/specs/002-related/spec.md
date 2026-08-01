---
schema: forge/spec@1
id: 002-related
status: approved
language: en
kind: system
areas: []
components: ["parser", "deterministic-renderer-with-an-intentionally-long-component-label"]
relatedSpecs: [{"id": "001-basic", "relation": "relatedTo"}]
---
# Related Rendering Contract

## Overview

This specification supplies empty and long metadata states for the catalog.

## Requirements

- R1. The catalog must derive entries from current metadata.

## Behavior & Flows

The source contains no Mermaid diagram.

## Data & Interfaces

The renderer consumes an immutable `SpecDocument`.

## Acceptance Criteria

- AC1 (R1): Building the catalog lists this source and its generated page.

## Decisions & History

- 2026-08-01 [DECISION] The fixture keeps an empty area list.
