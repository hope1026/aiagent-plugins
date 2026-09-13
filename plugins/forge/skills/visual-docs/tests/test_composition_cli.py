"""CLI acceptance for source-bound explanations, independent of source browsing.

The fixtures contain authored answers. These tests establish preservation,
readability structure and lifecycle safety; they do not certify comprehension.
"""
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

TEST_DIR = Path(__file__).resolve().parent
SCRIPT = TEST_DIR.parent / 'scripts/build_review_viewer.py'
FIXTURES = TEST_DIR / 'fixtures'
STAMP = '2026-09-13T00:00:00Z'


class ReadingText(HTMLParser):
    """Read the explanatory layer without its hidden evidence or source library."""
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag == 'details':
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def manifest(markup):
    return json.loads(re.search(r'<script[^>]*id="forge-source-manifest"[^>]*>(.*?)</script>', markup, re.S).group(1))


class CompositionCLI(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        shutil.copytree(FIXTURES / 'repository', self.repo, dirs_exist_ok=True)
        shutil.copytree(FIXTURES / 'comprehension', self.repo / 'inputs')
        shutil.copy2(FIXTURES / 'brief.md', self.repo / 'brief.md')
        self.git('init', '-q')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '--allow-empty', '-qm', 'fixture')

    def git(self, *args):
        subprocess.run(['git', *args], cwd=self.repo, check=True, capture_output=True)

    def cli(self, args, *, ok=True, script=SCRIPT):
        result = subprocess.run([sys.executable, str(script), *args], cwd=self.repo,
                                text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def args(self, kind='brief', locale='en', source=None):
        inputs = {
            'brief': ['--brief', source or 'brief.md'],
            'spec': ['--spec', source or 'docs/specs/semantic-spec-bundles'],
            'plan': ['--plan', 'docs/plans/001-demo/plan.md'],
            'project': ['--project-map', 'docs/project/project-map.md'],
        }
        return ['--kind', kind, *inputs[kind], '--view-id', 'comprehension',
                '--locale', locale, '--generated-at', STAMP, '--offline']

    def prepare(self, args):
        return json.loads(self.cli([*args, '--prepare', '--format', 'json']).stdout)

    def ref(self, packet, quote):
        source = next(s for s in packet['sources'] if quote in s['text'] or quote == s['heading'])
        return [{'source': source['id'], 'quote': quote}]

    def composition(self, packet, quote, answer='A readable explanation of the selected source.', question='What does this source explain?'):
        refs = self.ref(packet, quote)
        return {'schema': packet['schema'], 'source_fingerprint': packet['source_fingerprint'],
                'context': packet['context'], 'title': 'Understanding the selected work',
                'lead': {'text': answer, 'refs': refs},
                'questions': [{'text': question, 'answer_blocks': ['answer']}],
                'sections': [{'id': 'explanation', 'title': 'How it works', 'blocks': [
                    {'id': 'answer', 'type': 'prose', 'text': answer, 'refs': refs}]}],
                'review': {'method': 'agent', 'reviewer': 'integration fixture author',
                           'notes': 'Source excerpts reviewed; human reading assessment remains separate.'}}

    def write_composition(self, value):
        path = self.repo / 'composition.json'
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return ['--composition', 'composition.json']

    def build(self, args, value):
        result = self.cli([*args, *self.write_composition(value)])
        return self.repo / result.stdout.strip()

    def test_prepare_is_read_only_and_default_preflight_labels_source_browser(self):
        for kind in ('brief', 'plan', 'spec', 'project'):
            with self.subTest(kind=kind):
                args = self.args(kind)
                before = {str(p.relative_to(self.repo)): p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
                packet = self.prepare(args)
                self.assertRegex(packet['source_fingerprint'], r'^[0-9a-f]{64}$')
                self.assertEqual(packet['context']['kind'], kind)
                self.assertTrue(any(s['text'].strip() for s in packet['sources']))
                payload = json.loads(self.cli([*args, '--dry-run', '--format', 'json']).stdout)
                self.assertEqual(payload['quality'], 'source-browser')
                after = {str(p.relative_to(self.repo)): p.read_bytes() for p in self.repo.rglob('*') if p.is_file()}
                self.assertEqual(before, after)

    def test_brief_with_list_and_following_explanation_keeps_both_source_blocks(self):
        source = self.repo / 'brief.md'
        condition = 'A newly documented condition belongs to this work.'
        source.write_text(source.read_text() + '\n' + condition + '\n')
        args = self.args()
        packet = self.prepare(args)
        self.assertTrue(any(condition in row['text'] for row in packet['sources']))
        value = self.composition(packet, condition, condition)
        output = self.build(args, value)
        self.assertIn('The brief is readable', output.read_text())
        self.assertIn(condition, output.read_text())

    def test_all_four_kinds_keep_explanation_before_originals_without_source_changes(self):
        examples = {
            'brief': ('Explain the requested work.', 'This brief explains the requested work.'),
            'spec': ('Defines how structured Spec Bundle members and statements remain traceable.', 'The spec explains how to trace bundle members and statements.'),
            'plan': ('Build a deterministic review source bundle.', 'This plan builds a deterministic review source bundle.'),
            'project': ('Forge 문서를 사람이 이해하기 쉬운 화면으로 제공한다.', 'The project presents Forge documents in an understandable view.'),
        }
        for kind, (quote, answer) in examples.items():
            with self.subTest(kind=kind):
                args = self.args(kind)
                packet = self.prepare(args)
                source_bytes = {s['path']: (self.repo / s['path']).read_bytes() for s in packet['sources']}
                value = self.composition(packet, quote, answer)
                preflight = json.loads(self.cli([*args, *self.write_composition(value), '--dry-run', '--format', 'json']).stdout)
                self.assertEqual(preflight['quality'], 'reading-check-required')
                self.assertEqual(preflight['composition'], value)
                output = self.build(args, value)
                first = output.read_bytes()
                markup = first.decode()
                reading = markup[markup.index('<div class="reading-document"'):re.search(r'<(?:details|section) class="reading-source-library"', markup).start()]
                self.assertIn(answer, reading)
                self.assertIn('href="#reading-answer"', reading)
                self.assertIn('id="reading-answer"', reading)
                self.assertIn('id="reading-originals"', markup)
                self.assertEqual(manifest(markup)['composition'], value)
                self.assertEqual(manifest(markup)['quality'], 'reading-check-required')
                self.build(args, value)
                self.assertEqual(first, output.read_bytes())
                self.assertEqual(source_bytes, {p: (self.repo / p).read_bytes() for p in source_bytes})

    def test_prose_workflow_and_policy_answers_survive_without_opening_sources(self):
        for name in ('workflow-en', 'workflow-ko', 'policy-en', 'policy-ko'):
            with self.subTest(case=name):
                case = json.loads((self.repo / 'inputs' / (name + '.json')).read_text())
                bundle = self.repo / 'docs/specs' / name
                bundle.mkdir()
                shutil.copy2(self.repo / 'inputs' / (name + '.md'), bundle)
                args = self.args(kind='spec', locale=name[-2:], source='docs/specs/' + name)
                packet = self.prepare(args)
                value = self.composition(packet, case['quote'], case['answer'], case['question'])
                block = value['sections'][0]['blocks'][0]
                if name.startswith('workflow'):
                    block['type'] = 'flow'
                    source_quote = next(s['text'] for s in packet['sources'] if case['quote'] in s['text'])
                    block['nodes'] = [{'id': key, 'text': label, 'refs': self.ref(packet, source_quote)} for key, label in case['nodes']]
                    block['edges'] = [{'from': src, 'to': dst, 'text': label, 'refs': self.ref(packet, quote)} for src, dst, label, quote in case['edges']]
                else:
                    block['type'] = 'table'
                    block['columns'] = case['columns']
                    block['rows'] = [{'cells': cells, 'refs': self.ref(packet, quote)} for cells, quote in case['rows']]
                markup = self.build(args, value).read_text()
                reading = markup[markup.index('<div class="reading-document"'):re.search(r'<(?:details|section) class="reading-source-library"', markup).start()]
                parser = ReadingText()
                parser.feed(reading)
                visible = ' '.join(parser.parts)
                for text in (case['question'], case['answer'], *case['expected']):
                    self.assertIn(text, visible)
                self.assertNotIn('inputs/', visible)
                self.assertIn('data-reading-type="' + block['type'] + '"', reading)

    def test_invalid_composition_does_not_replace_existing_output(self):
        args = self.args()
        original = self.composition(self.prepare(args), 'Explain the requested work.')
        output = self.build(args, original)
        before = output.read_bytes()
        variants = []
        stale = deepcopy(original)
        stale['source_fingerprint'] = '0' * 64
        variants.append((stale, 'COMPOSITION_STALE'))
        context = deepcopy(original)
        context['context']['audience'] = 'operations'
        variants.append((context, 'COMPOSITION_CONTEXT'))
        quote = deepcopy(original)
        quote['sections'][0]['blocks'][0]['refs'][0]['quote'] = 'No source ever states this.'
        variants.append((quote, 'COMPOSITION_QUOTE'))
        for value, diagnostic in variants:
            with self.subTest(diagnostic=diagnostic):
                result = self.cli([*args, *self.write_composition(value)], ok=False)
                self.assertIn(diagnostic, result.stderr)
                self.assertEqual(output.read_bytes(), before)
        self.write_composition(original)
        source = self.repo / 'brief.md'
        source.write_text(source.read_text().replace('Explain the requested work.', 'Explain the newly requested work.'))
        result = self.cli([*args, '--composition', 'composition.json'], ok=False)
        self.assertIn('COMPOSITION_STALE', result.stderr)
        self.assertEqual(output.read_bytes(), before)

    def test_copied_plugin_runtime_produces_identical_generator_and_output(self):
        args = self.args()
        value = self.composition(self.prepare(args), 'Explain the requested work.')
        output = self.build(args, value)
        original = output.read_bytes()
        original_manifest = manifest(original.decode())
        self.assertRegex(original_manifest['generator']['sha256'], r'^[0-9a-f]{64}$')
        copied_skills = self.repo / 'isolated-plugin/skills'
        for skill in ('visual-docs', 'writing-specs'):
            source = TEST_DIR.parent.parent / skill
            for folder in ('scripts', 'assets'):
                if (source / folder).is_dir():
                    shutil.copytree(source / folder, copied_skills / skill / folder,
                                    ignore=shutil.ignore_patterns('__pycache__'))
        copied_script = copied_skills / 'visual-docs/scripts/build_review_viewer.py'
        self.cli([*args, '--composition', 'composition.json'], script=copied_script)
        copied = output.read_bytes()
        self.assertEqual(manifest(copied.decode())['generator'], original_manifest['generator'])
        self.assertEqual(copied, original)
        # This is runtime relocation parity, not a claim about live app installation.

    def test_composition_file_participates_in_read_only_freshness_checks(self):
        args = self.args()
        value = self.composition(self.prepare(args), 'Explain the requested work.')
        output = self.build(args, value)
        before = output.read_bytes()
        check = ['--check', str(output), '--repo-root', str(self.repo), '--format', 'json']
        current = json.loads(self.cli(check).stdout)
        self.assertEqual(current['overall'], 'current')
        value['lead']['text'] = 'A revised explanation awaits regeneration.'
        self.write_composition(value)
        stale = json.loads(self.cli(check, ok=False).stdout)
        self.assertEqual(stale['overall'], 'stale')
        self.assertTrue(any('composition.json' in diagnostic for diagnostic in stale['diagnostics']))
        self.assertEqual(before, output.read_bytes())
        (self.repo / 'composition.json').unlink()
        missing = json.loads(self.cli(check, ok=False).stdout)
        self.assertEqual(missing['overall'], 'missing')
        self.assertEqual(before, output.read_bytes())


if __name__ == '__main__':
    unittest.main()
