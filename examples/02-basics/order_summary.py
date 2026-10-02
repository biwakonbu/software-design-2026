"""架空の注文を集計する公開例。外部ライブラリ・ネットワークは不要。"""

import argparse
import json
from pathlib import Path

DEMO_ORDERS = [
    {"name": "ノート", "price": 200, "quantity": 2},
    {"name": "ペン", "price": 120, "quantity": 3},
]


def summarize(orders: list[dict]) -> dict:
    """円の整数価格と0以上の整数個数を受け取り、品目別数量と総額を返す。"""
    if not isinstance(orders, list):
        raise ValueError("入力は注文のリストにしてください")
    quantities = {}
    total = 0
    for index, order in enumerate(orders):
        if not isinstance(order, dict):
            raise ValueError(f"注文{index}: オブジェクトが必要です")
        item = order.get("name")
        price = order.get("price")
        quantity = order.get("quantity")
        if not isinstance(item, str):
            raise ValueError(f"注文{index}: nameは文字列です")
        # boolもintの一種なので、金額・個数では明示的に除く。
        if type(price) is not int or price < 0:
            raise ValueError(f"注文{index}: priceは0以上の整数です")
        if type(quantity) is not int or quantity < 0:
            raise ValueError(f"注文{index}: quantityは0以上の整数です")
        quantities[item] = quantities.get(item, 0) + quantity
        total += price * quantity
    return {"quantities": quantities, "total_yen": total}


def summary(orders: list[dict]) -> int:
    """演習と同じ契約で総額だけを返す公開例。"""
    return summarize(orders)["total_yen"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="UTF-8のJSON注文リスト")
    args = parser.parse_args()
    try:
        orders = json.loads(args.input.read_text(encoding="utf-8")) if args.input else DEMO_ORDERS
        print(json.dumps(summarize(orders), ensure_ascii=False, sort_keys=True))
    except (OSError, ValueError) as error:
        parser.exit(2, f"入力エラー: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
