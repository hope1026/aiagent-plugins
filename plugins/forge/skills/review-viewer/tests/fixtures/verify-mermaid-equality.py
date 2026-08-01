#!/usr/bin/env python3
"""Verify that Viewer Mermaid sources match spec fences exactly."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class MermaidParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self._active = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = dict(attrs).get("class", "") or ""
        if tag == "pre" and "mermaid" in classes.split():
            self._active = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._active:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre" and self._active:
            self.blocks.append("".join(self._parts))
            self._active = False


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: verify-mermaid-equality.py SPEC VIEWER", file=sys.stderr)
        return 2
    spec = Path(sys.argv[1]).read_text(encoding="utf-8")
    expected = re.findall(r"(?ms)^```mermaid\n(.*?)\n```\s*$", spec)
    parser = MermaidParser()
    parser.feed(Path(sys.argv[2]).read_text(encoding="utf-8"))
    if expected != parser.blocks:
        print(f"Mermaid mismatch: spec={len(expected)} viewer={len(parser.blocks)}", file=sys.stderr)
        return 1
    print(f"mermaid equality: {len(expected)} blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
