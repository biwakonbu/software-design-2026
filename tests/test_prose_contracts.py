"""Review-tool regressions: accept explanations, reject changes to delivered contracts."""
from pathlib import Path
import importlib.util
import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'scripts/check-prose-contracts.py'
spec = importlib.util.spec_from_file_location('prose_contracts', path)
contracts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contracts)


class ProseContractTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {
            'lectures/03.md': ('---\ntitle: 第3回\n---\n# 追跡\n結果を読む。\n'
                               '値は `3` です。\n| 入力 | 期待値 |\n| --- | --- |\n| 1 | 3 |\n'
                               '```python\nprint(1 + 2)\n```\n[演習](../exercises/03.md)\n').encode(),
            'lectures/02.md': '# 保護教材\n既存の説明です。\n'.encode(),
            'examples/03-ai-workflow/verify.py': b'assert 1 + 2 == 3\n',
            'output/pdf/02-python-basics.pdf': b'%PDF-protected',
            'output/pdf/03-ai-workflow.pdf': b'%PDF-generated',
            'scripts/build-slides.mjs': b'original build\n',
        }

    def check(self, name=None, old=None, new=None, allowances=()):
        current = dict(self.baseline)
        if name:
            current[name] = current[name].replace(old, new)
        return contracts.compare_snapshots(self.baseline, current, allowances)

    def test_polite_explanation_is_accepted(self):
        self.assertTrue(self.check('lectures/03.md', '結果を読む。'.encode(), '結果を読んでください。'.encode())['passed'])

    def test_fenced_example_change_is_rejected(self):
        self.assertFalse(self.check('lectures/03.md', b'print(1 + 2)', b'print(1 - 2)')['passed'])

    def test_acceptance_table_change_is_rejected(self):
        self.assertFalse(self.check('lectures/03.md', b'| 1 | 3 |', b'| 1 | 4 |')['passed'])

    def test_slide_order_metadata_and_links_are_protected(self):
        for old, new in [(b'---\n#', b'#'), ('title: 第3回'.encode(), 'title: 変更'.encode()),
                         (b'../exercises/03.md', b'../exercises/04.md')]:
            with self.subTest(old=old):
                self.assertFalse(self.check('lectures/03.md', old, new)['passed'])

    def test_lesson02_source_and_pdf_are_frozen(self):
        self.assertFalse(self.check('lectures/02.md', '既存'.encode(), '新規'.encode())['passed'])
        self.assertFalse(self.check('output/pdf/02-python-basics.pdf', b'protected', b'changed')['passed'])

    def test_executable_code_is_frozen(self):
        self.assertFalse(self.check('examples/03-ai-workflow/verify.py', b'== 3', b'== 4')['passed'])

    def test_generated_pdf_can_change_but_cannot_disappear(self):
        self.assertTrue(self.check('output/pdf/03-ai-workflow.pdf', b'generated', b'new')['passed'])
        current = dict(self.baseline)
        del current['output/pdf/03-ai-workflow.pdf']
        self.assertFalse(contracts.compare_snapshots(self.baseline, current)['passed'])

    def test_tooling_change_requires_explicit_named_allowance(self):
        name = 'scripts/build-slides.mjs'
        self.assertFalse(self.check(name, b'original', b'new')['passed'])
        result = self.check(name, b'original', b'new', allowances=[name])
        self.assertTrue(result['passed'])
        self.assertEqual(result['allowed_tooling_changes'], [name])
        self.assertFalse(self.check(allowances=['lectures/02.md'])['passed'])

    def cli_fixture(self, folder):
        baseline, current = folder / 'baseline', folder / 'current'
        baseline.mkdir()
        current.mkdir()
        for root in [baseline, current]:
            (root / 'lectures').mkdir()
            (root / 'lectures/03.md').write_bytes(self.baseline['lectures/03.md'])
        return baseline, current

    def test_cli_writes_a_new_report_outside_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            baseline, current = self.cli_fixture(folder)
            output = folder / 'reports/check.json'
            arguments = ['check-prose-contracts.py', '--root', str(current), '--baseline-dir', str(baseline), '--out', str(output)]
            with patch.object(contracts, 'git', return_value=b'lectures/03.md\0'), patch('sys.argv', arguments), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(contracts.main(), 0)
            self.assertTrue(json.loads(output.read_text())['passed'])

    def test_cli_rejects_existing_and_hard_link_outputs_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            baseline, current = self.cli_fixture(folder)
            protected = baseline / 'lectures/03.md'
            ordinary = folder / 'existing.json'
            ordinary.write_bytes(b'existing report')
            linked = folder / 'hard-link.json'
            os.link(protected, linked)
            for output in [ordinary, linked]:
                before = output.read_bytes()
                arguments = ['check-prose-contracts.py', '--root', str(current), '--baseline-dir', str(baseline), '--out', str(output)]
                with self.subTest(output=output.name), patch.object(contracts, 'git', return_value=b'lectures/03.md\0'), patch('sys.argv', arguments), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as failure:
                        contracts.main()
                    self.assertEqual(failure.exception.code, 2)
                self.assertEqual(output.read_bytes(), before)
                self.assertEqual(protected.read_bytes(), self.baseline['lectures/03.md'])


if __name__ == '__main__':
    unittest.main()
