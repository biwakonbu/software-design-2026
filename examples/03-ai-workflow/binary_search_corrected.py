"""公開修正版。入力は昇順に整列済みの整数列。"""


def binary_search(values: list[int], target: int) -> int | None:
    """一致する添字を1つ返す。重複時の最初の添字は保証しない。"""
    low, high = 0, len(values) - 1
    # 不変条件: 存在するなら探索候補は閉区間[low, high]内にある。
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return None


if __name__ == "__main__":
    print("公開修正版:", binary_search([1, 3, 5, 7], 7))
