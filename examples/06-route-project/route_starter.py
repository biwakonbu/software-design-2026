"""提出練習用starter。完成版ではなく、同駅・隣駅だけ動作する。"""

from route_data import run_cli, validate_input


def find_route(graph: dict[str, list[str]], start: str, goal: str) -> list[str] | None:
    validate_input(graph, start, goal)
    if start == goal:
        return [start]
    if goal in graph[start]:
        return [start, goal]
    # TODO: deque、訪問済み集合/辞書、直前の駅でBFSを実装する。
    # TODO: 到達時に逆順に復元し、到達不能時のみNoneを返す。
    return None


if __name__ == "__main__":
    raise SystemExit(run_cli(find_route, starter=True))
