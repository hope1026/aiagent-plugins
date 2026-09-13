---
schema: forge/spec@3
role: root
status: approved
language: en
kind: system
areas: ["requests"]
components: ["coordination"]
relatedSpecs: []
---
# Request handling

## Documents

- root: [Request handling](workflow-en.md)

## Purpose

A coordinator checks each request for a contact address. If the address is missing, the coordinator asks for it and the request remains pending. A request with an address is assigned to a specialist. The specialist records a result before the coordinator closes the request. Closure without a recorded result is not permitted.
