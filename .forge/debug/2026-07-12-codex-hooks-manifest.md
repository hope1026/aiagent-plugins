# Codex manifest legacy hooks field

## Symptom

plugin-creator의 공식 validator가 Forge의 `.codex-plugin/plugin.json`을 `plugin.json field hooks is not accepted by plugin validation`으로 거부했다.

## Reproduction

임시 venv에서 `PyYAML`을 제공한 뒤 다음 validator를 실행한다.

```bash
.forge/scratch/plugin-validator-venv/bin/python \
  /Users/han-byeol/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/forge
```

legacy `hooks` field가 있으면 exit 1이다.

## Root cause

Forge의 portability reference와 Codex manifest가 과거의 빈 `hooks` field를 유지했지만, 현재 Codex ingestion contract는 `hooks`를 허용하지 않는다.

## Fix

Codex manifest에서 `hooks` field를 제거하고 portability reference를 현재 contract에 맞췄다. Claude hook 파일과 Claude manifest는 변경하지 않았다.

## Regression test path

`/Users/han-byeol/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py`  
`scripts/validate.sh`
