"""二分探索の公開学習例を、仕様から作った独立の期待値で検証する。"""

import io
import itertools
import os
from pathlib import Path
import subprocess
import sys
import unittest

from binary_search_buggy import binary_search as buggy
from binary_search_corrected import binary_search as corrected
from verify import verify


class SearchContractTests(unittest.TestCase):
    exhaustive_cases = 0

    def assert_contract(self, values, target):
        before = values.copy()
        result = corrected(values, target)
        # 線形の存在判定を使う。二分探索の境界計算を期待値へ写さない。
        if target in values:
            self.assertIs(type(result), int)
            self.assertGreaterEqual(result, 0)
            self.assertLess(result, len(values))
            self.assertEqual(values[result], target)
        else:
            self.assertIsNone(result)
        self.assertEqual(values, before)

    def test_found_and_endpoints(self):
        for values, target, expected in [([1], 1, 0), ([1, 3, 5], 1, 0),
                                         ([1, 3, 5], 5, 2), ([-5, -2, 0], -2, 1)]:
            with self.subTest(values=values, target=target):
                self.assert_contract(values, target)
                self.assertEqual(corrected(values, target), expected)

    def test_empty_and_absent(self):
        for values, target in [([], 1), ([1], 0), ([1], 2), ([1, 3, 5], 4),
                                ([1, 3, 5], -1), ([1, 3, 5], 6)]:
            with self.subTest(values=values, target=target):
                self.assert_contract(values, target)

    def test_duplicates_allow_any_matching_index(self):
        for values, target in [([2, 2, 2], 2), ([-1, 0, 0, 0, 3], 0)]:
            with self.subTest(values=values, target=target):
                self.assert_contract(values, target)

    def test_large_integers(self):
        values = [-(10 ** 100), 0, 10 ** 100]
        for target in [*values, 10 ** 99]:
            with self.subTest(target=target):
                self.assert_contract(values, target)

    def test_exhaustive_small_sorted_inputs(self):
        checked = 0
        for size in range(6):
            for items in itertools.combinations_with_replacement(range(-2, 3), size):
                for target in range(-3, 4):
                    with self.subTest(values=items, target=target):
                        self.assert_contract(list(items), target)
                    checked += 1
        self.assertEqual(checked, 1764)
        type(self).exhaustive_cases = checked

    def test_intentional_bug_is_reproduced(self):
        # これは誤りの再現を確認するテスト。buggyの正しさを示さない。
        for values, target, expected in [([1], 1, 0), ([7], 7, 0), ([1, 3], 3, 1),
                                         ([1, 3, 5], 5, 2)]:
            with self.subTest(values=values, target=target):
                self.assertIsNone(buggy(values, target))
                self.assertEqual(corrected(values, target), expected)

    def test_original_finite_verification(self):
        self.assertEqual(verify(), 272)

    def test_documented_cli_output(self):
        folder = Path(__file__).resolve().parent
        expected = {
            "verify.py": "反例: values=[7], target=7\nbuggy: None corrected: 0\n修正版の有限入力検証: 272 cases passed\n",
            "binary_search_corrected.py": "公開修正版: 3\n",
        }
        for name, output in expected.items():
            with self.subTest(script=name):
                result = subprocess.run([sys.executable, str(folder / name)], cwd=folder,
                                        capture_output=True, text=True, encoding="utf-8",
                                        env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, output)
                self.assertEqual(result.stderr, "")


def main():
    # 成功時の出力を決定的にする。失敗時は全診断を表示し非ゼロ終了する。
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SearchContractTests)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    if not result.wasSuccessful() or result.testsRun != 8:
        print(stream.getvalue(), file=sys.stderr, end="")
        return 1
    print(f"{result.testsRun} tests passed; exhaustive contract: {SearchContractTests.exhaustive_cases} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
