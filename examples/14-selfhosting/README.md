# 第14回: Lisp製評価器とREPL

このフォルダだけで実行できます。Python 3.12 以上、標準ライブラリのみを使います。Python を host にすること、この Lisp 方言の構文・真偽値・組み込み関数は**教材で選んだ設計**です。2026年シラバスが特定の処理系や方言を指定しているわけではありません。

## 実行

リポジトリのルートから:

```sh
python3 examples/14-selfhosting/lisp.py --eval '(+ 1 (* 2 3))'
python3 examples/14-selfhosting/lisp.py
python3 examples/14-selfhosting/starter.py --eval '(square 5)'
```

期待値は順に `7`、対話入力の結果、`25`。REPL は一行ごとに読みます。EOF または単独の `:quit` で終了し、不正な入力の後も次の行を受け付けます。複数行を補完するエディタはありません。成功終了は 0、--eval の言語エラーは 1、CLI 引数エラーは 2。

## reference と starter

- `lisp.py`: 完成 reference。Token → read_all → Interpreter.evaluate → Env / Closure の順に追います。
- `starter.py`: reference を読み込み square だけを追加した実行可能な拡張 starter。完成処理系の穴埋めではなく、小さな拡張を考える入口です。未実装の TODO はありません。変更する場所は starter.py の machine.add_builtin の第2引数である lambda x: number(x) ** 2 です。このコールバックを名前付き square 関数に置き換え、number で数値を確認した後に、負数なら LispError を送出する分岐を加えます。LispError も lisp から import してください。正常値とエラーを確認します。この square は host の拡張で、meta 利用者環境には自動登録されません。

## 機能と境界

四則の `+` と `*` は 0 個以上 (結果は `0` / `1`)、`-` と `/` は 1 個以上の数値を取ります。単項 `-` は符号反転、単項 `/` は逆数。数値は int / float、除算は実数。float の丸め誤差はあります。浮動小数の入力と演算結果は有限値だけを許し、Infinity / NaN を値として扱いません。指数表記が範囲を超える場合は read の言語エラー、演算結果の非有限値や int から float への変換 overflow は適用時の言語エラーです。整数は任意精度ですが、十進文字列の入出力は Python の桁数安全制限に従い、限界超過を LispError に変換します。コメントは `;` から行末。未知の名前、空の呼び出し、0 除算、括弧の不一致は LispError になります。読み取り器と評価器を分け、Python の eval / exec は使いません。
追加の特殊形式: `define lambda if quote begin`。比較 `= < >` と `not`。`'x` は `(quote x)` の短縮です。関数定義は `(define f (lambda (x) ...))` で、`(define (f x) ...)` の省略形はありません。lambda は重複しない固定個数の仮引数と一つ以上の本文を取ります。定義時の環境を捕捉する字句スコープ。再帰は定義先と同じ環境をクロージャが参照することで成立します。

**`#f` だけが偽**です。0、空リスト、#t は真。boolean は数値ではなく、`(+ #t 1)` はエラー。`'()` は空のデータ、`()` の評価はエラー。if は選んだ枝だけを評価します。関数適用は演算子と引数を左から右に評価します。Symbol と string は別の型です。

```lisp
(begin
  (define make-adder (lambda (x) (lambda (y) (+ x y))))
  (define add10 (make-adder 10))
  (add10 3)) ; => 13
```

```sh
python3 examples/14-selfhosting/lisp.py examples/14-selfhosting/demo.lisp
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
python3 examples/14-selfhosting/lisp.py --meta --eval '(+ 1 (* 2 3))'
python3 examples/14-selfhosting/lisp.py examples/14-selfhosting/evaluator_starter.lisp
```

`evaluator.lisp` を Python host の Lisp でロードし、その m-eval に reader のデータを渡します。primitive は Python の組み込み算術・list・入出力への橋です。ソース式の評価全体を host evaluator に渡す関数ではありません。

`evaluator_starter.lisp` は自己評価される値だけを扱い、42 を返す実行可能な最小 starter。quote、次に算術適用を追加してください。

meta 層にも define/lambda/字句クロージャ/再帰/if/quote/begin/set!/while を Lisp で実装しています。環境は `(frame-cell parent)`、束縛は `(name value)`、クロージャは `(closure params body captured-env)`。define/set! は共有セルの束縛リストを入れ替えます。cdr はコピーなので、束縛の cdr を変更するだけでは環境を更新できない点に注意してください。

特殊形式の分岐、引数評価、名前検索、クロージャ適用は evaluator.lisp にあります。meta の apply は meta クロージャを理解するよう Lisp で特別扱いします。guard/primitive/trace-event は host 支援 API で、meta 利用者環境には公開しません。内部のタグ付きリストを偽造した場合の防御や、関数値の同一性比較は互換性対象外です。循環する環境を展開せず、meta クロージャは `<meta-closure>` と表示します。

## 二層の診断

```sh
python3 examples/14-selfhosting/lisp.py --trace --meta --eval '((lambda (x) (+ x 1)) 4)'
```

標準出力は 5。標準エラーの `[host depth=...]` は Python host が Lisp 実装を評価する過程、`[meta depth=...]` は Lisp 実装が利用者プログラムを評価する過程。host の深い評価とロード時の定義を省略します。meta depth はソース式の入れ子を追う値で、Python のスタック深さではありません。

`review_cases.json` の6ケースについて、期待値やエラーの理由を先に説明してから host / meta の両方で確認してください。診断全文ではなく、結果とエラー分類を比較します。

## Lisp 製 REPL

```sh
python3 examples/14-selfhosting/lisp.py --selfhost-repl
printf '(+ 1 2)\n(/ 1 0)\n(+ 3 4)\n:quit\n' | python3 examples/14-selfhosting/lisp.py --selfhost-repl
```

順に 3、error: division by zero、7 と出し、終了します。`repl.lisp` が read → m-eval → print、終了条件、エラー後の継続を定義します。一行ごとに read-all し、空行・コメントも扱います。評価と結果表示を guard の中で実行するので、巨大整数が表示の桁数制限を超えても次の入力へ進みます。guard は LispError を捕捉して `(成功? 値またはメッセージ)` を返す host 支援。この REPL のエラー表示は通常出力です。

達成するのは **同じ言語で書いた評価器を、その言語の処理系上で動かすこと**。ネイティブ bootstrap、Python から独立したバイナリ、host を取り除いた処理系は達成していません。read/read-all の字句・構文解析、算術/list primitive、read-line/display/newline、guard、while の反復機構は Python host に依存します。式の意味を決める評価の核心は Lisp 側です。どの処理をどの層が担当するかを二層トレースで説明してください。

## 検証

ルートで `python3 -m unittest discover -s tests -p 'test_languages.py' -v`。reader、算術、arity、環境、回復、host/meta 互換を確認します。
