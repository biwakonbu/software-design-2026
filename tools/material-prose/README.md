# 教材文章検査

[co-routine/jaio](https://github.com/co-routine/jaio) を使う共通 runner **1.1.0** を再利用しています。スクリプト、共通設定、2つの教材profile、21件の回帰テストは共通版と同一です。大学教材には `university` を指定してください。`bootcamp` profileは共通回帰との互換性を保つため収録しています。

説明文を抽出する読み取り専用の検査です。文体・用語・長文・重複の候補を原文の行へ対応付けます。問題、解答、仕様、コード、引用、表は検査対象から保護します。学生演習14ファイルも全文を除外するため、全文レビューには [教材文章レビュー手順](../../docs/prose-review.md) を併用してください。

## 実行

Python 3.9以上、macOS、検証済みjaio 0.9.4の既存バイナリを使用します。`configs/jaio-provenance.json` にsource commit・バイナリSHAを固定しています。個人のローカルパスは収録せず、実行時に `JAIO_BIN` を指定します。バイナリが固定SHAと異なる場合は検証後にpinを更新し、変更根拠を残してください。

リポジトリのルートから、未作成で入力ツリーの外にある出力先を指定します。

```sh
python3 -m unittest discover -s tools/material-prose/tests -v

python3 tools/material-prose/scripts/material_prose.py run \
  --profile university --root . \
  --out /tmp/software-design-2026-prose-before-YYYYMMDD \
  --jaio "$JAIO_BIN"
```

改稿後も同じ版・設定で実行し、別の未作成出力先へ保存します。出力済みディレクトリや入力ツリー内への出力は拒否します。抽出のみなら `run` を `extract` に置き換え、`--jaio` を省略できます。

jaioはmacOSの `sandbox-exec` でネットワークを禁止して実行します。既存sandbox内でその起動がOSに拒否された場合は、同じコマンドを実行環境の承認レビューへ渡します。ネットワーク禁止を外した再試行は行いません。インストール、Cargoビルド、認証設定、Git操作、外部LLM呼び出しは行いません。

## 結果

- `manifest.json`：入力版、SHA、抽出範囲と保護範囲。
- `jaio.toml`：実際に適用した全設定。
- `jaio.raw.json`：jaioの元診断。
- `jaio.corpus.json`：公式dumpによる全類似ペア。
- `report.json`：原文の位置へ戻した候補、計測値、実行根拠。
- `corpus/`：検査専用の抽出物。教材の正本ではありません。

`analysis_complete` は抽出した対象の解析完了を表します。`completion_status` は `human_review_required` です。元ソースや抽出物が途中で変わった場合、検査は失敗します。通常checkの重複診断件数と公式dumpの一意なペア数は異なるので、全ペアを確認してください。

大学は和文80字・読点なし60字を長文確認の起点にします。ASCIIはjaioの長文文字数から除かれます。記事向けの自己体験・過去形・記事字数の規則を教材へ持ち込まず、note向けlintのコード/引用保護、候補と人の判断の分離、fixture回帰を応用しています。

`material/repeated-block` と `material/ambiguous-instruction` は共通runnerの補助検査です。jaioの公式機能とは区別します。リンク、PDF組版、図の意味、学習上の必要な再掲はこの解析だけでは判定できません。結果には教材本文とローカル入力パスが含まれるため、公開ZIPへ解析出力をそのまま入れないでください。
