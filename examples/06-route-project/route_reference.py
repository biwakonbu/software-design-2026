"""公開reference: 学習・照合用の完成例。提出物とは区別する。"""

from collections import deque
from route_data import run_cli, validate_input


def find_route(graph: dict[str, list[str]], start: str, goal: str) -> list[str] | None:
    validate_input(graph, start, goal)
    queue = deque([start])
    # 辞書のキーを訪問済み集合として兼用する。
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


if __name__ == "__main__":
    raise SystemExit(run_cli(find_route))
