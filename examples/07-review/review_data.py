"""講評用の架空データ。実在の提出・路線・人物は含まない。"""

GRAPH = {"A": ["B", "C"], "B": ["A", "E"], "C": ["A", "D"],
         "D": ["F", "C"], "E": ["B", "F"], "F": ["E", "D"], "X": []}


def validate_input(graph: dict[str, list[str]], start: str, goal: str) -> None:
    if start not in graph or goal not in graph:
        raise ValueError("未知の駅IDです")
    adjacency_sets = {vertex: set(neighbors) for vertex, neighbors in graph.items()}
    for vertex, neighbors in graph.items():
        for neighbor in neighbors:
            if neighbor not in graph or vertex not in adjacency_sets[neighbor]:
                raise ValueError("グラフは定義済み頂点間の無向辺にしてください")


def run_cli(find_route, *, flawed: bool = False) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="架空提出の講評用デモ")
    parser.add_argument("start", nargs="?", default="A")
    parser.add_argument("goal", nargs="?", default="D")
    args = parser.parse_args()
    try:
        path = find_route(GRAPH, args.start, args.goal)
    except ValueError as error:
        parser.exit(2, f"入力エラー: {error}\n")
    if path is None:
        parser.exit(2, "経路なし\n")
    if flawed:
        print("教材用の誤り: 以下を『最短』と呼ぶのは不適切")
        print("架空提出の主張: 最短経路")
    print(" -> ".join(path))
    print(f"移動数: {len(path) - 1}")
    return 0
