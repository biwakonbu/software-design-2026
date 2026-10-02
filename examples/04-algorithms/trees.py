"""木構造のDFS（前順）とBFS（レベル順）。子の順を保持する。"""

from collections import deque
from dataclasses import dataclass, field


@dataclass
class Node:
    value: str
    children: list["Node"] = field(default_factory=list)


def dfs(root: Node | None) -> list[str]:
    result = []

    def visit(node: Node) -> None:
        result.append(node.value)
        for child in node.children:
            visit(child)

    if root is not None:
        visit(root)
    return result


def bfs(root: Node | None) -> list[str]:
    queue = deque([root]) if root is not None else deque()
    result = []
    while queue:
        node = queue.popleft()
        result.append(node.value)
        queue.extend(node.children)
    return result


def demo_tree() -> Node:
    return Node("A", [Node("B", [Node("D"), Node("E")]), Node("C", [Node("F")])])


if __name__ == "__main__":
    print("DFS:", dfs(demo_tree()))
    print("BFS:", bfs(demo_tree()))
    print("木は閉路なし・各子は親1つ。共有/閉路を許すグラフにはvisitedが必要。")
