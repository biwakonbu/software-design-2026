"""保護範囲・位置・教材別分類と、更新された入力の拒否を確認する回帰テスト。"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/material_prose.py'
spec = importlib.util.spec_from_file_location('material_prose', SCRIPT)
mp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mp
spec.loader.exec_module(mp)


class ExtractionTests(unittest.TestCase):
    def test_markdown_protects_code_quote_exercise_answer_and_values(self):
        text = ('---\ntitle: テスト\n---\n# 説明\n設定を確認します。\n'
                '```python\nprint("秘密の構文")\n```\n'
                '> 引用を変更することができます。\n引用の継続です。\n\n'
                '## 演習\n数値100を変えてください。\n## 解答\n答えは200です。\n'
                '## 説明に戻る\nファイルを保存します。\n|値|結果|\n|---|---|\n|1|2|\n')
        docs, protected = mp.markdown(text, 'lecture.md', 'university', 'slides')
        combined = '\n'.join(f.text for d in docs for f in d.fragments)
        self.assertIn('設定を確認します。', combined)
        self.assertIn('ファイルを保存します。', combined)
        for excluded in ['秘密', '引用', '100', '200', '|1|2|', 'title:']:
            self.assertNotIn(excluded, combined)
        self.assertEqual(next(f.line for f in docs[0].fragments if '保存' in f.text), 17)
        self.assertTrue(any(x['reason'] == 'code' for x in protected))

    def test_slide_number_survives_protected_slide(self):
        text = '# 説明\n保存します。\n---\n# 演習\n答えを書いてください。\n---\n# 復習\n保存方法を復習します。\n'
        docs, _ = mp.markdown(text, 'deck.md', 'university', 'slides', True)
        self.assertEqual([d.unit for d in docs], ['1', '3'])
        self.assertEqual(docs[-1].fragments[-1].role, 'recap')

    def test_html_protects_svg_script_and_attributes_keeps_visible_text(self):
        text = '<div data-example="未知の属性">表示説明を確認します。</div>\n<svg>\n<text>図中の秘密</text>\n</svg>\n<script>実行しない日本語</script>\n<!--\n非表示の引用\n-->\n表示を保存します。\n'
        docs, _ = mp.markdown(text, 'deck.md', 'university', 'slides')
        combined = '\n'.join(f.text for d in docs for f in d.fragments)
        self.assertIn('表示説明を確認します。', combined)
        self.assertIn('表示を保存します。', combined)
        for excluded in ['未知', '秘密', '実行しない', '非表示']:
            self.assertNotIn(excluded, combined)

    def test_typst_preserves_terms_protects_prompt_code_table_and_quote(self):
        text = ('#import "hidden.typ": example\n#let chapter() = {\n'
                'spread("定義を確認する", [\n#term("agent") は道具を使います。\n'
                '#artifact("依頼例", [引用を変更することができます。], kind: "入力例")\n'
                '#table([値を変えてください。], [100])\n'
                '#quote[引用を編集しない。]\n`実行コード`\n'
                '確認結果を保存します。\n])\n}\n')
        docs, protected = mp.typst(text, 'chapter.typ', 'bootcamp', 'book', {'agent': 'エージェント'})
        combined = '\n'.join(f.text for d in docs for f in d.fragments)
        self.assertIn('エージェント は道具を使います。', combined)
        self.assertIn('確認結果を保存します。', combined)
        for excluded in ['引用を変更', '値を変え', '100', '引用を編集', '実行コード', 'hidden.typ']:
            self.assertNotIn(excluded, combined)
        self.assertTrue(any(x['reason'] == 'typst-artifact' for x in protected))
        self.assertTrue(all(f.approximate for f in docs[0].fragments))

    def test_json_selects_display_fields_and_distinguishes_equal_strings(self):
        text = '[\n {"title":"確認方法", "body":"結果を確認します。", "code":"実行しないコード", "notes":"講師専用の引用", "messages":[{"text":"対話の引用"}]},\n {"title":"復習", "body":"結果を確認します。"},\n {"title":"演習", "body":"答えは200です。"}\n]'
        docs, protected = mp.slide_json(text, 'content.json', 'bootcamp', 'slides')
        self.assertEqual(len(docs), 2)
        body_fragments = [f for d in docs for f in d.fragments if '結果' in f.text]
        self.assertEqual([f.line for f in body_fragments], [2, 3])
        self.assertEqual(body_fragments[-1].role, 'recap')
        combined = '\n'.join(f.text for d in docs for f in d.fragments)
        for excluded in ['コード', '講師専用', '対話の引用', '200']:
            self.assertNotIn(excluded, combined)
        self.assertTrue(protected)

    def test_wrapped_markdown_sentence_keeps_paragraph_and_line_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            (out / 'corpus').mkdir()
            doc = mp.Document('a.md', 'university', 'reference', '1',
                              [mp.Fragment('条件を確認し、', 2), mp.Fragment('結果を保存します。', 3)])
            data = mp.serialize_document(doc, out, 1)
            self.assertEqual((out / data['corpus']).read_text(), '条件を確認し、\n結果を保存します。\n\n')
            mapped = mp.map_location({'file': data['corpus'], 'span': {'line': 2, 'col': 1}}, {data['corpus']: data})
            self.assertEqual(mapped['line'], 3)

    def test_typst_bare_url_is_not_a_comment_or_unclosed_delimiter(self):
        text = 'spread("参照先を確認", [公式の説明は https://example.com/docs を参照します。])\n[次の内容を保存します。]'
        docs, _ = mp.typst(text, 'chapter.typ', 'bootcamp', 'book', {})
        combined = '\n'.join(f.text for d in docs for f in d.fragments)
        self.assertIn('次の内容を保存します。', combined)
        self.assertNotIn('https://', combined)

    def test_typst_diagram_labels_do_not_become_one_long_sentence(self):
        text = 'spread("説明を読む", [\n#flow(((title: "入力を読む", detail: [必要な条件を確認]), (title: "結果を残す", detail: "記録を保存")), caption: "図の説明です。")\n本文を確認します。\n])'
        docs, _ = mp.typst(text, 'chapter.typ', 'bootcamp', 'book', {})
        labels = [f.text for f in docs[0].fragments if f.role == 'label']
        self.assertEqual(labels, ['入力を読む', '必要な条件を確認', '結果を残す', '記録を保存'])
        self.assertTrue(all(')' not in f.text for f in docs[0].fragments))
        self.assertIn('本文を確認します。', [f.text for f in docs[0].fragments])

    def test_unreviewed_binary_is_rejected_without_launch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            (root / 'lectures').mkdir(parents=True)
            (root / 'lectures/03.md').write_text('# 説明\n内容を確認します。')
            out = Path(temp) / 'out'
            mp.extract('university', root, out)
            binary = Path(temp) / 'unknown-binary'
            binary.write_text('never execute this file')
            with patch.object(mp.subprocess, 'run') as launch:
                with self.assertRaisesRegex(ValueError, 'reviewed pin'):
                    mp.analyze(out, binary)
                launch.assert_not_called()

    def test_typst_markup_heading_is_not_body_and_sets_recap_context(self):
        text = 'spread([復習を#linebreak()続ける], [内容を思い出します。])'
        docs, _ = mp.typst(text, 'chapter.typ', 'bootcamp', 'book', {})
        self.assertEqual(docs[0].fragments[0].role, 'heading')
        self.assertEqual(docs[0].fragments[-1].role, 'recap')

    def test_jaio_cross_doc_maps_primary_and_counterpart(self):
        docs = {'corpus/a.md': {'source': 'a.typ', 'course': 'bootcamp', 'medium': 'book', 'unit': '1', 'line_map': [{'line': 9}]},
                'corpus/b.md': {'source': 'b.json', 'course': 'bootcamp', 'medium': 'slides', 'unit': '1', 'line_map': [{'line': 3}]}}
        diagnostic = {'file': 'corpus/a.md', 'span': {'line': 1, 'col': 1}, 'locations': [{'file': 'corpus/b.md', 'span': {'line': 1, 'col': 1}}]}
        mapped = mp.map_diagnostic(diagnostic, docs)
        self.assertEqual([x['line'] for x in mapped], [9, 3])
        self.assertEqual(mp.duplicate_class(mapped)[0], 'book_slide_alignment')

    def test_source_and_corpus_mutations_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            root.mkdir()
            (root / 'lectures').mkdir()
            (root / 'lectures/03.md').write_text('# 説明\n変更内容を確認します。\n')
            out = Path(temp) / 'output'
            manifest = mp.extract('university', root, out)
            mp.verify_inputs(manifest, out)
            (root / 'lectures/03.md').write_text('# 説明\n本人が変更しました。\n')
            with self.assertRaisesRegex(ValueError, 'inputs changed'):
                mp.verify_inputs(manifest, out)

    def test_output_cannot_be_inside_sources_or_overwrite_previous_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(ValueError, 'outside'):
                mp.exclusive_output(root / 'report', [root])
            out = root / 'existing'
            out.mkdir()
            with self.assertRaises(FileExistsError):
                mp.exclusive_output(out, [])

    def test_symlink_escape_is_rejected_before_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'source'
            (root / 'lectures').mkdir(parents=True)
            outside = Path(temp) / 'private.md'
            outside.write_text('対象外の秘密')
            (root / 'lectures/03.md').symlink_to(outside)
            with self.assertRaisesRegex(ValueError, 'escapes'):
                mp.extract('university', root, Path(temp) / 'out')

    def test_book_override_uses_current_staging_and_keeps_slide_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root, book = Path(temp) / 'repo', Path(temp) / 'current-book'
            (root / 'products/bootcamp/books/old').mkdir(parents=True)
            (root / 'products/bootcamp/books/old/main.typ').write_text('[旧本文です。]')
            slides = root / 'products/bootcamp/slides/day-01/src'
            slides.mkdir(parents=True)
            (slides / 'content.json').write_text('[{"title":"現在のスライド", "body":"内容を確認します。"}]')
            book.mkdir()
            (book / 'main.typ').write_text('[現在の書籍です。]')
            manifest = mp.extract('bootcamp', root, Path(temp) / 'out', book)
            text = '\n'.join(f['text'] for d in manifest['documents'] for f in d['fragments'])
            self.assertIn('現在の書籍', text)
            self.assertIn('現在のスライド', text)
            self.assertNotIn('旧本文', text)
            self.assertEqual(len(manifest['roots']), 2)


class ClassificationTests(unittest.TestCase):
    def location(self, course='bootcamp', medium='book', role='body', source='chapter.typ'):
        return {'course': course, 'medium': medium, 'role': role, 'source': source}

    def test_definition_recap_and_cross_course_are_not_bad_duplicates(self):
        for role in ('definition', 'recap'):
            self.assertEqual(mp.duplicate_class([self.location(role=role), self.location()])[0], 'learning_repetition_candidate')
        self.assertEqual(mp.duplicate_class([self.location(), self.location(course='university')])[0], 'shared_foundation_candidate')
        self.assertEqual(mp.duplicate_class([self.location(), self.location(medium='slides')])[0], 'book_slide_alignment')

    def test_within_same_and_cross_material_need_review(self):
        self.assertEqual(mp.duplicate_class([self.location(), self.location()])[0], 'within_material_review')
        self.assertEqual(mp.duplicate_class([self.location(), self.location(source='other.typ')])[0], 'cross_material_review')
        self.assertEqual(mp.duplicate_class([self.location()])[0], 'review_required')

    def test_ambiguity_is_supplemental_and_never_a_definite_error(self):
        doc = mp.Document('chapter.typ', 'bootcamp', 'book', '1', [mp.Fragment('適切に設定してください。', 8)])
        result = mp.supplementary({'documents': [mp.asdict(doc)]})
        self.assertEqual(result[0]['origin'], 'supplement')
        self.assertEqual(result[0]['severity'], 'info')
        self.assertIn('確定しません', result[0]['limitation'])

    def test_past_observation_is_not_an_ambiguous_instruction(self):
        doc = mp.Document('a.typ', 'bootcamp', 'book', '1', [mp.Fragment('うまくいった説明だけを保存せず、確認した条件を残します。', 2)])
        self.assertEqual(mp.supplementary({'documents': [mp.asdict(doc)]}), [])

    def test_exact_repeat_is_only_a_candidate(self):
        sentence = '目的と変更範囲を確認し、検査方法と期待する結果を資料に記録してください。' * 2
        docs = [mp.asdict(mp.Document('a.typ', 'bootcamp', 'book', '1', [mp.Fragment(sentence, 2)])),
                mp.asdict(mp.Document('deck.json', 'bootcamp', 'slides', '1', [mp.Fragment(sentence, 9)]))]
        result = mp.supplementary({'documents': docs})
        self.assertEqual(result[0]['classification'], 'book_slide_alignment')

    def test_profiles_only_override_verified_jaio_thresholds(self):
        self.assertIn('long_sentence_min_chars = 40', mp.config_for('bootcamp'))
        self.assertIn('long_sentence_min_chars = 80', mp.config_for('university'))
        self.assertIn('"relation/broken-link" = "allow"', mp.config_for('bootcamp'))
        self.assertNotIn('past-tense', mp.config_for('bootcamp'))


if __name__ == '__main__':
    unittest.main()
