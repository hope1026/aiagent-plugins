---
schema: forge/spec@3
role: root
status: approved
language: ko
kind: system
areas: ["requests"]
components: ["coordination"]
relatedSpecs: []
---
# 요청 처리

## Documents

- root: [요청 처리](workflow-ko.md)

## 목적

담당자는 요청에 연락처가 있는지 확인한다. 연락처가 없으면 보완을 요청하고 대기 상태를 유지한다. 연락처가 있으면 전문가에게 배정한다. 전문가는 결과를 기록하고, 그 후 담당자가 요청을 종료한다. 결과를 기록하지 않은 요청은 종료할 수 없다.
