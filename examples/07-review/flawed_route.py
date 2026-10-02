"""架空の誤った提出例: DFSで見つけた最初の経路を『最短』と解釈する。"""

from review_data import run_cli, validate_input


def find_route(graph: dict[str, list[str]], start: str, goal: str) -> list[str] | None:
    validate_input(graph, start, goal)
    visited = set()

    def visit(vertex: str, path: list[str]) -> list[str] | None:
        if vertex == goal:
            return path
        visited.add(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                result = visit(neighbor, path + [neighbor])
                if result is not None:
                    return result
        return None

    return visit(start, [start])


if __name__ == "__main__":
    raise SystemExit(run_cli(find_route, flawed=True))
