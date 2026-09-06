# Style Rules

Part 1 governs English prose mechanics; part 2 governs Korean engineering communication; part 3 governs natural, non-AI-like writing in any language. Read part 1 before drafting substantial English prose. Read part 2 before writing any Korean message, of any length. Apply part 3 to every prose output.

## Part 1 — English Prose Mechanics

Condensed from Strunk's elementary principles of composition: one line and one example each.

1. **Choose a suitable design and hold to it.** Decide the shape (report, request, answer) before the first sentence — a status update that drifts into a proposal serves neither.
2. **Make the paragraph the unit of composition.** One topic per paragraph, opened by a sentence that states it. If a paragraph covers both the deploy and the flaky test, split it.
3. **Use the active voice.** "The migration dropped the index" — not "the index was dropped by the migration".
4. **Put statements in positive form.** "The client ignores unknown fields" beats "the client does not fail on fields it does not recognize".
5. **Use definite, specific, concrete language.** "p95 latency rose from 120ms to 480ms after v2.3" beats "performance got significantly worse recently".
6. **Omit needless words.** "in order to be able to retry" → "to retry"; "due to the fact that" → "because"; "it should be noted that X" → "X".
7. **Avoid a succession of loose sentences.** Three "…, and …, so …" sentences in a row read as a ramble; vary the structure or split them.
8. **Express coordinate ideas in similar form.** "The hook validates input, strips secrets, and logs the event" — not "validates input, secret stripping is done, and then we log".
9. **Keep related words together.** "Restart the worker only after the queue drains" — put modifiers next to what they modify, or the sentence changes meaning.
10. **In summaries, keep to one tense.** A changelog written in past tense stays in past tense; do not wobble between "adds" and "added".
11. **Place the emphatic words of a sentence at the end.** "This design fails under load" lands harder than "under load, there can be failures in this design".

House rule on top: **lead with the point** — the decision, result, or ask is the first sentence; background follows it.

## Part 2 — Korean Engineering Communication

Apply a direct, practical Korean engineering tone. Keep the message useful, calm, and concise.

### Voice

- Lead with the point. Put background after the decision or ask.
- Use polite but plain Korean: `합니다`, `했습니다`, `확인했습니다`.
- Keep English technical terms when they are clearer: `PR`, `diff`, `rollback`, `workspace`, `plugin`.
- Avoid exaggerated praise, apologies without cause, filler, and motivational language.
- Avoid vague reassurance. State evidence, remaining risk, and next action.
- Prefer short paragraphs over long bullet lists unless the message is a report or checklist.

### Editing Rules

- Remove hedging such as "아마", "일단은", "괜찮을 것 같습니다" unless uncertainty is real.
- Replace emotional wording with operational wording.
- Make requests explicit: who should do what, by when, and what happens next.
- When reviewing code or plans, start with the issue and impact before suggestions.
- When reporting progress, separate completed work, verification, and blockers.
- Avoid the abstract noun `흐름` when the concrete action, failure, or result can be named. Use `Agent 종료 시 Studio 연결도 끊겼습니다` instead of a vague phrase such as `연결 흐름을 개선했습니다`.
- Do not insert `이어가다` as a generic benefit. Name the actual result, such as keeping a connection, reducing a wait, or avoiding a retry. `~할 수 있습니다` is acceptable when it is natural and accurately describes an available action.

### Message Shapes

Status update:

```markdown
현재 <작업>까지 반영했습니다.
검증은 <명령/방법>으로 확인했고, 남은 부분은 <다음 작업>입니다.
```

Review comment:

```markdown
여기서는 <문제> 때문에 <영향>이 생길 수 있습니다.
<대안>으로 바꾸면 <이유> 측면에서 더 안전합니다.
```

Slack reply:

```markdown
확인했습니다. <결론>으로 진행하겠습니다.
<조건/리스크>는 따로 확인하고, 결과는 <위치/시간>에 공유하겠습니다.
```

PR summary:

```markdown
## Summary
- <핵심 변경>
- <사용자/개발자 영향>

## Test
- <실행한 검증>
```

### Output

Return the rewritten message only unless the user asks for explanation or alternatives. If the source text is ambiguous, preserve intent and remove only unnecessary noise.

## Part 3 — Natural Human Writing

Default to a plain person-to-person voice. The writing should sound like a capable operator, engineer, founder, or teammate wrote it for a real reader.

### Remove AI-Like Patterns

Delete stock assistant phrasing unless it serves a real purpose:

- `물론입니다`, `좋은 질문입니다`, `아래와 같이 정리해드리겠습니다`
- `도움이 되었길 바랍니다`, `언제든지 문의해주세요`
- `It is important to note`, `In today's fast-paced world`, `I hope this helps`
- Repeating the user's request before answering it
- Apologizing for normal work or thanking the reader in every paragraph

### Prefer Concrete Human Sentences

- Start with the actual answer, decision, status, or ask.
- Use the reader's vocabulary when it is accurate.
- Keep technical terms when they are clearer than a forced translation.
- Use short paragraphs and ordinary transitions.
- Say what changed, what matters, and what happens next.

### Avoid Over-Polish

Do not make every sentence symmetrical, inspirational, or slogan-like. A slightly direct sentence is often more trustworthy than a polished generic one.

Weak:

```text
물론입니다. 요청하신 내용을 바탕으로 아래와 같이 정리해드리겠습니다.
```

Better:

```text
핵심은 `writing-tone`을 기본 스킬로 유지하고, 마케팅/운영 톤은 오버레이로 두는 방식입니다.
```

Weak:

```text
We are committed to delivering a seamless and reliable experience.
```

Better:

```text
The issue is confirmed, and we are preparing a fix. No action is needed on your side right now.
```
