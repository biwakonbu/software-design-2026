# 第03回の公開学習サンプル

[本人の公開Gist](https://gist.github.com/biwakonbu/7aa6c2d4eba43e49f852381734a38265) を同じIDで更新しました。全7ファイルをGitHubから読み戻し、下記SHAと一致しました。主例10テスト/3906整数リスト、参考8テスト/1764ケースと272ケース、READMEの実行例をPython3.12.13・3.14.7で実行し、標準出力・空の標準エラー・終了0を確認しました。旧4Pythonの内容は保持しています。

|ファイル|SHA-256|
|---|---|
|README.md|`24c4f39abecaf6524c4204f868d4f8fcf6838a1740c90e28ad41c948ae7cb0eb`|
|binary_search_buggy.py|`45ad0611e6b0156a951cf06dcfc1ffc4475c4ac57c7ee19e4df67fb30d719b78`|
|binary_search_corrected.py|`d86d2e5491a31a3f90d4aa6a357d5ebbfc6d8dc4b0d493e6b12d4856c48d350c`|
|highest.py|`58c336f6f0780adc3e64691f12163d7ff9a2726991e806b1874d135e1f72e75f`|
|test_contract.py|`16b44ce9bcfd5543faa3efbeae46445b39f21f38bdafedbea39a875055110b5e`|
|test_highest.py|`adda5f8445eb53b780be5287cef3da0abf32bc94e13137c13a210476c5842b5f`|
|verify.py|`b089ad4c4d21b7560ac81d3519a135a501855fe309e52d85852865987de70198`|

以下は公開READMEと同じ内容です。

---

# 第03回: AIを学習相手として使う

主例はfor文と初期値で理解の変化を確かめ、二分探索は別冊演習Bにつながる参考として使います。収録は `highest.py`、`test_highest.py`、`binary_search_buggy.py`、`binary_search_corrected.py`、`verify.py`、`test_contract.py`、`README.md` の7ファイルだけです。すべて自作教材で、学生情報、課題の完成解答、授業・採点条件は含めません。

## 主例: for文と初期値 (highest.py / test_highest.py)

二分探索用の既存Python 4ファイルは変更していません。`python3 test_contract.py` の期待出力は従来どおり `8 tests passed; exhaustive contract: 1764 cases` です。

| ファイル | 内容 |
|---|---|
| `highest.py` | `highest_draft`(教材用に自作した誤りの例。特定サービスの回答ではありません)と `highest`(修正版) |
| `test_highest.py` | 仕様と手計算から決めた期待値によるテスト10件 |

```sh
python3 test_highest.py
```

期待出力は `10 tests passed; highest: 3906 integer lists` です。正常・負数・空入力・重複・入力を変更しないことを確認し、長さ0〜5・値-2〜2の整数列非空3905個を `max` と独立に照合し、空の1個は `ValueError` を確かめます（合計3906個）。有限の検査であり、全入力の証明ではありません。Python 3.12以上、標準ライブラリのみで動きます。

### 主例の契約

`highest(temps)` は整数のリストから最大値を返します。空リストでは `ValueError`、入力は変更しません。型チェックは行いません。小数、NaN、文字列、bool、リスト以外はこの教材例の契約外です。`highest_draft` は**意図的な誤り**の例で、負の値だけの入力と空入力で仕様に違反します。実用や提出の正解として使わないでください。

### 予想を書いた後で実行する

以下の複数行コマンドは bash / zsh 用です。他のシェルでは Python 部分をファイルに保存して `python3 ファイル名.py` で実行できます。

`highest.py` と `test_highest.py` を同じディレクトリに置き、そこで次を実行します。

```sh
python3 - <<'PYTHON'
from highest import highest_draft
print(highest_draft([-3, -1, -5]))
print(highest_draft([]))
PYTHON
```

意図的な誤り版の実行結果は2行の `0` です。仕様の期待値 -1 / ValueError と一致しません。

```sh
python3 - <<'PYTHON'
from highest import highest
print(highest([-3, -1, -5]))
try:
    highest([])
except ValueError:
    print('ValueError')
PYTHON
```

修正版の期待出力は2行の `-1` と `ValueError` です。

### 5ステップで使う

| ステップ | この例でやること | 手元に残すもの |
|---|---|---|
| 1 言葉にする | `best` を 0 から始めてよい理由を、1文で書く | 分からない点の1文 |
| 2 予想する | `[-3, -1, -5]` と `[]` について、期待値(仕様)と `highest_draft` の戻り値の予想を別々に書く | 期待値と予想 |
| 3 AIに聞く | 予想を添えて、答えではなく確かめ方のヒントを1つ求める | 説明・ヒント |
| 4 確かめる | `highest_draft` を実行して期待値と比べる。空リストの扱いを Python 3.12 の `max` の文書と照合する | 実行結果・反例・資料 |
| 5 言い直す | 初期値の理由を自分の言葉で書き、`[5]`、`[2, 9, 9]`、`[0, -2]` の戻り値を実行前に予想する | 自分の説明 |

AIを使えない場合は、スライドp10・p15の自作ヒント例、p13の自作誤答例、p19の自作指摘例をAIの返答に見立て、相互質問と公式文書で同じ検証を行います。`highest_draft` は自分の試行に相当する、教材用の誤り例です。

### 学習できたかの確かめ方

AIを使わずに `lowest(temps)`(最小値)を書き、次を確かめます。解答は配布しません。

- 初期値を何にしたか、理由を1文で言える。
- `[3, 7, 5]` と `[8, 9]` の戻り値を、実行前に予想できる。
- `best = 0` で書いた場合に誤る入力を、自分で作れる。
- 結果を `min(temps)` と比べて一致する。

### 注意

- 期待値は `highest_draft` の出力から作らず、仕様と手計算から決めます。
- AIには教材の架空データと最小のコードだけを渡し、氏名・学籍番号・連絡先・パスワード・APIキーを含めません。
- 参考: https://docs.python.org/3.12/library/functions.html#max / https://docs.python.org/3.12/library/unittest.html

---

## 参考: 二分探索の最小反例と契約テスト

ソフトウェアデザイン 2026 第3回「AI時代の学び方」の補助教材です。意図的に誤りを入れた二分探索と修正版を並べ、最小の反例と有限の検証で違いを確かめます。

### 公開範囲

| 項目 | 内容 |
| --- | --- |
| 収録ファイル | 下表の5ファイル（このREADMEは主例と共通） |
| 由来 | 公開リポジトリ `biwakonbu/software-design-2026` の commit `0c0be0afbac421ad84628ca0e41ab6d07fb6227c` にある `examples/03-ai-workflow/` の3ファイルを無変更で収録 |
| 新規 | `test_contract.py` と、このREADME |
| 作者 | すべて教材用の自作コード。buggy版は説明用の架空のAI出力で、実際の対話、特定サービスの回答、学生の提出物ではない |
| 含まないもの | 講義スライド、演習課題、授業・採点条件、学生データ、リポジトリの `tests/` |

### ファイルの役割

| ファイル | 役割 |
| --- | --- |
| `binary_search_buggy.py` | **意図的な誤り**を含む例。`low < high` のため、候補が1個残ったときに調べず `None` を返す |
| `binary_search_corrected.py` | 修正版。候補を閉区間 `[low, high]` で表し、`low <= high` の間は調べる |
| `verify.py` | 最小反例 `[7]`（スライドの `[1]` と同じ、候補1個の反例）を表示し、修正版を大きさ0から15の偶数列で272ケース検証する |
| `test_contract.py` | 入力契約を確かめる8個のテスト (標準ライブラリの `unittest`) |
| `README.md` | この説明 |

### 必要環境

- Python 3.12以上
- 標準ライブラリのみ (追加インストールなし)
- 二分探索用のPython 4ファイルを同じディレクトリに置く

### 実行

ダウンロードしたディレクトリで実行します。

```sh
python3 verify.py
python3 test_contract.py
```

`verify.py` の期待出力 (3行):

```text
反例: values=[7], target=7
buggy: None corrected: 0
修正版の有限入力検証: 272 cases passed
```

`test_contract.py` の期待出力 (1行):

```text
8 tests passed; exhaustive contract: 1764 cases
```

失敗したときは、unittestの詳細を標準エラーに出して終了コード1で終わります。`verify.py` は `assert` を使うため、`python3 -O` や環境変数 `PYTHONOPTIMIZE` を使うと検証が行われず、`test_contract.py` のテスト7（`PYTHONOPTIMIZE` の場合はテスト8が別プロセスで起動する `verify.py` も）も実質的に検査しません。`-O` を付けずに実行してください。

### 入力契約

| 項目 | 内容 |
| --- | --- |
| 入力 | 昇順に整列済みの整数リスト `values` と、探索値 `target` |
| 戻り値 | 一致する添字を1つ。見つからなければ `None` |
| 非整列の入力 | 仕様外。結果は保証しない |
| 整列の検査 | 行わない。並べ替えもしない |
| 重複 | 一致する添字ならどれでもよい。先頭の添字は保証しない (例: `[2, 2, 2]` から2を探すと修正版は1を返す) |
| 入力の変更 | しない |

### テストの内容

| 番号 | 確認すること |
| --- | --- |
| 1 | 正常系: 先頭、末尾、負数、1要素 |
| 2 | 空リストと、値が存在しない場合 |
| 3 | 重複: 戻り値が一致する添字のどれかであること |
| 4 | 大きな整数 |
| 5 | 長さ0から5、値-2から2の昇順列 (重複あり) 252個 x target -3から3 = 1764ケース。`target in values` を独立の正解とし、戻り値の添字、`None` の条件、入力を変更しないことを確かめる |
| 6 | 意図的なbuggy版が、候補1個の反例などで契約に違反することを確かめる |
| 7 | `verify.verify()` が272を返すこと |
| 8 | `verify.py` と `binary_search_corrected.py` を別プロセスで実行し、標準出力を期待値と照合する |

### 検証の限界

| 検証 | 範囲 | 範囲外 |
| --- | --- | --- |
| `verify.py` | 大きさ0から15の重複なし偶数列、存在する値と欠けた値 | 重複、負数、大きい入力 |
| `test_contract.py` | 小さな定義域の全列挙と個別例 | 長いリスト、定義域外の値、非整列の入力 |

有限個のテストに合格しても、全入力での正しさの証明にはなりません。正しさは、候補が閉区間 `[low, high]` にあるという不変条件と、毎回候補が減るので終了するという理由を合わせて説明してください。

### 誤り例についての注意

`binary_search_buggy.py` は学習のための**意図的な誤り**です。実用、課題の提出、他教材への正解としての転用はしないでください。


## 第04回：処理順・木・探索

[検証済み公開Gist](https://gist.github.com/biwakonbu/ad6341fde64f3a41d5b4f1fa60711edf)。本人所有・public、Python3.12.13/3.14.7でデモと2テスト（全364整数列と木の境界）を実行し、独立Opus5.5レビューに合格しました（53,114ms）。任意の自習用で、提出条件は追加していません。保存後に全5ファイルをreadbackし、次のSHAと一致しました。第03回のGistは変更していません。

| ファイル | SHA-256 |
|---|---|
| README.md | `f869dc6fc6f31851f7a5a0cbc0e88947529bb71b74d933d021ab57cf175372a4` |
| containers.py | `72eabe680b322eae21a9d95c33c4d2ebfc8e27ea8e853ea739392bcf20923928` |
| sorting_search.py | `fdd8c1c1de6be9bb903a97310db83d4f9315cd6c10fa9377564bb1b96e6c3334` |
| test_examples.py | `622adc2068ba59f290c66c6a6e47fb637d8481dc833f4c0462ee87963e58a24a` |
| trees.py | `e6b4dfff3e344a38088d1dcbe8ae807fabfefae23333a2a7c55d9630b1be860c` |


## 第05回：グラフ・BFSと経路復元

[検証済み公開Gist](https://gist.github.com/biwakonbu/b3ff11e2b12c062e11854f5df658269b)。本人所有・public、Python3.12.13/3.14.7でデモと4テスト（全64グラフ・1024経路と境界）を実行し、独立Opus5.5レビューに合格しました（53,114ms）。自習用で提出条件は追加していません。保存後の全3ファイルをreadbackし、次のSHAと一致しました。

| ファイル | SHA-256 |
|---|---|
| README.md | `b71a1d2ee4a8d3cf7da0dfbd87ab477b43f7bc297d7629b2d5c17171bce76e4d` |
| graphs.py | `31d97d6c840efafe050a803e865443f928df22652669806bb5eef0d27989c156` |
| test_graphs.py | `6e494840cd9847c7bbe0b26f262e8afe60173c70b7c349e10f833838d3ac23cb` |


## 第08回：電卓の字句・構文・意味解析

[検証済み公開Gist](https://gist.github.com/biwakonbu/f6214b0649b0581842fb41cba2fc21e7)。本人所有・publicで、保存後の全3ファイルSHAをreadbackしました。Python3.12.13/3.14.7で4テスト、3375計算と72除算、正常・境界・失敗・CLIのstdout/stderr/終了コードを照合しました。実Opus5.5の公開前レビューは合格（64,585ms）。公開済み自作referenceはbyte一致で、READMEとテストを添えた自習用です。有限の検証範囲と数値の制約をREADMEに明記しました。既存の非公開Gist、授業契約・課題解答・学生情報を収録していません。

| ファイル | SHA-256 |
|---|---|
| README.md | `eb114c96c5bfab5edf6c2015c6eeb51c7cd4153366680039336702784a4bbc91` |
| calculator.py | `678b9c5cfd7f07be6af501600950ab2811968e2ae714a0fc7ff9094c7d3b14cf` |
| test_calculator.py | `bd017bf596bffcb7bffffb10e9a1b7c2338e31d0ba1e3f326d28d9e4b7e4ad42` |
