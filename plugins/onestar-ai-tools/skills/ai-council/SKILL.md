---
name: ai-council
description: Coordinate multiple AI assistants for a synthesized second opinion. Use when the user asks "AI council", "AI들끼리 논의", "여러 AI 의견", "다른 AI 의견", architecture review, difficult debugging, security review, or a high-impact technical decision that benefits from Codex, Claude Code, Gemini, or other available AI perspectives.
---

# AI Council

Use multiple AI assistants as reviewers, then synthesize the result into one recommendation. Prefer this for complex decisions where independent perspectives reduce blind spots.

## Safety

- Do not send secrets, credentials, customer data, private keys, tokens, `.env` values, or proprietary data unless the user explicitly approves that exact disclosure.
- Summarize sensitive context instead of pasting raw files when possible.
- Avoid recursive calls to the same active agent. If running inside Codex, do not ask Codex CLI for the same task unless the user explicitly wants that comparison. If running inside Claude Code, do not ask Claude Code to re-answer the same task.
- Treat external AI output as advice, not authority. Verify claims against local files, tests, docs, or source material.

## Workflow

1. Frame the decision in one paragraph.
2. Identify the minimal context needed: relevant files, diffs, error logs, constraints, and success criteria.
3. Choose assistants based on availability and value:
   - Use Codex for implementation tradeoffs, test strategy, and concrete code risks.
   - Use Claude Code for product reasoning, edge cases, communication, and maintainability.
   - Use Gemini for large-context scans, architecture review, and security review.
4. Ask each assistant a focused prompt. Include the same core problem statement so responses are comparable.
5. Compare responses by evidence quality. Separate agreements, disagreements, and unsupported claims.
6. Provide a recommendation with confidence level, risks, and next steps.

## CLI Patterns

Check availability before use:

```bash
command -v codex >/dev/null && codex --version
command -v claude >/dev/null && claude --version
command -v gemini >/dev/null && gemini --version
```

Codex:

```bash
codex exec "Review this approach for implementation risks and tests: <problem>"
```

Claude Code:

```bash
claude -p "Review this approach for maintainability, edge cases, and user-facing risks: <problem>"
```

Gemini:

```bash
gemini -m gemini-2.5-pro "Analyze this decision from architecture and security standpoints: <problem>"
```

For file context, prefer concise extracts or explicit file arguments supported by the local CLI. Avoid shell-substituting entire large files into prompts unless necessary.

## Synthesis Format

```markdown
## AI Council Report

### Problem
<decision or question>

### Perspectives
- Codex: <summary or "not used">
- Claude Code: <summary or "not used">
- Gemini: <summary or "not used">

### Agreement
- <shared conclusions>

### Disagreement
- <material differences and why they matter>

### Recommendation
<direct recommendation with confidence>

### Next Steps
1. <action>
2. <verification>
```

Keep the final report concise. Do not paste long external AI transcripts unless the user asks for raw output.
