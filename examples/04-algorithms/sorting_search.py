"""挿入/マージソートと線形/全探索/二分探索の公開実装。"""


def insertion_sort(values: list) -> list:
    result = list(values)
    for index in range(1, len(result)):
        current = result[index]
        position = index
        while position > 0 and result[position - 1] > current:
            result[position] = result[position - 1]
            position -= 1
        result[position] = current
    return result


def merge_sort(values: list) -> list:
    if len(values) <= 1:
        return list(values)
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    return merged + left[i:] + right[j:]


def linear_search(values: list, target) -> int | None:
    for index, value in enumerate(values):
        if value == target:
            return index
    return None


def all_pairs_with_sum(values: list[int], target: int) -> list[tuple[int, int]]:
    """異なる添字i < jの全候補を調べるO(n²)の全探索。値の重複も区別。"""
    return [(i, j) for i in range(len(values)) for j in range(i + 1, len(values))
            if values[i] + values[j] == target]


def binary_search(values: list, target) -> int | None:
    """昇順整列済みが前提。O(log n)。検査のための並べ替えは含まない。"""
    low, high = 0, len(values) - 1
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
    values = [7, 2, 4, 2, 9]
    print("insertion O(n²):", insertion_sort(values))
    print("merge O(n log n):", merge_sort(values))
    print("linear O(n):", linear_search(values, 4))
    print("all pairs O(n²):", all_pairs_with_sum(values, 11))
    print("binary O(log n):", binary_search(merge_sort(values), 9))
