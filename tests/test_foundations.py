"""公開サンプルの仕様・境界・反例・CLIを標準unittestで検証する。"""

import importlib.util
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(folder, filename):
    path = ROOT / "examples" / folder / f"{filename}.py"
    name = f"foundation_{filename}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


orders = load("02-basics", "order_summary")
buggy = load("03-ai-workflow", "binary_search_buggy")
corrected = load("03-ai-workflow", "binary_search_corrected")
verification = load("03-ai-workflow", "verify")
memory = load("04-algorithms", "memory_complexity")
containers = load("04-algorithms", "containers")
search = load("04-algorithms", "sorting_search")
trees = load("04-algorithms", "trees")
graphs = load("05-graphs", "graphs")
route_data = load("06-route-project", "route_data")
starter = load("06-route-project", "route_starter")
reference = load("06-route-project", "route_reference")
review_data = load("07-review", "review_data")
flawed = load("07-review", "flawed_route")
improved = load("07-review", "improved_route")


def assert_path(test, graph, path, start, goal):
    test.assertEqual(path[0], start)
    test.assertEqual(path[-1], goal)
    test.assertEqual(len(path), len(set(path)))
    for left, right in itertools.pairwise(path):
        test.assertIn(right, graph[left])


def brute_distance(graph, start, goal):
    """BFSと独立した小入力用オラクル: 単純経路候補を辺数順に全列挙。"""
    if start == goal:
        return 0
    others = [vertex for vertex in graph if vertex not in (start, goal)]
    for count in range(len(others) + 1):
        for middle in itertools.permutations(others, count):
            path = (start, *middle, goal)
            if all(right in graph[left] for left, right in itertools.pairwise(path)):
                return len(path) - 1
    return None


class OrderTests(unittest.TestCase):
    def test_demo_aggregates_repeated_items(self):
        self.assertEqual(orders.summarize(orders.DEMO_ORDERS),
                         {"quantities": {"ノート": 2, "ペン": 3}, "total_yen": 760})
        self.assertEqual(orders.summarize([{"name": "A", "price": 2, "quantity": 1},
                                           {"name": "A", "price": 3, "quantity": 2}]),
                         {"quantities": {"A": 3}, "total_yen": 8})

    def test_empty_orders(self):
        self.assertEqual(orders.summarize([]), {"quantities": {}, "total_yen": 0})
        self.assertEqual(orders.summary([]), 0)
        self.assertEqual(orders.summary(orders.DEMO_ORDERS), 760)

    def test_zero_price_is_valid(self):
        self.assertEqual(orders.summarize([{"name": "試供品", "price": 0, "quantity": 2}])["total_yen"], 0)
        self.assertEqual(orders.summary([{ "name": "A", "price": 9, "quantity": 0}]), 0)

    def test_does_not_modify_input(self):
        data = [{"name": "A", "price": 3, "quantity": 2}]
        before = json.dumps(data)
        orders.summarize(data)
        self.assertEqual(json.dumps(data), before)

    def test_rejects_invalid_container(self):
        for data in ({}, [None], ["A"]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                orders.summarize(data)

    def test_rejects_missing_or_non_string_name(self):
        for item in (None, True, 7):
            with self.subTest(item=item), self.assertRaises(ValueError):
                orders.summarize([{"name": item, "price": 1, "quantity": 1}])
        self.assertEqual(orders.summary([{"name": "", "price": 1, "quantity": 1}]), 1)

    def test_rejects_invalid_price_and_quantity(self):
        for field, bad_values in (("price", (-1, 1.5, True, "2", None)),
                                  ("quantity", (-1, 1.5, True, "2", None))):
            for value in bad_values:
                data = {"name": "A", "price": 1, "quantity": 1, field: value}
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    orders.summarize([data])


class AIWorkflowTests(unittest.TestCase):
    def test_smallest_counterexample(self):
        self.assertIsNone(buggy.binary_search([7], 7))
        self.assertEqual(corrected.binary_search([7], 7), 0)

    def test_right_endpoint_counterexample(self):
        self.assertIsNone(buggy.binary_search([1, 3], 3))
        self.assertEqual(corrected.binary_search([1, 3], 3), 1)

    def test_empty_missing_and_duplicates(self):
        self.assertIsNone(corrected.binary_search([], 1))
        self.assertIsNone(corrected.binary_search([1, 3], 2))
        index = corrected.binary_search([2, 2, 2], 2)
        self.assertIn(index, (0, 1, 2))

    def test_finite_verification(self):
        self.assertEqual(verification.verify(), 272)


class AlgorithmTests(unittest.TestCase):
    def test_growth_counts(self):
        counts = memory.comparison_counts(16)
        self.assertEqual(list(counts.values()), [1, 5, 16, 64, 256])
        self.assertEqual(memory.comparison_counts(0)["one scan O(n)"], 0)

    def test_counts_reject_invalid_size(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                memory.comparison_counts(value)

    def test_memory_is_shallow(self):
        small = memory.shallow_sizes(["x"])
        large = memory.shallow_sizes(["x" * 10000])
        self.assertEqual(small["list_shallow_bytes"], large["list_shallow_bytes"])
        self.assertLess(small["first_element_shallow_bytes"], large["first_element_shallow_bytes"])

    def test_stack_and_queue_order(self):
        self.assertEqual(containers.stack_order([1, 2, 3]), [3, 2, 1])
        self.assertEqual(containers.queue_order([1, 2, 3]), [1, 2, 3])
        self.assertEqual(containers.stack_order([]), [])
        self.assertEqual(containers.queue_order([]), [])

    def test_sorts_permutations_and_duplicates(self):
        for size in range(6):
            for values in itertools.permutations(range(size)):
                for sort in (search.insertion_sort, search.merge_sort):
                    self.assertEqual(sort(list(values)), sorted(values))
        for sort in (search.insertion_sort, search.merge_sort):
            self.assertEqual(sort([3, -1, 3, 0]), [-1, 0, 3, 3])

    def test_sorts_preserve_input(self):
        values = [3, 1, 2]
        for sort in (search.insertion_sort, search.merge_sort):
            result = sort(values)
            self.assertEqual(values, [3, 1, 2])
            self.assertIsNot(result, values)

    def test_linear_search_returns_first(self):
        self.assertEqual(search.linear_search([4, 2, 4], 4), 0)
        self.assertIsNone(search.linear_search([], 1))
        self.assertIsNone(search.linear_search([4], 1))

    def test_all_search_preserves_distinct_indices(self):
        self.assertEqual(search.all_pairs_with_sum([2, 2, 2], 4), [(0, 1), (0, 2), (1, 2)])
        self.assertEqual(search.all_pairs_with_sum([1, 2, 3, 4], 5), [(0, 3), (1, 2)])
        self.assertEqual(search.all_pairs_with_sum([2], 4), [])

    def test_binary_search_boundaries(self):
        for target in range(-2, 12):
            values = [0, 2, 4, 6, 8]
            index = search.binary_search(values, target)
            if target in values:
                self.assertEqual(values[index], target)
            else:
                self.assertIsNone(index)
        self.assertIsNone(search.binary_search([], 0))

    def test_tree_traversal_orders(self):
        self.assertEqual(trees.dfs(trees.demo_tree()), list("ABDECF"))
        self.assertEqual(trees.bfs(trees.demo_tree()), list("ABCDEF"))

    def test_empty_and_single_tree(self):
        for traversal in (trees.dfs, trees.bfs):
            self.assertEqual(traversal(None), [])
            self.assertEqual(traversal(trees.Node("A")), ["A"])
        self.assertIsNot(trees.Node("A").children, trees.Node("B").children)


class GraphTests(unittest.TestCase):
    def test_bfs_and_dfs_cycle_orders(self):
        self.assertEqual(graphs.bfs(graphs.DEMO_GRAPH, "A"), list("ABCD"))
        self.assertEqual(graphs.dfs(graphs.DEMO_GRAPH, "A"), list("ABDC"))

    def test_shortest_path_and_tie_order(self):
        self.assertEqual(graphs.shortest_path(graphs.DEMO_GRAPH, "A", "D"), list("ABD"))

    def test_self_and_unreachable(self):
        self.assertEqual(graphs.shortest_path(graphs.DEMO_GRAPH, "X", "X"), ["X"])
        self.assertIsNone(graphs.shortest_path(graphs.DEMO_GRAPH, "A", "X"))

    def test_connected_components(self):
        self.assertEqual(graphs.connected_components(graphs.DEMO_GRAPH), [list("ABCD"), ["X"]])
        self.assertEqual(graphs.connected_components({}), [])

    def test_unknown_vertices(self):
        for function in (graphs.bfs, graphs.dfs):
            with self.assertRaises(ValueError):
                function(graphs.DEMO_GRAPH, "?")
        with self.assertRaises(ValueError):
            graphs.shortest_path(graphs.DEMO_GRAPH, "A", "?")

    def test_rejects_dangling_edge(self):
        with self.assertRaises(ValueError):
            graphs.shortest_path({"A": ["B"]}, "A", "A")

    def test_directed_edges_follow_direction(self):
        graph = {"A": ["B"], "B": []}
        self.assertEqual(graphs.shortest_path(graph, "A", "B"), ["A", "B"])
        self.assertIsNone(graphs.shortest_path(graph, "B", "A"))
        with self.assertRaises(ValueError):
            graphs.connected_components(graph)

    def test_self_loop_and_duplicate_edges(self):
        graph = {"A": ["A", "B", "B"], "B": ["A"]}
        self.assertEqual(graphs.bfs(graph, "A"), ["A", "B"])
        self.assertEqual(graphs.dfs(graph, "A"), ["A", "B"])

    def test_all_four_vertex_graphs_against_exhaustive_oracle(self):
        vertices = list("ABCD")
        edges = list(itertools.combinations(vertices, 2))
        for mask in range(1 << len(edges)):
            graph = {vertex: [] for vertex in vertices}
            for bit, (left, right) in enumerate(edges):
                if mask & (1 << bit):
                    graph[left].append(right)
                    graph[right].append(left)
            for start, goal in itertools.product(vertices, repeat=2):
                expected = brute_distance(graph, start, goal)
                for find in (graphs.shortest_path, reference.find_route, improved.find_route):
                    path = find(graph, start, goal)
                    if expected is None:
                        self.assertIsNone(path)
                    else:
                        assert_path(self, graph, path, start, goal)
                        self.assertEqual(len(path) - 1, expected)


class RouteTests(unittest.TestCase):
    def test_starter_existing_behavior(self):
        self.assertEqual(starter.find_route(route_data.GRAPH, "A", "A"), ["A"])
        self.assertEqual(starter.find_route(route_data.GRAPH, "A", "B"), ["A", "B"])

    def test_starter_unfinished_behavior_is_explicit(self):
        self.assertIsNone(starter.find_route(route_data.GRAPH, "A", "D"))
        self.assertIsNone(starter.find_route(route_data.GRAPH, "A", "X"))

    def test_reference_route(self):
        self.assertEqual(reference.find_route(route_data.GRAPH, "A", "D"), list("ABD"))
        self.assertEqual(reference.find_route(route_data.GRAPH, "X", "X"), ["X"])
        self.assertIsNone(reference.find_route(route_data.GRAPH, "A", "X"))

    def test_reference_every_pair_has_valid_minimal_route(self):
        for start, goal in itertools.product(route_data.GRAPH, repeat=2):
            path = reference.find_route(route_data.GRAPH, start, goal)
            expected = brute_distance(route_data.GRAPH, start, goal)
            if path is None:
                self.assertIsNone(expected)
            else:
                assert_path(self, route_data.GRAPH, path, start, goal)
                self.assertEqual(len(path) - 1, expected)

    def test_route_validation(self):
        for find in (starter.find_route, reference.find_route):
            with self.assertRaises(ValueError):
                find(route_data.GRAPH, "?", "A")
            with self.assertRaises(ValueError):
                find({"A": ["B"], "B": []}, "A", "B")


class ReviewTests(unittest.TestCase):
    def test_flawed_counterexample_is_valid_but_long(self):
        path = flawed.find_route(review_data.GRAPH, "A", "D")
        self.assertEqual(path, list("ABEFD"))
        assert_path(self, review_data.GRAPH, path, "A", "D")
        self.assertGreater(len(path) - 1, brute_distance(review_data.GRAPH, "A", "D"))

    def test_improved_counterexample(self):
        self.assertEqual(improved.find_route(review_data.GRAPH, "A", "D"), list("ACD"))

    def test_review_boundaries_and_validation(self):
        for find in (flawed.find_route, improved.find_route):
            self.assertEqual(find(review_data.GRAPH, "X", "X"), ["X"])
            self.assertIsNone(find(review_data.GRAPH, "A", "X"))
            with self.assertRaises(ValueError):
                find(review_data.GRAPH, "A", "?")


class CLITests(unittest.TestCase):
    def run_cli(self, relative, *args):
        return subprocess.run([sys.executable, str(ROOT / relative), *args],
                              capture_output=True, text=True, timeout=10, cwd=ROOT)

    def test_demo_scripts(self):
        files = ["02-basics/order_summary.py", "03-ai-workflow/binary_search_buggy.py",
                 "03-ai-workflow/binary_search_corrected.py", "03-ai-workflow/verify.py",
                 "04-algorithms/memory_complexity.py", "04-algorithms/containers.py",
                 "04-algorithms/sorting_search.py", "04-algorithms/trees.py", "05-graphs/graphs.py"]
        for filename in files:
            with self.subTest(filename=filename):
                result = self.run_cli(f"examples/{filename}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip())

    def test_order_input_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "orders.json"
            source.write_text('[{"name":"A","price":5,"quantity":2}]', encoding="utf-8")
            result = self.run_cli("examples/02-basics/order_summary.py", str(source))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["total_yen"], 10)
            source.write_text("invalid json", encoding="utf-8")
            self.assertEqual(self.run_cli("examples/02-basics/order_summary.py", str(source)).returncode, 2)

    def test_reference_cli_default_and_failure(self):
        script = "examples/06-route-project/route_reference.py"
        result = self.run_cli(script)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "A -> B -> D\n移動数: 2\n")
        for goal in ("X", "?"):
            result = self.run_cli(script, "A", goal)
            self.assertEqual(result.returncode, 2)
            self.assertTrue(result.stderr.strip())

    def test_starter_cli_baseline_and_todo(self):
        script = "examples/06-route-project/route_starter.py"
        self.assertEqual(self.run_cli(script, "A", "B").stdout, "A -> B\n移動数: 1\n")
        self.assertEqual(self.run_cli(script, "A", "A").returncode, 0)
        result = self.run_cli(script)
        self.assertEqual(result.returncode, 2)
        self.assertIn("多段経路未実装", result.stderr)

    def test_review_cli_counterexample(self):
        result = self.run_cli("examples/07-review/flawed_route.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("教材用の誤り", result.stdout)
        self.assertIn("A -> B -> E -> F -> D", result.stdout)
        result = self.run_cli("examples/07-review/improved_route.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "A -> C -> D\n移動数: 2\n")
        self.assertEqual(self.run_cli("examples/07-review/improved_route.py", "A", "X").returncode, 2)


if __name__ == "__main__":
    unittest.main()
