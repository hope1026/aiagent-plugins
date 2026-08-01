#!/usr/bin/env python3
"""Verify that Viewer Mermaid sources match spec fences exactly."""

from __future__ import annotations

import re
import sys
import hashlib
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class MermaidParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[str] = []
        self.hashes: list[str] = []
        self._active = False
        self._parts: list[str] = []
        self._diagram_origin: str | None = None
        self._diagram_hash = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = dict(attrs).get("class", "") or ""
        values = dict(attrs)
        if tag == "article" and "diagram-card" in classes.split():
            self._diagram_origin = values.get("data-origin")
            self._diagram_hash = values.get("data-mermaid-sha256") or ""
        if tag == "pre" and "mermaid" in classes.split():
            self._active = True
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._active:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "pre" and self._active:
            if self._diagram_origin != "Derived view":
                self.blocks.append("".join(self._parts))
                self.hashes.append(self._diagram_hash)
            self._active = False
        if tag == "article" and self._diagram_origin is not None:
            self._diagram_origin = None
            self._diagram_hash = ""


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: verify-mermaid-equality.py SPEC VIEWER", file=sys.stderr)
        return 2
    spec = Path(sys.argv[1]).read_text(encoding="utf-8")
    expected = re.findall(r"(?ms)^```mermaid\n(.*?)\n```\s*$", spec)
    parser = MermaidParser()
    parser.feed(Path(sys.argv[2]).read_text(encoding="utf-8"))
    available = Counter(parser.blocks)
    needed = Counter(expected)
    if any(available[source] < count for source, count in needed.items()):
        print(f"Mermaid mismatch: source={len(expected)} viewer-source={len(parser.blocks)}", file=sys.stderr)
        return 1
    for source, digest in zip(parser.blocks, parser.hashes):
        if hashlib.sha256(source.encode("utf-8")).hexdigest() != digest:
            print("Mermaid hash mismatch in Viewer", file=sys.stderr)
            return 1
    print(f"mermaid equality: {len(expected)} source blocks present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
