"""公開改善例: BFSで辺数最小を保証し、直前の駅から経路を復元する。"""

from collections import deque
from review_data import run_cli, validate_input


def find_route(graph: dict[str, list[str]], start: str, goal: str) -> list[str] | None:
    validate_input(graph, start, goal)
    previous: dict[str, str | None] = {start: None}
    queue = deque([start])
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


if __name__ == "__main__":
    raise SystemExit(run_cli(find_route))
