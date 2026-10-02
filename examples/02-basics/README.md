# 第2回: 架空注文の集計

Python 3.12以上、標準ライブラリのみ。以下はリポジトリのルートから実行します。`python3 --version`で3.12以上を確認してください。

```sh
python3 examples/02-basics/order_summary.py
```

既定の架空データはノート200円×2、ペン120円×3。総額は760円です。出力はJSONで、`quantities`が品目別数量、`total_yen`が総額です。

`summary(orders) -> int`は総額だけを返す公開例、`summarize(orders) -> dict`は品目別数量も返す関数です。リスト・辞書・関数・`for`・`if`・例外を一つの処理で確認できます。どちらも入力を変更しません。

| 項目 | 入力契約 |
| --- | --- |
| 入力全体 | 注文辞書のリスト。空リストの総額は0 |
| `name` | 文字列。空文字も型としては受け付ける |
| `price` | 0以上の整数、単位は円。`bool`や小数、文字列は不可 |
| `quantity` | 0以上の整数。`bool`や小数、文字列は不可 |
| 同じ品目 | 個数を加算。価格は各注文行の値を使用 |
| 不正な値 | 関数は`ValueError`を送出 |

入力を変えるにはUTF-8 JSONファイルを使います。実在の注文や個人情報は用いません。

```json
[{"name": "ノート", "price": 200, "quantity": 2},
 {"name": "ペン", "price": 120, "quantity": 3}]
```

```sh
python3 examples/02-basics/order_summary.py /path/to/orders.json
```

成功は終了コード0。ファイルを読めない、JSONが不正、値が契約に反する場合は標準エラーへ説明を出して終了コード2です。`try`の中で入力・集計を行い、例外の処理をCLIの境界へまとめています。

変更前に「数量0は許すか」「円未満は扱うか」を仕様として決め、その境界をテストにします。公開検証は`python3 -m unittest discover -s tests -p test_foundations.py`です。
