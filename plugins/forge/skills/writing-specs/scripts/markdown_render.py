"""Small escape-first Markdown renderer shared by Forge document views."""

from __future__ import annotations

import html
import re
from urllib.parse import urlsplit


_FENCE_RE = re.compile(r"^\s*(```|~~~)([^`]*)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(\S.*)$")
_UNORDERED_RE = re.compile(r"^\s*[-+*]\s+(\S.*)$")
_ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+(\S.*)$")
_TABLE_DIVIDER_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
_INLINE_RE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)]*)\)")


def _safe_href(raw: str) -> str | None:
    value = raw.strip()
    if not value or any(ord(character) < 32 or ord(character) == 127 for character in value):
        return None
    try:
        scheme = urlsplit(value).scheme.lower()
    except ValueError:
        return None
    if scheme and scheme not in {"http", "https", "mailto"}:
        return None
    return value


def _inline(text: str) -> str:
    rendered: list[str] = []
    offset = 0
    for match in _INLINE_RE.finditer(text):
        rendered.append(html.escape(text[offset : match.start()], quote=True))
        code, label, raw_href = match.groups()
        if code is not None:
            rendered.append(f"<code>{html.escape(code, quote=True)}</code>")
        else:
            safe_href = _safe_href(raw_href)
            safe_label = html.escape(label, quote=True)
            if safe_href is None:
                rendered.append(f'<span class="unsafe-link">{safe_label}</span>')
            else:
                rendered.append(
                    f'<a href="{html.escape(safe_href, quote=True)}">{safe_label}</a>'
                )
        offset = match.end()
    rendered.append(html.escape(text[offset:], quote=True))
    return "".join(rendered)


def anchor_slug(text: str, used: dict[str, int]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    count = used.get(base, 0)
    used[base] = count + 1
    return base if count == 0 else f"{base}-{count + 1}"


def _cells(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _starts_block(lines: list[str], index: int) -> bool:
    line = lines[index]
    if not line.strip():
        return True
    if _FENCE_RE.fullmatch(line) or _HEADING_RE.fullmatch(line):
        return True
    if _UNORDERED_RE.fullmatch(line) or _ORDERED_RE.fullmatch(line):
        return True
    return index + 1 < len(lines) and "|" in line and _TABLE_DIVIDER_RE.fullmatch(
        lines[index + 1]
    ) is not None


def render_markdown(text: str) -> str:
    """Render the supported Markdown subset without I/O or ambient state."""

    lines = text.splitlines()
    output: list[str] = []
    index = 0
    heading_ids: dict[str, int] = {}
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue

        fence = _FENCE_RE.fullmatch(line)
        if fence is not None:
            marker = fence.group(1)
            language = fence.group(2).strip()
            index += 1
            content: list[str] = []
            while index < len(lines) and lines[index].strip() != marker:
                content.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            source = "\n".join(content)
            escaped_source = html.escape(source, quote=False)
            if language.lower() == "mermaid":
                output.append(
                    '<div class="diagram-scroll" role="region" '
                    'aria-label="Mermaid diagram source">'
                    f'<pre class="mermaid">{escaped_source}</pre></div>'
                )
            else:
                class_name = (
                    f' class="language-{html.escape(language, quote=True)}"'
                    if language
                    else ""
                )
                output.append(f"<pre><code{class_name}>{escaped_source}</code></pre>")
            continue

        heading = _HEADING_RE.fullmatch(line)
        if heading is not None:
            level = len(heading.group(1))
            text_value = heading.group(2).strip()
            anchor = anchor_slug(text_value, heading_ids)
            output.append(f'<h{level} id="{anchor}">{_inline(heading.group(2))}</h{level}>')
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and _TABLE_DIVIDER_RE.fullmatch(
            lines[index + 1]
        ):
            headers = _cells(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                rows.append(_cells(lines[index]))
                index += 1
            head = "".join(f"<th scope=\"col\">{_inline(cell)}</th>" for cell in headers)
            body = "".join(
                "<tr>" + "".join(f"<td>{_inline(cell)}</td>" for cell in row) + "</tr>"
                for row in rows
            )
            output.append(
                '<div class="table-scroll" role="region" aria-label="Scrollable table" '
                f'tabindex="0"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
            )
            continue

        unordered = _UNORDERED_RE.fullmatch(line)
        if unordered is not None:
            items: list[str] = []
            while index < len(lines):
                item = _UNORDERED_RE.fullmatch(lines[index])
                if item is None:
                    break
                items.append(f"<li>{_inline(item.group(1))}</li>")
                index += 1
            output.append("<ul>" + "".join(items) + "</ul>")
            continue

        ordered = _ORDERED_RE.fullmatch(line)
        if ordered is not None:
            items = []
            while index < len(lines):
                item = _ORDERED_RE.fullmatch(lines[index])
                if item is None:
                    break
                items.append(f"<li>{_inline(item.group(1))}</li>")
                index += 1
            output.append("<ol>" + "".join(items) + "</ol>")
            continue

        paragraph = [line.strip()]
        index += 1
        while index < len(lines) and not _starts_block(lines, index):
            paragraph.append(lines[index].strip())
            index += 1
        output.append(f"<p>{_inline(' '.join(paragraph))}</p>")

    return "\n".join(output)
