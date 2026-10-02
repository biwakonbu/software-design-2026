"""自習デモの公開期待値と、学習で使う関数の境界を検証する。"""

from contextlib import redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples" / "02-basics" / "concepts.py"
spec = importlib.util.spec_from_file_location("basics_concepts", SCRIPT)
concepts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(concepts)

# READMEは実装とは独立した出力契約。巨大な期待値の複製を避けて照合する。
README = SCRIPT.with_name("README.md").read_text(encoding="utf-8")
EXPECTED = dict(re.findall(r"### `([^`]+)`\n.*?```text\n(.*?)```", README, re.DOTALL))


class CaseOutputTests(unittest.TestCase):
    def check_case(self, name):
        result = subprocess.run([sys.executable, str(SCRIPT), name], cwd=ROOT,
                                text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, EXPECTED[name])

    def test_rebinding(self):
        self.check_case("rebinding")

    def test_types(self):
        self.check_case("types")

    def test_conversion(self):
        self.check_case("conversion")

    def test_conditions(self):
        self.check_case("conditions")

    def test_lists(self):
        self.check_case("lists")

    def test_shallow_copy(self):
        self.check_case("shallow-copy")

    def test_dictionary(self):
        self.check_case("dictionary")

    def test_for_trace(self):
        self.check_case("for-trace")

    def test_range(self):
        self.check_case("range")

    def test_while_update(self):
        self.check_case("while-update")

    def test_functions(self):
        self.check_case("functions")

    def test_exception_types_and_real_traceback_excerpt(self):
        self.check_case("exceptions")


class ConceptFunctionTests(unittest.TestCase):
    def test_documented_case_inventory(self):
        self.assertEqual(set(EXPECTED), set(concepts.CASES))
        self.assertEqual(len(EXPECTED), 12)

    def test_integer_string_conversion_boundaries(self):
        for text, expected in (("0", 0), ("-1", -1), (" 2 ", 2), ("+2", 2)):
            with self.subTest(text=text):
                self.assertEqual(concepts.convert_integer(text), expected)
        for text in ("", "two", "2.5"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                concepts.convert_integer(text)

    def test_returned_value_is_available_to_caller(self):
        amount = concepts.subtotal(200, 2)
        self.assertEqual(amount + 10, 410)
        self.assertEqual(concepts.subtotal(200, 0), 0)

    def test_print_only_function_returns_none(self):
        stream = StringIO()
        with redirect_stdout(stream):
            result = concepts.show_subtotal(200, 2)
        self.assertEqual(stream.getvalue(), "display: 400\n")
        self.assertIsNone(result)
        with self.assertRaises(TypeError):
            result + 10

    def test_parameter_rebinding_preserves_callers_name(self):
        number = 100
        self.assertEqual(concepts.local_increment(number), 101)
        self.assertEqual(number, 100)

    def test_argument_count_is_checked_at_call(self):
        with self.assertRaises(TypeError):
            concepts.subtotal(200)

    def test_annotations_do_not_validate_types(self):
        # 計算だけの教材関数と、入力検証付きorder_summaryを区別する。
        self.assertEqual(concepts.subtotal("a", 3), "aaa")

    def test_cases_can_run_twice_without_retained_mutation(self):
        for name, demo in concepts.CASES.items():
            with self.subTest(case=name):
                for _ in range(2):
                    stream = StringIO()
                    with redirect_stdout(stream):
                        demo()
                    self.assertEqual(stream.getvalue(), EXPECTED[name])


class CLIUsageTests(unittest.TestCase):
    def test_missing_or_unknown_case_is_usage_error(self):
        for args in ([], ["unknown-case"]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(SCRIPT), *args],
                                        text=True, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("usage:", result.stderr)

    def test_help_lists_every_case(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                                text=True, capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        for name in concepts.CASES:
            self.assertIn(name, result.stdout)


if __name__ == "__main__":
    unittest.main()
