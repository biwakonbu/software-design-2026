# 第4回: データ構造とアルゴリズム

Python 3.12以上。以下はルートから実行する独立した公開デモです。

```sh
python3 examples/04-algorithms/memory_complexity.py
python3 examples/04-algorithms/containers.py
python3 examples/04-algorithms/sorting_search.py
python3 examples/04-algorithms/trees.py
```

| ファイル | 学習内容・観察 |
| --- | --- |
| `memory_complexity.py` | メモリのbytes、O(1)/O(log n)/O(n)/O(n log n)/O(n²)の成長比較 |
| `containers.py` | listスタックのLIFO、dequeキューのFIFO、deque両端操作 |
| `sorting_search.py` | 挿入ソート、マージソート、線形探索、全探索、二分探索 |
| `trees.py` | 木の親子構造、DFS前順、BFSレベル順 |

## メモリと計算量

`sys.getsizeof`は**浅いサイズ**です。リストの参照先オブジェクトを再帰的に足した総メモリではありません。同じ文字列への参照を10個持つ例では、文字列を10回分として数えてもいけません。数値はPython実装・OS・版に依存し、固定の提出期待値にしません。

`comparison_counts(n)`の表は実測秒数ではなく、典型的な操作回数のモデルです。半減処理を`while n > 0`で数えた値は`n.bit_length()`、順序付き全ペアはn²です。Big-Oは上界の増え方を表し、定数や小入力での速さを決めません。入力サイズ、最悪/平均/最良のどれか、数える処理を明示してください。

## データ構造の操作

スタックは末尾へ`append`し末尾から`pop`します。list末尾操作は償却O(1)。キューは`deque.append`と`popleft`、両端操作はO(1)です。listの`pop(0)`は残り要素の移動が必要でO(n)。`stack_order([A,B,C])`はC,B,A、`queue_order`はA,B,Cとなり、元のリストは変えません。

## ソートと探索

| 処理 | 契約 | 時間の目安 |
| --- | --- | --- |
| 挿入ソート | 新しい整列済みリストを返す | 最悪O(n²)、整列済みはO(n) |
| マージソート | 新しい整列済みリストを返す | O(n log n)、補助領域O(n) |
| 線形探索 | 最初の一致添字、未発見は`None` | 最悪O(n) |
| 全探索 | 和が目標になる添字組`i < j`を全て返す | O(n²)、結果領域は組の数に依存 |
| 二分探索 | 昇順整列済みが前提、一致添字1つまたは`None` | O(log n) |

二分探索に先立つ整列は別コストです。重複時の最初の位置は保証しません。`[7,2,4,2,9]`の整列結果は`[2,2,4,7,9]`。全探索は値が同じでも違う添字を区別します。

## 木のDFS/BFS

デモの木は`A → B(D,E), C(F)`。DFSは`A B D E C F`、BFSは`A B C D E F`です。全ノード数をVとして両者O(V)。DFSの再帰呼び出しは木の高さhに比例し、非常に深い木ではPythonの再帰上限に達します。BFSのキューは最大幅に比例します。どちらも戻り値リストのO(V)を別に持ちます。

`Node`は閉路・共有子を持たない木を前提とし、空の木`None`には空リストを返します。閉路を許すグラフでは訪問済み管理が必要で、第5回の実装へ進みます。

検証: `python3 -m unittest discover -s tests -p test_foundations.py`。小入力の順列をPythonの`sorted`と照合し、境界、未発見、重複、入力不変性を確かめます。
