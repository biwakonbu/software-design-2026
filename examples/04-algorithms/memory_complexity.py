"""メモリの浅い計測と、実測時間ではなく操作回数によるO記号比較。"""

import math
import sys


def comparison_counts(n: int) -> dict[str, int]:
    if type(n) is not int or n < 0:
        raise ValueError("nは0以上の整数です")
    return {
        "constant O(1)": 1,
        "halving O(log n)": n.bit_length(),
        "one scan O(n)": n,
        "merge-sort model O(n log n)": n * math.ceil(math.log2(n)) if n else 0,
        "all ordered pairs O(n²)": n * n,
    }


def shallow_sizes(values: list) -> dict[str, int]:
    """bytes。参照先や共有オブジェクトを含む総メモリではない。"""
    return {"list_shallow_bytes": sys.getsizeof(values),
            "first_element_shallow_bytes": sys.getsizeof(values[0]) if values else 0}


if __name__ == "__main__":
    print("浅いサイズ（Python実装・環境に依存）:", shallow_sizes(["x" * 1000] * 10))
    print("getsizeof(list)は参照先の文字列の総量を含みません。")
    for n in (8, 16, 32):
        print(n, comparison_counts(n))
