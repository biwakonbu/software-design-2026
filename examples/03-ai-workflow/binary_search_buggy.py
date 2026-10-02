"""教材用の誤りを含む架空AI出力。実用・提出用の正解ではない。"""


def binary_search(values: list[int], target: int) -> int | None:
    """誤り: 最後に残った1要素を検査しない。常に終了する安全な反例。"""
    low, high = 0, len(values) - 1
    while low < high:  # BUG: low == highの候補も検査する必要がある。
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return None


if __name__ == "__main__":
    print("教材用buggy: binary_search([7], 7) =", binary_search([7], 7))
