"""BFSとは別のFloyd–Warshall法で最短辺数を照合する有限検査。"""
from copy import deepcopy
from itertools import combinations
import unittest
from graphs import bfs, dfs, shortest_path, connected_components, validate_graph, DEMO_GRAPH

class Graphs(unittest.TestCase):
    def test_all_four_vertex_undirected_graphs(self):
        vertices = list('ABCD')
        edges = list(combinations(vertices, 2))
        cases = 0
        for mask in range(64):
            graph = {v: [] for v in vertices}
            distance = {(a, b): 0 if a == b else 99 for a in vertices for b in vertices}
            for bit, (a, b) in enumerate(edges):
                if mask & (1 << bit):
                    graph[a].append(b); graph[b].append(a)
                    distance[a, b] = distance[b, a] = 1
            for k in vertices:
                for a in vertices:
                    for b in vertices:
                        distance[a, b] = min(distance[a, b], distance[a, k] + distance[k, b])
            original = deepcopy(graph)
            for start in vertices:
                reached = {v for v in vertices if distance[start, v] < 99}
                for visit in (bfs, dfs):
                    result = visit(graph, start)
                    self.assertEqual(set(result), reached)
                    self.assertEqual(len(result), len(reached))
                for goal in vertices:
                    path = shortest_path(graph, start, goal)
                    if distance[start, goal] == 99:
                        self.assertIsNone(path)
                    else:
                        self.assertEqual((path[0], path[-1]), (start, goal))
                        self.assertEqual(len(path) - 1, distance[start, goal])
                        self.assertEqual(len(path), len(set(path)))
                        self.assertTrue(all(b in graph[a] for a, b in zip(path, path[1:])))
                    cases += 1
            groups = connected_components(graph)
            flat = [v for group in groups for v in group]
            self.assertEqual(sorted(flat), vertices)
            self.assertEqual(len(flat), len(set(flat)))
            for group in groups:
                self.assertEqual(set(group), {v for v in vertices if distance[group[0], v] < 99})
            self.assertEqual(graph, original)
        self.assertEqual(cases, 1024)

    def test_demo_order(self):
        self.assertEqual(bfs(DEMO_GRAPH, 'A'), list('ABCD'))
        self.assertEqual(dfs(DEMO_GRAPH, 'A'), list('ABDC'))
        self.assertEqual(shortest_path(DEMO_GRAPH, 'A', 'D'), list('ABD'))
        self.assertIsNone(shortest_path(DEMO_GRAPH, 'A', 'X'))
        self.assertEqual(connected_components(DEMO_GRAPH), [list('ABCD'), ['X']])

    def test_directed_self_loop_and_duplicate_edges(self):
        graph = {'A': ['A', 'B', 'B'], 'B': ['C'], 'C': []}
        self.assertEqual(bfs(graph, 'A'), list('ABC'))
        self.assertEqual(shortest_path(graph, 'A', 'C'), list('ABC'))
        self.assertIsNone(shortest_path(graph, 'C', 'A'))

    def test_invalid_inputs(self):
        for visit in (bfs, dfs):
            with self.assertRaises(ValueError): visit({}, 'A')
            with self.assertRaises(ValueError): visit({'A': ['Z']}, 'A')
        with self.assertRaises(ValueError): shortest_path({'A': []}, 'A', 'Z')
        with self.assertRaises(ValueError): shortest_path({'A': ['Z']}, 'A', 'A')
        with self.assertRaises(ValueError): validate_graph({'A': ['B'], 'B': []}, undirected=True)
        with self.assertRaises(ValueError): connected_components({'A': ['B'], 'B': []})
        self.assertEqual(connected_components({}), [])

if __name__ == '__main__':
    unittest.main()
