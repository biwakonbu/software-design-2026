# 第10回: 変数と関数

このフォルダだけで実行できます。Python 3.12 以上、標準ライブラリのみを使います。Python を host にすること、この Lisp 方言の構文・真偽値・組み込み関数は**教材で選んだ設計**です。2026年シラバスが特定の処理系や方言を指定しているわけではありません。

## 実行

リポジトリのルートから:

```sh
python3 examples/10-lisp-functions/lisp.py --eval '(+ 1 (* 2 3))'
python3 examples/10-lisp-functions/lisp.py
python3 examples/10-lisp-functions/starter.py --eval '(square 5)'
```

期待値は順に `7`、対話入力の結果、`25`。REPL は一行ごとに読みます。EOF または単独の `:quit` で終了し、不正な入力の後も次の行を受け付けます。複数行を補完するエディタはありません。成功終了は 0、--eval の言語エラーは 1、CLI 引数エラーは 2。

## reference と starter

- `lisp.py`: 完成 reference。Token → read_all → Interpreter.evaluate → Env / Closure の順に追います。
- `starter.py`: reference を読み込み、square だけを追加した実行可能な拡張 starter です。完成処理系の穴埋めではなく、小さな拡張を考える入口です。未実装の TODO はありません。

ウォームアップで変更する場所は、starter.py の machine.add_builtin の第2引数である lambda x: number(x) ** 2 です。次の順に作業してください。

- このコールバックを、名前付き square 関数に置き換える。
- number で数値を確認した後に、負数なら LispError を送出する分岐を加える。
- LispError も lisp から import する。
- 正常値とエラーを確認する。

この square は host の拡張で、meta 利用者環境には自動登録されません。

## 機能と境界

算術の引数: 四則の `+` と `*` は 0 個以上 (引数がなければ結果は `0` / `1`)、`-` と `/` は 1 個以上の数値を取ります。単項 `-` は符号反転、単項 `/` は逆数です。

数値: 数値は int / float で、除算の結果は実数です。float には丸め誤差があります。浮動小数の入力と演算結果は有限値だけを許し、Infinity / NaN を値として扱いません。整数は任意精度ですが、十進文字列の入出力は Python の桁数安全制限に従います。

失敗の扱い:

- 指数表記が範囲を超える場合は、read の言語エラーです。
- 演算結果の非有限値や、int から float への変換 overflow は、適用時の言語エラーです。
- 十進文字列の桁数の限界超過は、LispError に変換します。
- 未知の名前、空の呼び出し、0 除算、括弧の不一致は LispError になります。

コメントは `;` から行末までです。読み取り器と評価器を分け、Python の eval / exec は使いません。
追加の特殊形式: `define lambda if quote begin`。比較 `= < >` と `not`。`'x` は `(quote x)` の短縮です。関数定義は `(define f (lambda (x) ...))` で、`(define (f x) ...)` の省略形はありません。lambda は重複しない固定個数の仮引数と一つ以上の本文を取ります。スコープは字句スコープで、定義時の環境を捕捉します。再帰は定義先と同じ環境をクロージャが参照することで成立します。

**`#f` だけが偽**です。0、空リスト、#t は真。boolean は数値ではなく、`(+ #t 1)` はエラー。`'()` は空のデータ、`()` の評価はエラー。if は選んだ枝だけを評価します。関数適用は演算子と引数を左から右に評価します。Symbol と string は別の型です。

```lisp
(begin
  (define make-adder (lambda (x) (lambda (y) (+ x y))))
  (define add10 (make-adder 10))
  (add10 3)) ; => 13
```
この段階の execute は一つのフォーム。複数の処理は begin に入れます。文字列の評価、list 操作、script CLI は第11回で導入します。

## 検証

ルートで `python3 -m unittest discover -s tests -p 'test_languages.py' -v`。reader、算術、arity、環境、回復、host/meta 互換を確認します。

## 環境寿命と再帰を観察する補足

`learning_trace.py` は完成hostの理解確認用です。新しい処理系・提出課題・採点条件ではありません。予測を先に書き、出力を講義の環境図と照合してください。

```sh
python3 examples/10-lisp-functions/learning_trace.py closure
python3 examples/10-lisp-functions/learning_trace.py fact
```

closureの期待出力：

```text
[closure]
define make-adder: captured=G
call make-adder(5): E5 x=5, parent=G
returned add5: captured=E5; make-adder call finished
call add5(3): E3 y=3, parent=E5
lookup x: E5=5; lookup y: E3=3
result: 8
```

Gは大域環境、E5はmake-adderへ5を渡した呼び出し環境、E3はadd5へ3を渡した呼び出し環境の説明用の名前です。メモリ番地ではありません。実際の呼び出しが作った環境を記録しています。add5の定義環境としてE5への参照が残り、E3の親になるため、外側の呼び出し終了後もxを読めます。

factの期待出力：

```text
[fact]
call fact: n=2
call fact: n=1
call fact: n=0
return fact: n=0 => 1
return fact: n=1 => 1
return fact: n=2 => 2
result: 2
```

各callのnは別のローカル環境です。0から戻るときに、待っていた掛け算が順に完了します。入力2では戻り値1が続くため、callのnと戻り値を区別して読んでください。

引数なしは両方、`--help`は使い方を表示します。正常終了0、未知のCASEは2です。観察用のPythonクラスは完成参照の評価器へ処理を任せ、環境と戻り値だけを記録します。計算式の評価や環境作成の実装を複製していません。

補足の検証：`python3 -m unittest discover -s tests -p 'test_learning_traces.py' -v`。
