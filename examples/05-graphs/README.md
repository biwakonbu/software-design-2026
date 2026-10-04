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
