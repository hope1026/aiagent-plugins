from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import sys
import unittest

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR.parent / 'scripts'))
from review_ir import build_semantic_ir
from review_sources import collect_spec_sources
from review_planner import ViewContext
from review_composition import prepare_composition, validate_composition, render_composition


def fixture():
    repository = TEST_DIR / 'fixtures/repository'
    ir = build_semantic_ir(collect_spec_sources(repository / 'docs/specs/semantic-spec-bundles', (), repository))
    context = ViewContext('spec', 'system', 'workflow', 'review', 'product', 'ko', 'standalone')
    prepared = prepare_composition(ir, context)
    source = next(b for b in prepared['sources'] if 'Defines how structured' in b['text'])
    evidence = [{'source': source['id'], 'quote': source['text']}]
    document = {
        'schema': 'forge/visual-doc-composition@1',
        'source_fingerprint': prepared['source_fingerprint'],
        'context': prepared['context'],
        'title': '문서의 근거를 확인하는 방법',
        'lead': {'text': '문서와 규칙의 출처를 찾아갈 수 있도록 합니다.', 'refs': evidence},
        'questions': [{'text': '무엇을 위한 기능인가?', 'answer_blocks': ['purpose']}],
        'sections': [{'id': 'understanding', 'title': '문서의 목적', 'blocks': [
            {'id': 'purpose', 'type': 'prose', 'text': '문서와 규칙이 어느 원문에서 왔는지 확인할 수 있습니다.', 'refs': evidence}
        ]}],
        'review': {'method': 'agent', 'reviewer': 'fixture reviewer', 'notes': '원문의 목적만 설명하며 추가 정책을 만들지 않았습니다.'},
    }
    return ir, context, document


class CompositionTest(unittest.TestCase):
    def test_explanation_is_readable_without_source_file_enumeration(self):
        ir, context, document = fixture()
        validate_composition(document, ir, context)
        markup = render_composition(document, ir, context)
        self.assertIn('문서와 규칙이 어느 원문에서 왔는지', markup)
        self.assertIn('무엇을 위한 기능인가?', markup)
        self.assertIn('Defines how structured', markup)
        self.assertNotIn(' entities', markup)

    def test_changed_sources_and_context_require_reconsideration(self):
        ir, context, document = fixture()
        for altered in [dict(document, source_fingerprint='0'*64), dict(document, context=dict(document['context'], audience='engineering'))]:
            with self.assertRaisesRegex(ValueError, 'STALE|CONTEXT'):
                validate_composition(altered, ir, context)

    def test_missing_or_false_evidence_and_unanswered_questions_fail(self):
        ir, context, document = fixture()
        variants = []
        for field, value in [('refs', []), ('refs', [{'source': 'invented', 'quote': 'no source'}]), ('refs', [dict(document['lead']['refs'][0], quote='invented quote')])]:
            bad = deepcopy(document)
            bad['sections'][0]['blocks'][0][field] = value
            variants.append(bad)
        bad = deepcopy(document)
        bad['questions'][0]['answer_blocks'] = ['not-an-answer']
        variants.append(bad)
        for bad in variants:
            with self.assertRaises(ValueError):
                validate_composition(bad, ir, context)

    def test_html_is_rejected_and_question_links_are_internal(self):
        ir, context, document = fixture()
        bad = deepcopy(document)
        bad['sections'][0]['blocks'][0]['text'] = '<script>alert(1)</script>'
        with self.assertRaisesRegex(ValueError, 'MARKUP'):
            validate_composition(bad, ir, context)
        self.assertIn('href="#reading-purpose"', render_composition(document, ir, context))

    def test_schema_does_not_claim_semantic_or_human_verification(self):
        ir, context, document = fixture()
        # A real quote does not prove the explanation entails it. This must stay
        # explicit instead of treating the schema as an entailment checker.
        document['sections'][0]['blocks'][0]['text'] = 'A deliberately incorrect interpretation for semantic review.'
        validate_composition(document, ir, context)
        output = render_composition(document, ir, context)
        self.assertIn('읽기 검증 필요', output)
        self.assertIn('agent', output)

    def test_plain_generic_type_identifier_is_escaped_without_renaming(self):
        ir, context, document = fixture()
        document['sections'][0]['blocks'][0]['text'] = 'List<T> keeps its exact type identifier.'
        validate_composition(document, ir, context)
        self.assertIn('List&lt;T&gt;', render_composition(document, ir, context))

    def test_example_assumptions_and_conditional_flow_are_preserved(self):
        ir, context, document = fixture()
        refs = document['lead']['refs']
        document['sections'][0]['blocks'] += [
            {'id': 'sample', 'type': 'example', 'text': '설명용 문서를 선택한 예시입니다.', 'assumptions': ['실제 운영 결과를 나타내지 않습니다.'], 'refs': refs},
            {'id': 'route', 'type': 'flow', 'text': '조건을 먼저 확인합니다.', 'refs': refs,
             'nodes': [{'id': 'a', 'text': '확인', 'refs': refs}, {'id': 'b', 'text': '이동', 'refs': refs}],
             'edges': [{'from': 'a', 'to': 'b', 'text': '근거가 있을 때', 'refs': refs}]},
        ]
        validate_composition(document, ir, context)
        output = render_composition(document, ir, context)
        self.assertIn('근거가 있을 때', output)
        self.assertIn('실제 운영 결과를 나타내지 않습니다.', output)
        self.assertIn('Derived view', output)
        self.assertEqual(output, render_composition(deepcopy(document), ir, context))


if __name__ == '__main__':
    unittest.main()
