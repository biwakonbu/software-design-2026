"""有限の整数入力で標準機能・独立した列挙と照合する。正しさの証明ではない。"""
from itertools import combinations, product
import unittest
from containers import stack_order, queue_order
from sorting_search import insertion_sort, merge_sort, linear_search, binary_search, all_pairs_with_sum
from trees import Node, bfs, dfs, demo_tree

class Examples(unittest.TestCase):
    def test_integer_lists(self):
        cases = 0
        for length in range(6):
            for row in product((-1, 0, 1), repeat=length):
                values = list(row)
                original = values.copy()
                ordered = sorted(values)
                self.assertEqual(stack_order(values), values[::-1])
                self.assertEqual(queue_order(values), values)
                self.assertEqual(insertion_sort(values), ordered)
                self.assertEqual(merge_sort(values), ordered)
                for target in range(-2, 3):
                    expected = next((i for i, v in enumerate(values) if v == target), None)
                    self.assertEqual(linear_search(values, target), expected)
                    result = binary_search(ordered, target)
                    if target in ordered:
                        self.assertIsNotNone(result)
                        self.assertEqual(ordered[result], target)
                    else:
                        self.assertIsNone(result)
                    expected_pairs = [(i, j) for i, j in combinations(range(length), 2)
                                      if values[i] + values[j] == target]
                    self.assertEqual(all_pairs_with_sum(values, target), expected_pairs)
                self.assertEqual(ordered, sorted(original))
                self.assertEqual(values, original)
                cases += 1
        self.assertEqual(cases, 364)

    def test_tree_boundaries(self):
        self.assertEqual(dfs(None), [])
        self.assertEqual(bfs(None), [])
        self.assertEqual(dfs(Node('A')), ['A'])
        self.assertEqual(bfs(Node('A')), ['A'])
        self.assertEqual(dfs(demo_tree()), ['A', 'B', 'D', 'E', 'C', 'F'])
        self.assertEqual(bfs(demo_tree()), ['A', 'B', 'C', 'D', 'E', 'F'])
        root = Node('A', [Node('B'), Node('C')])
        first = root.children.copy()
        dfs(root); bfs(root)
        self.assertEqual(root.children, first)

if __name__ == '__main__':
    unittest.main()
