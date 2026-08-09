---
schema: forge/spec@3
role: root
status: approved
language: en
kind: system
areas: ["forge"]
components: ["writing-specs"]
relatedSpecs: [{"path":"docs/specs/review-lifecycle/","relation":"dependsOn"}]
---
# Semantic Workflow Contract

## Documents

- root: [Semantic Workflow Contract](workflow-contract.md)
- contract: [Bundle Containment Rules](bundle-containment-rules.md)
- acceptance: [Repository Validation Outcomes](repository-validation-outcomes.md)
- history: [Semantic Workflow Decisions](semantic-workflow-decisions.md)

## Requirements

### Each spec bundle is discovered as a direct child of the spec root

Repository discovery uses the bundle directory as the durable identity.
