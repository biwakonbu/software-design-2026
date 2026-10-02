# 第08回: 電卓を言語として実装する

Python 3.12 以上、標準ライブラリのみ。Python の利用とこの電卓の文法は教材の設計選択です。完成 reference は calculator.py、演習 starter は starter.py。

    python3 examples/08-calculator/calculator.py --eval '2 + 3 * (4 - 1)'
    python3 examples/08-calculator/starter.py

最初の期待値は 11。starter は 2 + 3 * 4 の AST と値を表示します。

tokenize → parse → AST → evaluate の段階を分けています。文法は expression = term ((+ | -) term)*、term = factor ((* | /) factor)*、factor = number | (+ | -) factor | (expression)。乗除は加減より優先、同じ優先順位では左結合。括弧と単項符号を扱います。数字は ASCII の 0–9 に限ります。整数・小数表記を読み、指数表記や非 ASCII の数字は対象外。不正文字は tokenize が検出する字句エラーです。空入力、括弧不一致、余剰トークンは parse が検出する構文エラーです。0 除算は構文解析に成功した AST を evaluate するときに検出する意味上のエラーです。

数値は float なので丸め誤差があります。変数・関数・文字列・べき乗は対象外。Python の eval / exec は使わず、自分で定義した AST の演算だけを評価します。

演習: starter の AST の根がなぜ Binary(+) か説明し、10 - 3 - 2 の左結合を AST で確認してください。その後 % を加えるなら、字句・構文・評価の変更点を先に列挙します。starter.py 自体には未実装の TODO はありません。実装コースでは自分の tokenizer/parser/evaluator を作り、拡張コースでは別コピーの calculator.py の tokenize・Parser・evaluate を変更します。どちらも同じ入出力とエラー段階を説明してください。完成 reference と提出する実装・拡張を区別します。

検証: ルートで python3 -m unittest discover -s tests -p 'test_languages.py' -v。
