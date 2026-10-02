"""listのスタック（LIFO）、dequeのキュー（FIFO）、両端操作。"""

from collections import deque


def stack_order(values: list) -> list:
    stack = []
    for value in values:
        stack.append(value)
    result = []
    while stack:
        result.append(stack.pop())
    return result


def queue_order(values: list) -> list:
    queue = deque(values)
    result = []
    while queue:
        result.append(queue.popleft())
    return result


if __name__ == "__main__":
    print("stack LIFO:", stack_order(["A", "B", "C"]))
    print("queue FIFO:", queue_order(["A", "B", "C"]))
    both_ends = deque(["B"])
    both_ends.appendleft("A")
    both_ends.append("C")
    print("deque 両端:", both_ends.popleft(), both_ends.pop())
    print("list.pop(0)は残り要素を移動するためO(n)。deque.popleft()はO(1)。")
