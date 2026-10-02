"""最小反例を記録し、小さな有限入力で修正を検証する。"""

from binary_search_buggy import binary_search as buggy
from binary_search_corrected import binary_search as corrected


def verify() -> int:
    checked = 0
    for size in range(16):
        values = list(range(0, 2 * size, 2))
        for target in range(-1, 2 * size + 1):
            result = corrected(values, target)
            if target in values:
                assert result is not None and values[result] == target
            else:
                assert result is None
            checked += 1
    return checked


if __name__ == "__main__":
    print("反例: values=[7], target=7")
    print("buggy:", buggy([7], 7), "corrected:", corrected([7], 7))
    print(f"修正版の有限入力検証: {verify()} cases passed")
