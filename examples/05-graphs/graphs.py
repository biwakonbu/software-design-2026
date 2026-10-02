"""隣接リストのグラフ。BFSの最短性は辺数（重みなし）に対して成り立つ。"""

from collections import deque

DEMO_GRAPH = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"],
              "D": ["B", "C"], "X": []}


def validate_graph(graph: dict[str, list[str]], *, undirected: bool = False) -> None:
    adjacency_sets = {vertex: set(neighbors) for vertex, neighbors in graph.items()}
    for vertex, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor not in graph:
                raise ValueError(f"未定義の頂点: {neighbor}")
            if undirected and vertex not in adjacency_sets[neighbor]:
                raise ValueError(f"無向辺の逆向きがありません: {vertex}-{neighbor}")


def bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    validate_graph(graph)
    if start not in graph:
        raise ValueError(f"未知の頂点: {start}")
    return _bfs(graph, start)


def _bfs(graph: dict[str, list[str]], start: str) -> list[str]:
    queue = deque([start])
    visited = {start}
    result = []
    while queue:
        vertex = queue.popleft()
        result.append(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)  # enqueue時に印を付け重複を防ぐ。
                queue.append(neighbor)
    return result


def dfs(graph: dict[str, list[str]], start: str) -> list[str]:
    validate_graph(graph)
    if start not in graph:
        raise ValueError(f"未知の頂点: {start}")
    stack = [start]
    visited = set()
    result = []
    while stack:
        vertex = stack.pop()
        if vertex in visited:
            continue
        visited.add(vertex)
        result.append(vertex)
        stack.extend(reversed(graph[vertex]))
    return result


def shortest_path(graph: dict[str, list[str]], start: str, goal: str) -> list[str] | None:
    validate_graph(graph)
    if start not in graph or goal not in graph:
        raise ValueError("始点と終点は定義済みの頂点にしてください")
    queue = deque([start])
    previous: dict[str, str | None] = {start: None}
    while queue:
        vertex = queue.popleft()
        if vertex == goal:
            path = []
            cursor: str | None = goal
            while cursor is not None:
                path.append(cursor)
                cursor = previous[cursor]
            return path[::-1]
        for neighbor in graph[vertex]:
            if neighbor not in previous:
                previous[neighbor] = vertex
                queue.append(neighbor)
    return None


def connected_components(graph: dict[str, list[str]]) -> list[list[str]]:
    """無向グラフ専用。頂点の挿入順、隣接順で結果を決定する。"""
    validate_graph(graph, undirected=True)
    unseen = set(graph)
    components = []
    for vertex in graph:
        if vertex in unseen:
            component = _bfs(graph, vertex)
            components.append(component)
            unseen.difference_update(component)
    return components


if __name__ == "__main__":
    print("BFS:", bfs(DEMO_GRAPH, "A"))
    print("DFS:", dfs(DEMO_GRAPH, "A"))
    print("A→D 最短経路:", shortest_path(DEMO_GRAPH, "A", "D"))
    print("接続成分:", connected_components(DEMO_GRAPH))
    print("有向グラフは辺の向きに従う。重み付き最小費用にはこのBFSを使わない。")
