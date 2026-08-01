# Offline Mermaid bundle template-token collision

## Symptom

실제 Mermaid 11 bundle을 `--offline`으로 삽입하면 builder가 `unresolved template tokens: {{NAV_LABEL}}, {{SOURCE_MANIFEST}}`로 중단됐다. 일반 test stub을 사용한 offline build는 통과했다.

## Reproduction

`mermaid-mustache-stub.js`에 shell token과 같은 모양의 문자열을 넣고 다음 test를 실행한다.

```bash
bash plugins/forge/skills/spec-viewer/tests/test-build-viewer.sh
```

수정 전에는 Mustache stub build가 exit 1로 실패했다.

## Root cause

builder가 shell token replacement를 모두 수행한 뒤 완성된 HTML 전체를 다시 검사했다. 그 결과 replacement 과정에서 새로 삽입된 third-party Mermaid bundle의 Mustache 문자열까지 shell의 미해결 token으로 오인했다.

## Fix

미해결 token은 원본 shell template에서 replacement key와 비교한다. 그다음 정규식 callback으로 원본 shell token만 한 번 치환해 content fragment와 Mermaid bundle 안의 문자열을 다시 해석하지 않는다.

## Regression test path

`plugins/forge/skills/spec-viewer/tests/test-build-viewer.sh`  
`plugins/forge/skills/spec-viewer/tests/fixtures/mermaid-mustache-stub.js`
