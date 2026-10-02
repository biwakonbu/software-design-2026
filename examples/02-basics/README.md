# 第2回: 概念デモと架空注文の集計

Python 3.12以上、標準ライブラリのみ。以下はリポジトリのルートから実行します。`python3 --version`で3.12以上を確認してください。

## 概念を1つずつ実行する

リポジトリのルートから、調べるケースを1つ指定します。入力待ちはありません。先に結果を予測し、実行後に `concepts.py` の該当関数を読んで理由を確かめます。

```sh
python3 examples/02-basics/concepts.py rebinding
python3 examples/02-basics/concepts.py --help
```

| ケース名 | 観察すること |
| --- | --- |
| `rebinding` | 整数と文字列の不変性、名前の再束縛 |
| `types` | 型、加算と連結、除算、商と余り、float |
| `conversion` | inputに相当する文字列を数値へ変換 |
| `conditions` | 比較、-1/0/1の境界、if/elif/else |
| `lists` | 0始まりの添字、別名とコピー |
| `shallow-copy` | 外側をコピーしても内側は共有される |
| `dictionary` | キー参照、値の更新、getの既定値 |
| `for-trace` | 反復ごとの状態、空リストでの0回反復 |
| `range` | 開始・終了・刻み、終了値を含まない範囲 |
| `while-update` | 条件を再評価し、値を更新して終了 |
| `functions` | 引数、return、print、None、名前のスコープ |
| `exceptions` | 例外の種類とtracebackの読み取り |

各ケースは終了コード0です。`exceptions`も、教材で意図した失敗を捕捉して表示します。ケース未指定・未知のケースは使い方を標準エラーに出し、終了コード2です。

### `rebinding`

```sh
python3 examples/02-basics/concepts.py rebinding
```

```text
before: quantity=2, earlier=2
after: quantity=3, earlier=2
text='pen', upper_text='PEN'
```

`earlier = quantity`は値を破壊して移す操作ではなく、同じ整数を指す名前を増やします。`quantity = quantity + 1`は計算結果3へquantityを結び直します。整数2自身は変わらないのでearlierは2のままです。文字列も変更不能で、`upper()`の結果を別の名前へ束縛しても元のtextは変わりません。

### `types`

```sh
python3 examples/02-basics/concepts.py types
```

```text
int: 200
float: 0.1
str: '200'
bool: True
200 + 120 = 320
'200' + '120' = '200120'
7 / 2 = 3.5
7 // 2 = 3
7 % 2 = 1
-7 // 2 = -4
0.1 + 0.2 = 0.30000000000000004
```

同じ`+`でも整数なら加算、文字列なら連結です。`/`はこの例ではfloatを返します。`//`は商を負の無限大側へ切り下げるので、負数では単に小数部分を捨てる結果とは異なります。floatで表現した0.1と0.2の和は厳密な0.3になりません。boolはintの派生型ですが、注文の金額・数量では明示的に除外します。

### `conversion`

```sh
python3 examples/02-basics/concepts.py conversion
```

```text
raw='2', type=str
quantity=2, type=int
quantity + 1 = 3
float('3.5') = 3.5
```

`input()`が返すものと同じ形の文字列を固定値で用意しています。表示が2でも、文字列と整数は別の型です。`int(raw)`で変換してから足します。`int('two')`や`int('2.5')`は変換できずValueErrorになります。失敗の例は`exceptions`で確認できます。

### `conditions`

```sh
python3 examples/02-basics/concepts.py conditions
```

```text
x == 2: True
x != 2: False
x < 3: True
quantity=-1: 個数は0以上
quantity=0: 注文なし
quantity=1: 注文あり
x after comparisons=2
```

`=`は代入、`==`は比較です。比較を実行してもxの値は変わりません。ifから上順に条件を調べ、最初に成立する枝だけを実行します。境界の前・境界上・境界後を区別して追ってください。このデモはメッセージの分岐を示し、例外を送出する注文集計の入力検証とは別です。

### `lists`

```sh
python3 examples/02-basics/concepts.py lists
```

```text
a[0]=10, a[-1]=20, len(a)=2
after alias.append: a=[10, 20, 30], alias=[10, 20, 30], copied=[10, 20]
after copied[0] update: a=[10, 20, 30], copied=[99, 20]
alias is a: True
copied is a: False
```

添字0は先頭、-1は末尾です。`alias = a`では2つの名前が同じリストを参照するため、appendの変更が両方から見えます。`a.copy()`は別の外側リストを作るので、その添字0を更新してもaの添字0は変わりません。`is`は同じオブジェクトかを調べ、内容が等しいかを調べる`==`とは意味が異なります。範囲外の添字は`exceptions`で確認します。

### `shallow-copy`

```sh
python3 examples/02-basics/concepts.py shallow-copy
```

```text
after inner append: original=[[1, 9], [2]], copied=[[1, 9], [2]]
after outer append: original=[[1, 9], [2]], copied=[[1, 9], [2], [3]]
copied is original: False
copied[0] is original[0]: True
```

浅いコピーは外側のリストとその要素への参照をコピーします。内側のリストは複製していないため、copied[0]の変更はoriginal[0]にも見えます。外側のcopiedに新しい要素を追加する操作は、originalの外側へは伝わりません。「コピーしたから全て独立」とは言えない理由を2つの変更から説明してください。

### `dictionary`

```sh
python3 examples/02-basics/concepts.py dictionary
```

```text
name='ノート'
subtotal=400
updated quantity=3, subtotal=600
order.get('discount', 0)=0
'price' in order: True
keys=['name', 'price', 'quantity']
```

辞書は位置ではなくキーで項目を選びます。`order['quantity'] = 3`でそのキーの値を更新します。`get('discount', 0)`はキーがなければ0を返し、`in`はキーの存在を調べます。直接`order['missing']`と参照するとKeyErrorです。キーの列挙順は挿入順で、ソートした順ではありません。

### `for-trace`

```sh
python3 examples/02-basics/concepts.py for-trace
```

```text
initial total=0
step=1, price=200, before=0, after=200
step=2, price=120, before=200, after=320
step=3, price=80, before=320, after=400
empty list: iterations=0, total=0
```

forは各要素をpriceへ順に束縛し、本文を実行します。beforeとafterを比べると、前回の合計へ次の価格を足す流れが見えます。空のリストでは本文を1回も通らず、初期値0が残ります。要素の順番を変えた場合、途中の値と最終の値のどちらが変わるかを考えてください。

### `range`

```sh
python3 examples/02-basics/concepts.py range
```

```text
range(3): [0, 1, 2]
range(0): []
range(1, 4): [1, 2, 3]
range(1, 6, 2): [1, 3, 5]
range(3, 0, -1): [3, 2, 1]
```

rangeの終了値は含みません。開始を省略すれば0、刻みを省略すれば1です。負の刻みなら減る方向へ進みます。range自体は各値を全部持つリストではなく、ここでは`list()`で列を見える形にしています。

### `while-update`

```sh
python3 examples/02-basics/concepts.py while-update
```

```text
initial count=0
before=0, after=1
before=1, after=2
before=2, after=3
final condition: 3 < 3 is False
final count=3
```

whileは本文を繰り返す前に条件を評価します。countを増やすことで、3回目の本文の後に条件がFalseとなります。forの要素列による反復と、whileの条件による反復の違いを説明してください。

### `functions`

```sh
python3 examples/02-basics/concepts.py functions
```

```text
subtotal(200, 2)=400
amount + 10=410
display: 400
show_subtotal returned=None
returned type=NoneType
outer number before=100
local_increment returned=101
outer number after=100
```

実引数200と2は、呼出し先の仮引数priceとquantityへ束縛されます。returnで返した400は次の計算に使えます。画面表示だけのshow_subtotalはreturnを省略しているためNoneを返し、Noneは数値ではありません。local_incrementの仮引数numberと、呼出し元functionsのnumberは別のローカル名です。呼出し先で再束縛しても、呼出し元の名は100のままです。型注釈だけで実行時に引数を検証するわけではありません。この小さなsubtotalは計算のみで、下記のorder_summaryは入力も検証します。

### `exceptions`

```sh
python3 examples/02-basics/concepts.py exceptions
```

```text
Traceback excerpt (file / function / source):
Traceback (most recent call last):
  File "concepts.py", in exceptions
    convert_integer("two")
  File "concepts.py", in convert_integer
    return int(text)
ValueError: invalid literal for int() with base 10: 'two'
IndexError: list index out of range
KeyError: 'missing'
TypeError: can only concatenate str (not "int") to str
ZeroDivisionError: division by zero
```

最初の失敗は実際のValueErrorから取得したtracebackです。**この表示は抜粋**で、環境による絶対パスとソース変更による行番号を省略しています。通常の未捕捉tracebackには行番号なども出ます。最後の診断行で種類と理由を読み、その直前のフレームで失敗したコードを見ます。上のフレームはそこを呼んだ場所です。

後半の4行は別の短い入力を試して捕捉した例外です。順に、存在しない添字、存在しないキー、文字列と整数の連結、ゼロ除算です。全てを同じ理由の失敗にせず、直す入力またはコードを区別してください。

## デモの検証

```sh
python3 -m unittest discover -s tests -p test_basics_concepts.py -v
```

CLI出力をこのREADMEの期待値と照合し、引数・戻り値・文字列変換の境界も検証します。

## 架空注文の集計

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
