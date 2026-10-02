"""全て架空の駅。辺は双方向、移動1回が同じコストの教材モデル。"""

STATIONS = {"A": "青空駅", "B": "木の葉駅", "C": "雲の駅", "D": "光駅",
            "E": "丘の駅", "X": "離れ島駅"}
GRAPH = {"A": ["B", "C"], "B": ["A", "D"], "C": ["A", "E"],
         "D": ["B", "E"], "E": ["C", "D"], "X": []}


def validate_input(graph: dict[str, list[str]], start: str, goal: str) -> None:
    if start not in graph or goal not in graph:
        raise ValueError("未知の駅IDです")
    adjacency_sets = {vertex: set(neighbors) for vertex, neighbors in graph.items()}
    for vertex, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor not in graph or vertex not in adjacency_sets[neighbor]:
                raise ValueError("グラフは定義済み頂点間の無向辺にしてください")


def run_cli(find_route, *, starter: bool = False) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="架空駅の経路探索（無向・重みなし）")
    parser.add_argument("start", nargs="?", default="A")
    parser.add_argument("goal", nargs="?", default="D")
    args = parser.parse_args()
    try:
        path = find_route(GRAPH, args.start, args.goal)
    except ValueError as error:
        parser.exit(2, f"入力エラー: {error}\n")
    if path is None:
        detail = "（starterは多段経路未実装）" if starter else ""
        parser.exit(2, f"経路なし{detail}: {args.start} → {args.goal}\n")
    print(" -> ".join(path))
    print(f"移動数: {len(path) - 1}")
    return 0
