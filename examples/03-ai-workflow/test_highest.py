import unittest
import itertools
import sys

from highest import highest, highest_draft


class HighestTest(unittest.TestCase):
    # 期待値はすべて仕様と手計算から決めた

    def test_typical(self):
        self.assertEqual(highest([3, 7, 5]), 7)

    def test_all_negative(self):
        self.assertEqual(highest([-3, -1, -5]), -1)

    def test_single(self):
        self.assertEqual(highest([5]), 5)

    def test_first_is_highest(self):
        self.assertEqual(highest([9, 2, 4]), 9)

    def test_duplicate_highest(self):
        self.assertEqual(highest([2, 9, 9]), 9)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            highest([])

    def test_matches_builtin_max(self):
        for temps in ([0, -2], [-7], [4, 4, 4], [-1, 3, -2, 3]):
            with self.subTest(temps=temps):
                self.assertEqual(highest(temps), max(temps))

    def test_draft_differs_from_spec(self):
        # 誤りの再現: 旧版は反例で仕様の期待値 -1 を返さない
        self.assertNotEqual(highest_draft([-3, -1, -5]), -1)


class HighestExtendedTest(unittest.TestCase):
    def test_input_is_preserved(self):
        temps = [-3, -1, -5, -1]
        before = temps[:]
        self.assertEqual(highest(temps), -1)
        self.assertEqual(temps, before)
        self.assertEqual(highest([10**100, -(10**101)]), 10**100)

    def test_exhaustive_integer_lists(self):
        count = 0
        for length in range(6):
            for values in itertools.product(range(-2, 3), repeat=length):
                temps = list(values)
                before = temps[:]
                if temps:
                    self.assertEqual(highest(temps), max(temps))
                else:
                    with self.assertRaises(ValueError):
                        highest(temps)
                self.assertEqual(temps, before)
                count += 1
        self.assertEqual(count, 3906)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TestResult()
    suite.run(result)
    if result.wasSuccessful():
        print('10 tests passed; highest: 3906 integer lists')
    else:
        for _, detail in result.errors + result.failures:
            print(detail, file=sys.stderr)
        sys.exit(1)
