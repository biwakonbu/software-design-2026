# 第12回: meta evaluatorの開始

このフォルダだけで実行できます。Python 3.12 以上、標準ライブラリのみを使います。Python を host にすること、この Lisp 方言の構文・真偽値・組み込み関数は**教材で選んだ設計**です。2026年シラバスが特定の処理系や方言を指定しているわけではありません。

## 実行

リポジトリのルートから:

```sh
python3 examples/12-meta-evaluator/lisp.py --eval '(+ 1 (* 2 3))'
python3 examples/12-meta-evaluator/lisp.py
python3 examples/12-meta-evaluator/starter.py --eval '(square 5)'
```

期待値は順に `7`、対話入力の結果、`25`。REPL は一行ごとに読みます。EOF または単独の `:quit` で終了し、不正な入力の後も次の行を受け付けます。複数行を補完するエディタはありません。成功終了は 0、--eval の言語エラーは 1、CLI 引数エラーは 2。

## reference と starter

- `lisp.py`: 完成 reference。Token → read_all → Interpreter.evaluate → Env / Closure の順に追います。
- `starter.py`: reference を読み込み、square だけを追加した実行可能な拡張 starter です。完成処理系の穴埋めではなく、小さな拡張を考える入口です。未実装の TODO はありません。

変更する場所は、starter.py の machine.add_builtin の第2引数である lambda x: number(x) ** 2 です。次の順に作業してください。

- このコールバックを名前付き square 関数に置き換えてください。
- number で数値を確認した後に、負数なら LispError を送出する分岐を加えてください。
- LispError も lisp から import してください。
- 正常値とエラーの両方を確認してください。

この square は host の拡張で、meta 利用者環境には自動登録されません。

## 機能と境界

ここでは Python host の Lisp が受け付ける仕様を説明します。meta 層の対応範囲はLisp で書く評価器の節で示します。

**算術の引数**: 四則の `+` と `*` は 0 個以上 (結果は `0` / `1`)、`-` と `/` は 1 個以上の数値を取ります。単項 `-` は符号反転、単項 `/` は逆数です。

**数値の境界**: 数値は int / float、除算は実数です。float の丸め誤差はあります。浮動小数の入力と演算結果は有限値だけを許し、Infinity / NaN を値として扱いません。指数表記が範囲を超える場合は read の言語エラー、演算結果の非有限値や int から float への変換 overflow は適用時の言語エラーです。整数は任意精度ですが、十進文字列の入出力は Python の桁数安全制限に従い、限界超過を LispError に変換します。

**読取と失敗**: コメントは `;` から行末までです。未知の名前、空の呼び出し、0 除算、括弧の不一致は LispError になります。読み取り器と評価器を分け、Python の eval / exec は使いません。

追加の特殊形式: `define lambda if quote begin`。比較 `= < >` と `not`。`'x` は `(quote x)` の短縮です。関数定義は `(define f (lambda (x) ...))` で、`(define (f x) ...)` の省略形はありません。lambda は重複しない固定個数の仮引数と一つ以上の本文を取ります。定義時の環境を捕捉する字句スコープ。再帰は定義先と同じ環境をクロージャが参照することで成立します。

**`#f` だけが偽**です。0、空リスト、#t は真。boolean は数値ではなく、`(+ #t 1)` はエラー。`'()` は空のデータ、`()` の評価はエラー。if は選んだ枝だけを評価します。関数適用は演算子と引数を左から右に評価します。Symbol と string は別の型です。

```lisp
(begin
  (define make-adder (lambda (x) (lambda (y) (+ x y))))
  (define add10 (make-adder 10))
  (add10 3)) ; => 13
```

```sh
python3 examples/12-meta-evaluator/lisp.py examples/12-meta-evaluator/demo.lisp
```

UTF-8 スクリプト内の複数フォームを同じ大域環境で順番に評価します。demo は `計算結果: (120 13)` を出力したあと、最後の値 `(120 13)` を表示します。ファイル全体を先に解析するので構文エラーなら評価しません。実行時エラーの場合、既に起きた出力や定義は取り消しません。

追加: `list cons car cdr null? list? symbol? number? string? boolean? equal? length append set-car!`、`string-append symbol->string`、`display newline read-line read read-all apply error`、特殊形式 `set! while`。

- car/cdr は空リストならエラー。cdr/cons/append は新しい list を作ります。set-car! は第一要素を変更。標準 Scheme の pair / dotted list と同一ではありません。
- set! は既存の最も近い名前を変更します。while は条件と一つ以上の本文、最後の本文値を返し、0 回なら空リスト。
- 文字列は二重引用符。エスケープは改行、タブ、CR、引用符、バックスラッシュの5種。
- read は文字列から一つのフォーム、read-all はフォームのリストを読み、評価しません。
- read-line は EOF で #f。display は文字列の内容か値の読みやすい表現を出し、newline が改行します。apply は関数と引数リストを取ります。
- equal? は symbol と string、boolean と number を区別するデータ比較。数値比較 = とは別です。

マクロ、可変長仮引数、例外構文、モジュール、ファイル書き込み API、末尾呼び出し最適化は対象外。深すぎる再帰はエラーとして扱います。while の反復回数上限はありません。

## Lisp で書く評価器

```sh
python3 examples/12-meta-evaluator/lisp.py --meta --eval '(+ 1 (* 2 3))'
python3 examples/12-meta-evaluator/lisp.py examples/12-meta-evaluator/evaluator_starter.lisp
```

`evaluator.lisp` を Python host の Lisp でロードし、その m-eval に reader のデータを渡します。primitive は Python の組み込み算術・list・入出力への橋です。ソース式の評価全体を host evaluator に渡す関数ではありません。

`evaluator_starter.lisp` は自己評価される値だけを扱い、42 を返す実行可能な最小 starter。quote、次に算術適用を追加してください。
第12回の **meta 層** は数値、真偽値、文字列、四則、quote、if に限定。名前を保存する環境やクロージャはまだありません。Python host 層では第11回の機能を使えます。二つの対応範囲を混同しないことが演習の要点です。

## 検証

ルートで `python3 -m unittest discover -s tests -p 'test_languages.py' -v`。reader、算術、arity、環境、回復、host/meta 互換を確認します。
