# 第9回: 四則とREPL

このフォルダだけで実行できます。Python 3.12 以上、標準ライブラリのみを使います。Python を host にすること、この Lisp 方言の構文・真偽値・組み込み関数は**教材で選んだ設計**です。2026年シラバスが特定の処理系や方言を指定しているわけではありません。

## 実行

リポジトリのルートから:

```sh
python3 examples/09-lisp-arithmetic/lisp.py --eval '(+ 1 (* 2 3))'
python3 examples/09-lisp-arithmetic/lisp.py
python3 examples/09-lisp-arithmetic/starter.py --eval '(square 5)'
```

期待値は順に `7`、対話入力の結果、`25`。REPL は一行ごとに読みます。EOF または単独の `:quit` で終了し、不正な入力の後も次の行を受け付けます。複数行を補完するエディタはありません。成功終了は 0、--eval の言語エラーは 1、CLI 引数エラーは 2。

## reference と starter

- `lisp.py`: 完成 reference。Token → read_all → Interpreter.evaluate → Builtin の順に追います。
- `starter.py`: reference を読み込み square だけを追加した実行可能な拡張 starter。完成処理系の穴埋めではなく、小さな拡張を考える入口です。未実装の TODO はありません。変更する場所は starter.py の machine.add_builtin の第2引数である lambda x: number(x) ** 2 です。このコールバックを名前付き square 関数に置き換え、number で数値を確認した後に、負数なら LispError を送出する分岐を加えます。LispError も lisp から import してください。正常値とエラーを確認します。この square は host の拡張で、meta 利用者環境には自動登録されません。

## 機能と境界

四則の `+` と `*` は 0 個以上 (結果は `0` / `1`)、`-` と `/` は 1 個以上の数値を取ります。単項 `-` は符号反転、単項 `/` は逆数。数値は int / float、除算は実数。float の丸め誤差はあります。浮動小数の入力と演算結果は有限値だけを許し、Infinity / NaN を値として扱いません。指数表記が範囲を超える場合は read の言語エラー、演算結果の非有限値や int から float への変換 overflow は適用時の言語エラーです。整数は任意精度ですが、十進文字列の入出力は Python の桁数安全制限に従い、限界超過を LispError に変換します。コメントは `;` から行末。未知の名前、空の呼び出し、0 除算、括弧の不一致は LispError になります。読み取り器と評価器を分け、Python の eval / exec は使いません。
この段階は数値の評価だけです。quote、文字列、変数、関数、script CLI は後の段階。execute は一つのフォームだけを受け付けます。reader は将来の構文を読めても、未導入の機能の評価は拒否します。

## 検証

ルートで `python3 -m unittest discover -s tests -p 'test_languages.py' -v`。reader、算術、arity、環境、回復、host/meta 互換を確認します。
