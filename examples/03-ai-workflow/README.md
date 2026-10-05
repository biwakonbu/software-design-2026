# 第3回: AI時代の学び方

[公開Gist](https://gist.github.com/biwakonbu/7aa6c2d4eba43e49f852381734a38265) と同じ主例を収録しています。整数リストの最高値を題材に、疑問・予想・ヒント・検証・説明の5ステップを練習します。

リポジトリのルートから実行します。

```sh
python3 examples/03-ai-workflow/test_highest.py
python3 examples/03-ai-workflow/test_contract.py
python3 examples/03-ai-workflow/verify.py
```

期待出力はそれぞれ `10 tests passed; highest: 3906 integer lists`、`8 tests passed; exhaustive contract: 1764 cases`、反例を含む3行です。詳しい契約・意図的な誤りの扱い・検証範囲は [Gist収録内容](../../docs/gist-samples.md) を参照してください。有限テストは全入力での正しさの証明ではありません。課題の条件は `exercises/03.md` に従います。

## 参考: 二分探索


これは説明用に作った**架空のAI出力**です。実際の対話や学生の提出ではありません。Python 3.12以上で、ルートから実行します。

```sh
python3 examples/03-ai-workflow/verify.py
```

`binary_search_buggy.py`は意図的な誤りを含みます。`low < high`では探索範囲が1要素になった時に止まり、その要素を検査しません。無限ループや外部への書き込みはありません。

| 反例 | buggy | corrected |
| --- | --- | --- |
| `[7]`の7 | `None` | 0 |
| `[1, 3]`の3 | `None` | 1 |

`binary_search_corrected.py`は公開修正版です。候補を閉区間`[low, high]`で表し、空になるまで`low <= high`で検査します。整数除算で中央を決め、候補を厳密に減らすので終了します。

両者の入力契約は**昇順整列済みの整数リスト**と探索値です。出力は一致する添字1つ、なければ`None`。重複があっても最初の添字は保証しません。並べ替えや入力の整列検査は行いません。

`verify.py`は大きさ0〜15の偶数列で、存在する値と欠けた値を272ケース確認します。この有限検証だけで全入力の正しさは証明できません。空列・境界・重複のテストと、候補区間の不変条件・終了理由を合わせて説明してください。

AIを使う際は、仕様と戻り値を先に書き、予測できる小入力を渡します。反例が出たら「失敗入力・期待値・実値・原因・変更・再検証」を記録します。未確認の解説を正しさの根拠にせず、自分で実行と追跡を行います。

```sh
python3 -m unittest discover -s tests -p test_foundations.py
```
