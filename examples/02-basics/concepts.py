"""短いPython概念デモ。CASEを選び、実行前の予測と出力を比べる。"""

import argparse
from pathlib import Path
import traceback


def rebinding() -> None:
    quantity = 2
    earlier = quantity
    print(f"before: quantity={quantity}, earlier={earlier}")
    quantity = quantity + 1
    print(f"after: quantity={quantity}, earlier={earlier}")
    text = "pen"
    upper_text = text.upper()
    print(f"text={text!r}, upper_text={upper_text!r}")


def types() -> None:
    for value in (200, 0.1, "200", True):
        print(f"{type(value).__name__}: {value!r}")
    print(f"200 + 120 = {200 + 120}")
    print(f"'200' + '120' = {'200' + '120'!r}")
    print(f"7 / 2 = {7 / 2}")
    print(f"7 // 2 = {7 // 2}")
    print(f"7 % 2 = {7 % 2}")
    print(f"-7 // 2 = {-7 // 2}")
    print(f"0.1 + 0.2 = {0.1 + 0.2}")


def convert_integer(text: str) -> int:
    return int(text)


def conversion() -> None:
    # input()が返す文字列に相当する固定例。入力待ちはしない。
    raw = "2"
    quantity = convert_integer(raw)
    print(f"raw={raw!r}, type={type(raw).__name__}")
    print(f"quantity={quantity}, type={type(quantity).__name__}")
    print(f"quantity + 1 = {quantity + 1}")
    print(f"float('3.5') = {float('3.5')}")


def conditions() -> None:
    x = 2
    print(f"x == 2: {x == 2}")
    print(f"x != 2: {x != 2}")
    print(f"x < 3: {x < 3}")
    for quantity in (-1, 0, 1):
        if quantity < 0:
            message = "個数は0以上"
        elif quantity == 0:
            message = "注文なし"
        else:
            message = "注文あり"
        print(f"quantity={quantity}: {message}")
    print(f"x after comparisons={x}")


def lists() -> None:
    a = [10, 20]
    alias = a
    copied = a.copy()
    print(f"a[0]={a[0]}, a[-1]={a[-1]}, len(a)={len(a)}")
    alias.append(30)
    print(f"after alias.append: a={a}, alias={alias}, copied={copied}")
    copied[0] = 99
    print(f"after copied[0] update: a={a}, copied={copied}")
    print(f"alias is a: {alias is a}")
    print(f"copied is a: {copied is a}")


def shallow_copy() -> None:
    original = [[1], [2]]
    copied = original.copy()
    copied[0].append(9)
    print(f"after inner append: original={original}, copied={copied}")
    copied.append([3])
    print(f"after outer append: original={original}, copied={copied}")
    print(f"copied is original: {copied is original}")
    print(f"copied[0] is original[0]: {copied[0] is original[0]}")


def dictionary() -> None:
    order = {"name": "ノート", "price": 200, "quantity": 2}
    print(f"name={order['name']!r}")
    print(f"subtotal={order['price'] * order['quantity']}")
    order["quantity"] = 3
    print(f"updated quantity={order['quantity']}, subtotal={order['price'] * order['quantity']}")
    print(f"order.get('discount', 0)={order.get('discount', 0)}")
    print(f"'price' in order: {'price' in order}")
    print(f"keys={list(order)}")


def for_trace() -> None:
    total = 0
    print(f"initial total={total}")
    for step, price in enumerate([200, 120, 80], start=1):
        before = total
        total += price
        print(f"step={step}, price={price}, before={before}, after={total}")
    empty_total = 0
    iterations = 0
    for price in []:
        iterations += 1
        empty_total += price
    print(f"empty list: iterations={iterations}, total={empty_total}")


def range_demo() -> None:
    print(f"range(3): {list(range(3))}")
    print(f"range(0): {list(range(0))}")
    print(f"range(1, 4): {list(range(1, 4))}")
    print(f"range(1, 6, 2): {list(range(1, 6, 2))}")
    print(f"range(3, 0, -1): {list(range(3, 0, -1))}")


def while_update() -> None:
    count = 0
    print(f"initial count={count}")
    while count < 3:
        before = count
        count = count + 1
        print(f"before={before}, after={count}")
    print(f"final condition: {count} < 3 is {count < 3}")
    print(f"final count={count}")


def subtotal(price: int, quantity: int) -> int:
    """値を返す小さな計算例。注文集計の入力検証とは別の関数。"""
    return price * quantity


def show_subtotal(price: int, quantity: int) -> None:
    print(f"display: {subtotal(price, quantity)}")
    # returnを省略して末尾へ到達するとNoneを返す。


def local_increment(number: int) -> int:
    number = number + 1
    return number


def functions() -> None:
    amount = subtotal(200, 2)
    print(f"subtotal(200, 2)={amount}")
    print(f"amount + 10={amount + 10}")
    result = show_subtotal(200, 2)
    print(f"show_subtotal returned={result!r}")
    print(f"returned type={type(result).__name__}")
    number = 100
    print(f"outer number before={number}")
    updated = local_increment(number)
    print(f"local_increment returned={updated}")
    print(f"outer number after={number}")


def exceptions() -> None:
    try:
        convert_integer("two")
    except ValueError as error:
        # 実際の例外から取得。フルtracebackではなく、場所とコードを抜粋。
        # 絶対パスと行番号は出力を環境に依存させないため省略する。
        print("Traceback excerpt (file / function / source):")
        print("Traceback (most recent call last):")
        for frame in traceback.extract_tb(error.__traceback__):
            print(f'  File "{Path(frame.filename).name}", in {frame.name}')
            print(f"    {frame.line}")
        print(f"{type(error).__name__}: {error}")
    try:
        [10][1]
    except IndexError as error:
        print(f"{type(error).__name__}: {error}")
    try:
        {"price": 200}["missing"]
    except KeyError as error:
        print(f"{type(error).__name__}: {error}")
    try:
        "2" + 1
    except TypeError as error:
        print(f"{type(error).__name__}: {error}")
    try:
        1 / 0
    except ZeroDivisionError as error:
        print(f"{type(error).__name__}: {error}")


CASES = {
    "rebinding": rebinding,
    "types": types,
    "conversion": conversion,
    "conditions": conditions,
    "lists": lists,
    "shallow-copy": shallow_copy,
    "dictionary": dictionary,
    "for-trace": for_trace,
    "range": range_demo,
    "while-update": while_update,
    "functions": functions,
    "exceptions": exceptions,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES, help="観察する概念を1つ選ぶ")
    args = parser.parse_args(argv)
    CASES[args.case]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
