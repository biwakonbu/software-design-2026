# 第5回: グラフの隣接リスト

Python 3.12以上で、ルートから`python3 examples/05-graphs/graphs.py`を実行します。頂点は架空のID、辺は接続を表します。`dict[str, list[str]]`で全頂点をキーに持ち、孤立点は空リストです。

デモはA–B–D、A–C–Dの閉路と孤立点X。BFSは`A B C D`、DFSは`A B D C`、AからDの最短経路は`[A,B,D]`です。同じ長さの経路が複数なら隣接リストの順で選びます。接続成分は`[A,B,C,D]`と`[X]`の2つです。

| 関数 | 結果・契約 |
| --- | --- |
| `bfs(graph, start)` | 到達可能な頂点を幅優先順に返す |
| `dfs(graph, start)` | 到達可能な頂点を深さ優先順に返す |
| `shortest_path(graph, start, goal)` | 辺数最小の経路1つ。到達不能は`None`、同頂点は`[start]` |
| `connected_components(graph)` | **無向グラフ専用**の接続成分。空グラフは`[]` |
| `validate_graph(graph, undirected=False)` | 全隣接先が定義済みか検査。指定時は逆向き辺も検査 |

未知の始点/終点、未定義の隣接先は`ValueError`。無向グラフは両方向を記述します。DFS/BFSは訪問済み管理があるので閉路、自分への辺、重複辺でも終了します。BFSはキューへ追加した時点で訪問済みにし、`previous`で前の頂点を記録して逆向きに経路を復元します。

隣接リスト上の探索と接続成分列挙はO(V+E)です。訪問記録と戻り値はO(V)です。検査時には逆向き辺の確認用集合が別途O(V+E)必要です。無向辺は隣接リストに2回登場しますが、Big-Oの定数には影響しません。

有向グラフの`bfs`/`dfs`/`shortest_path`は矢印の向きにだけ移動します。A→BがあってもB→Aは保証されず、有向グラフの強連結・弱連結はこの`connected_components`の対象外です。

**重み付きの最小費用問題とは区別してください。** A→Dが1辺100円、A→B→Dが2辺で各1円なら、辺数最小はA→Dでも費用最小は別です。時間・費用・乗換制約を扱う実路線には、この教材のBFSだけでは足りません。

検証: `python3 -m unittest discover -s tests -p test_foundations.py`。4頂点の無向グラフ64通りを列挙し、全始終点について単純経路の全探索と最短距離を照合します。

## 自習ガイド：コードを読む順番と期待値

講義第05回の追加頁と同じ順で、このフォルダのコードを自分で追うための補足です。実行するのは冒頭と同じ `python3 examples/05-graphs/graphs.py` だけです。

### 読む順番

| 順 | 読むもの | 確かめること |
| --- | --- | --- |
| 1 | 校内マップの図 | 場所が頂点、通路が辺。図の位置や線の長さはデータではない |
| 2 | `DEMO_GRAPH` | キーが全頂点V。`graph["A"]` は1辺で行ける頂点だけ。隣接項目8個で無向辺4本 |
| 3 | `shortest_path` の探索部分 | 発見時に `previous` へ記録し、取り出した `vertex` が goal かを判定する |
| 4 | `shortest_path` の復元部分 | D→B→A→None とたどり、`path[::-1]` で `['A', 'B', 'D']` |
| 5 | `dfs` | `stack.pop()` で後入れ先出し。取り出し時に印を付けるので、候補が重複し得る |
| 6 | `connected_components` | 無向専用。`_bfs` が返す到達頂点のリストを1成分とし、`unseen` から除く |
| 7 | `validate_graph` | 隣接先が定義済みか。`undirected=True` のときは逆辺も検査する |

### 講義スライドとの名前の対応

| 役割 | 講義スライド | graphs.py |
| --- | --- | --- |
| 直前の頂点の辞書 | `parent` | `previous` |
| 取り出した頂点 | `node` | `vertex` |
| 復元中に今いる頂点 | `node` | `cursor` |
| 逆順にする | `path.reverse()` | `path[::-1]` |

### 実行したときの出力

```text
BFS: ['A', 'B', 'C', 'D']
DFS: ['A', 'B', 'D', 'C']
A→D 最短経路: ['A', 'B', 'D']
接続成分: [['A', 'B', 'C', 'D'], ['X']]
有向グラフは辺の向きに従う。重み付き最小費用にはこのBFSを使わない。
```

BFSの `['A', 'B', 'C', 'D']` は取り出した順で、経路ではありません。BとCの間に辺がないからです。接続成分は、講義の連結成分と同じ意味です。

### 境界の呼出しと期待値

`g = DEMO_GRAPH` とします。

| 呼出し | 期待値 |
| --- | --- |
| `shortest_path(g, "A", "A")` | `['A']` |
| `shortest_path(g, "A", "X")` | `None`（Xは定義済みで到達不能） |
| `shortest_path(g, "A", "Z")` | `ValueError`（未知の名前） |
| `dfs(g, "X")` | `['X']` |
| `connected_components({})` | `[]` |
| `validate_graph({"A": ["B"], "B": []}, undirected=True)` | `ValueError`（逆向きの辺がない） |

`previous` の初期値 `{start: None}` の None は「前の頂点なし」という印です。戻り値の `None`（到達不能）とは意味が違います。型注釈は実行時の検査ではありません。公開探索関数は入口で `validate_graph` を呼び、始点・終点を受け取る関数では、その名前がキーにあることも確認します。

### 演習の入力変更

| 変更 | 期待値 |
| --- | --- |
| B–Dを両方向から削除 | A→Dは `['A', 'C', 'D']` |
| さらにC–Dも削除（Dは値 `[]` で残す） | A→Dは `None` |
| 有向 `{"A": ["B"], "B": ["D"], "D": []}` | A→Dは `['A', 'B', 'D']`、D→Aは `None` |

表の有向データには逆辺がないため、`connected_components` の検査で `ValueError` になります。

### 追加領域の補足

`validate_graph` は `undirected=False` のときも、最初に `adjacency_sets` を作ります。そのため、すべての公開関数が O(V + E) の追加領域を使います。探索本体の `queue`・`previous`・`visited` は O(V) です。`dfs` の `stack` には同じ頂点の候補が重複して入るので、O(V) に収まるとは限りません。
