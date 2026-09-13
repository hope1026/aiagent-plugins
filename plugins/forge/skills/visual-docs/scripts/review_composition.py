"""Source-bound explanations, separate from lossless source browsing.

Validation proves shape, source binding and exact quotations, not entailment or
human comprehension. Frozen explanations still require semantic and rendered review.
"""
from dataclasses import asdict
import hashlib
import html
import json
import re

from review_ir import SemanticIR
from review_planner import ViewContext

SCHEMA = 'forge/visual-doc-composition@1'
_ID = re.compile(r'^[a-z][a-z0-9-]{0,63}$')
_MARKUP = re.compile(r'<\s*/?\s*(?:script|style|iframe|object|embed|svg|math|img|a|div|span|p|table|html|body)\b[^>]*>|```|%%\{', re.IGNORECASE)


def canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def prepare_composition(ir: SemanticIR, context: ViewContext) -> dict:
    sources = [
        {'id': block.key, 'path': document.path, 'role': document.role,
         'heading': block.heading, 'heading_path': list(block.heading_path),
         'line': block.line, 'end_line': block.end_line, 'text': block.body}
        for document in ir.documents for block in document.blocks
    ]
    fingerprint = hashlib.sha256(canonical_bytes({
        'sources': sources,
        'documents': [{'path': d.path, 'role': d.role, 'metadata': dict(d.metadata)} for d in ir.documents],
    })).hexdigest()
    return {'schema': SCHEMA, 'source_fingerprint': fingerprint,
            'context': asdict(context), 'sources': sources,
            'guidance': 'Read the source, choose reader questions, then author grounded sections. Exact quotes establish provenance, not semantic correctness. Never infer missing policy or ownership.'}


def _object(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise ValueError('COMPOSITION_SCHEMA: invalid or unknown fields')


def _text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 20000:
        raise ValueError('COMPOSITION_TEXT: expected non-empty readable text')
    if _MARKUP.search(value):
        raise ValueError('COMPOSITION_MARKUP: use plain text, not executable markup')


def _list(value, minimum=1):
    if not isinstance(value, list) or len(value) < minimum or len(value) > 1000:
        raise ValueError('COMPOSITION_SCHEMA: invalid list')


def validate_composition(value: dict, ir: SemanticIR, context: ViewContext) -> None:
    _object(value, ('schema', 'source_fingerprint', 'context', 'title', 'lead', 'questions', 'sections', 'review'))
    if value['schema'] != SCHEMA:
        raise ValueError('COMPOSITION_SCHEMA: unsupported version')
    prepared = prepare_composition(ir, context)
    if value['source_fingerprint'] != prepared['source_fingerprint']:
        raise ValueError('COMPOSITION_STALE: sources changed; reconsider the explanation')
    if value['context'] != prepared['context']:
        raise ValueError('COMPOSITION_CONTEXT: reader or request changed; reconsider the explanation')
    sources = {s['id']: s for s in prepared['sources']}

    def refs(evidence):
        _list(evidence)
        for ref in evidence:
            _object(ref, ('source', 'quote'))
            if not isinstance(ref['source'], str) or ref['source'] not in sources:
                raise ValueError('COMPOSITION_REFERENCE: unknown source block')
            source = sources[ref['source']]
            quote = ref['quote']
            if not isinstance(quote, str) or not quote.strip() or quote not in source['text'] and quote not in source['heading']:
                raise ValueError('COMPOSITION_QUOTE: evidence is not an exact source excerpt')

    def claim(obj):
        _text(obj['text'])
        refs(obj['refs'])

    def identifier(value):
        if not isinstance(value, str) or not _ID.fullmatch(value):
            raise ValueError('COMPOSITION_ID: use a short lowercase identifier')

    _text(value['title'])
    _object(value['lead'], ('text', 'refs'))
    claim(value['lead'])
    _list(value['sections'])
    section_ids, block_ids = set(), set()
    for section in value['sections']:
        _object(section, ('id', 'title', 'blocks'))
        identifier(section['id'])
        if section['id'] in section_ids:
            raise ValueError('COMPOSITION_ID: duplicate section')
        section_ids.add(section['id'])
        _text(section['title'])
        _list(section['blocks'])
        for block in section['blocks']:
            if not isinstance(block, dict):
                raise ValueError('COMPOSITION_SCHEMA: invalid block')
            kind = block.get('type')
            extra = {'prose': (), 'example': ('assumptions',), 'table': ('columns', 'rows'),
                     'flow': ('nodes', 'edges'), 'relationship': ('nodes', 'edges')}.get(kind)
            if extra is None:
                raise ValueError('COMPOSITION_TYPE: unsupported presentation')
            _object(block, ('id', 'type', 'text', 'refs', *extra))
            identifier(block['id'])
            if block['id'] in block_ids:
                raise ValueError('COMPOSITION_ID: duplicate answer block')
            block_ids.add(block['id'])
            claim(block)
            if kind == 'example':
                _list(block['assumptions'], 0)
                for assumption in block['assumptions']:
                    _text(assumption)
            elif kind == 'table':
                _list(block['columns'])
                for column in block['columns']:
                    _text(column)
                _list(block['rows'])
                for row in block['rows']:
                    _object(row, ('cells', 'refs'))
                    _list(row['cells'])
                    if len(row['cells']) != len(block['columns']):
                        raise ValueError('COMPOSITION_TABLE: cell count must match columns')
                    for cell in row['cells']:
                        _text(cell)
                    refs(row['refs'])
            elif kind in ('flow', 'relationship'):
                _list(block['nodes'])
                _list(block['edges'])
                nodes = set()
                for node in block['nodes']:
                    _object(node, ('id', 'text', 'refs'))
                    identifier(node['id'])
                    if node['id'] in nodes:
                        raise ValueError('COMPOSITION_GRAPH: duplicate node')
                    nodes.add(node['id'])
                    claim(node)
                used = set()
                for edge in block['edges']:
                    _object(edge, ('from', 'to', 'text', 'refs'))
                    if not isinstance(edge['from'], str) or not isinstance(edge['to'], str) or edge['from'] not in nodes or edge['to'] not in nodes:
                        raise ValueError('COMPOSITION_GRAPH: dangling edge')
                    used.update((edge['from'], edge['to']))
                    claim(edge)
                if used != nodes:
                    raise ValueError('COMPOSITION_GRAPH: disconnected node has no explained relation')
    _list(value['questions'])
    for question in value['questions']:
        _object(question, ('text', 'answer_blocks'))
        _text(question['text'])
        _list(question['answer_blocks'])
        if any(not isinstance(b, str) or b not in block_ids for b in question['answer_blocks']):
            raise ValueError('COMPOSITION_QUESTION: question has no reachable answer')
    _object(value['review'], ('method', 'reviewer', 'notes'))
    if value['review']['method'] not in ('agent', 'human'):
        raise ValueError('COMPOSITION_REVIEW: identify the actual semantic reviewer')
    _text(value['review']['reviewer'])
    _text(value['review']['notes'])


def render_composition(value: dict, ir: SemanticIR, context: ViewContext) -> str:
    validate_composition(value, ir, context)
    sources = {s['id']: s for s in prepare_composition(ir, context)['sources']}
    ko = context.locale == 'ko'
    esc = html.escape

    def evidence(refs):
        items = []
        for ref in refs:
            source = sources[ref['source']]
            items.append('<li><p class="provenance">' + esc(source['role']) + ' · <code>'
                         + esc(source['path']) + '</code> · ' + str(source['line'])
                         + '</p><blockquote>' + esc(ref['quote']) + '</blockquote></li>')
        return ('<details class="reading-evidence"><summary>' + ('설명의 근거' if ko else 'Evidence for this explanation')
                + '</summary><ul>' + ''.join(items) + '</ul><a href="#reading-originals">'
                + ('전체 원문 탐색' if ko else 'Browse complete sources') + '</a></details>')

    def mermaid_text(text):
        # Mermaid entity syntax keeps quotes, brackets and user text inside labels.
        return ''.join(f'#{ord(c)};' if c in '"&<>[]{}|\\\n\r' else c for c in text)

    parts = ['<div class="reading-document" data-composition="grounded">',
             '<p class="reading-lead">' + esc(value['lead']['text']) + '</p>', evidence(value['lead']['refs']),
             '<nav class="reading-questions" aria-label="' + ('확인할 질문' if ko else 'Reader questions') + '"><ul>']
    block_sections = {b['id']: section['title'] for section in value['sections'] for b in section['blocks']}
    for question in value['questions']:
        parts.append('<li><a href="#reading-' + question['answer_blocks'][0] + '">' + esc(question['text']) + '</a>')
        seen_sections = {block_sections[question['answer_blocks'][0]]}
        additional = []
        for key in question['answer_blocks'][1:]:
            if block_sections[key] not in seen_sections:
                additional.append('<li><a href="#reading-' + key + '">' + esc(block_sections[key]) + '</a></li>')
                seen_sections.add(block_sections[key])
        if additional:
            parts.append('<ul>' + ''.join(additional) + '</ul>')
        parts.append('</li>')
    parts.append('</ul></nav>')
    for section in value['sections']:
        parts.append('<section class="reading-section" id="reading-section-' + section['id'] + '"><h2>' + esc(section['title']) + '</h2>')
        for block in section['blocks']:
            parts.append('<article class="reading-block" id="reading-' + block['id'] + '" data-reading-type="' + block['type'] + '">')
            if block['type'] == 'example':
                parts.append('<h3>' + ('예시' if ko else 'Example') + '</h3>')
            parts.append('<p>' + esc(block['text']) + '</p>')
            if block['type'] == 'example' and block['assumptions']:
                parts.append('<p class="reading-assumptions">' + ('예시의 가정' if ko else 'Example assumptions') + '</p><ul>'
                             + ''.join('<li>' + esc(s) + '</li>' for s in block['assumptions']) + '</ul>')
            if block['type'] == 'table':
                parts.append('<div class="table-scroll" role="region" tabindex="0" aria-label="' + esc(section['title'], quote=True) + '"><table><thead><tr>'
                             + ''.join('<th scope="col">' + esc(c) + '</th>' for c in block['columns']) + '</tr></thead><tbody>')
                for row in block['rows']:
                    parts.append('<tr>' + ''.join('<td>' + esc(c) + (evidence(row['refs']) if index == len(row['cells'])-1 else '') + '</td>' for index,c in enumerate(row['cells'])) + '</tr>')
                parts.append('</tbody></table></div>')
            elif block['type'] in ('flow', 'relationship'):
                nodes = {n['id']: n for n in block['nodes']}
                direction = 'TD' if block['type'] == 'flow' else 'LR'
                lines = ['flowchart ' + direction]
                for key, node in nodes.items():
                    lines.append('  n_' + key.replace('-', '_') + '["' + mermaid_text(node['text']) + '"]')
                parts.append('<p class="provenance">Derived view</p><ul class="reading-relations">')
                for edge in block['edges']:
                    label = nodes[edge['from']]['text'] + ' → ' + nodes[edge['to']]['text'] + ': ' + edge['text']
                    parts.append('<li>' + esc(label) + evidence(edge['refs']) + '</li>')
                    lines.append('  n_' + edge['from'].replace('-', '_') + ' -->|"' + mermaid_text(edge['text']) + '"| n_' + edge['to'].replace('-', '_'))
                parts.append('</ul><details class="reading-evidence"><summary>' + ('노드의 근거' if ko else 'Node evidence') + '</summary>'
                             + ''.join('<p>' + esc(n['text']) + '</p>' + evidence(n['refs']) for n in nodes.values()) + '</details>')
                parts.append('<div class="diagram-scroll" role="region" tabindex="0" aria-label="' + esc(section['title'], quote=True)
                             + '"><pre class="mermaid">' + esc('\n'.join(lines)) + '</pre></div>')
            parts.append(evidence(block['refs']) + '</article>')
        parts.append('</section>')
    review = value['review']
    parts.append('<details class="reading-review"><summary>' + ('검토 기록 · 읽기 검증 필요' if ko else 'Review record · reading check required') + '</summary><p>'
                 + esc(review['method'] + ' · ' + review['reviewer']) + '</p><p>' + esc(review['notes']) + '</p><p>'
                 + ('출처 검사는 의미의 정확성이나 사람의 이해를 보장하지 않습니다.' if ko else 'Source checks do not prove semantic accuracy or human comprehension.') + '</p></details></div>')
    return ''.join(parts)
