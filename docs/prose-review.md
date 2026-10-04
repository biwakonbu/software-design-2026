# 教材文章レビュー手順

文章の自然さと、授業で使える教材の契約を合わせて確認します。共通 [jaio runner 1.1.0](../tools/material-prose/README.md) は候補の発見に使い、改稿・意味・余白の判断は原文と実表示で行います。Codex用の入口は [material-prose-review](../.agents/skills/material-prose-review/SKILL.md) です。

## 対象を確定する

納品commit、本人の未コミット変更、対象ファイルと保護対象を記録し、作業版へ分けます。今回の基準は `359c59a`、第03〜15回の講義・演習・教師補足・独立READMEです。第02回の既存60スライドと対応ソース・コード・PDF・プレビューは保持します。授業の指定が変わった場合は新しい範囲を明示します。

読み手は学生と教師です。丁寧な説明体を基本とし、操作指示は対象と行動を短く伝えます。用語はコードと対応させ、初出の説明と後の表記を揃えます。到達目標、図中ラベル、表の短句まで機械的に長い敬体へ変えません。

| 候補 | 判断すること |
| --- | --- |
| 冗長な説明・フィラー | 同じ理由を近くで繰り返していないか。理解に必要な理由は残す |
| 長い文・曖昧な指示 | 操作対象、前提、成功条件が読めるか。条件の範囲を変えず分ける |
| 資料間の重複 | 復習・定義・問題/解答・本/スライドの対応・独立実行に必要か |
| 文体の揺れ | 説明、指示、ラベル、引用という役割の違いか |
| 余白と改ページ | 文字や図が詰まりすぎていないか。見出し、コード、表、末尾行が分断されていないか |

## 解析と改稿

改稿前後を同じrunner・設定・バイナリで別の出力先へ解析します。`manifest.json` と実ソースのSHAを照合します。`latest` など版が異なる先行結果を前後比較に混ぜません。

学生演習全文、設問・解答・契約・コード・引用・表は抽出から除外されます。除外部分も、原文の全文レビューと他媒体との対応確認を行います。解析完了を56ファイルの全文評価と説明しません。

候補ごとに採用、必要な再掲、誤検出、保護対象への別提案を記録します。類似度や警告数を下げる目的で復習や独立READMEを削らず、閾値も変更しません。問題と解答の整合、数値・難度、必須/発展、授業配分、提出・採点の条件を保ちます。

意味に関わる改稿には、依頼者が指定した正式モデルの実行を用い、モデルID・provider・結果を記録します。今回の指定は `claude-opus-5-5` です。実行記録の `modelUsage` を確認し、失敗や代替モデルを正式モデルの成功として扱いません。認証情報は保存しません。

提案は現在の原文へ一意に一致する差分で適用します。独立レビューで、条件の必須化、成功の断定、API/CLI・数値・意味の変化がないことを確認します。人の新しい編集があればその本文を基準に再確認します。

## 保護契約と回帰

次は既存のローカルcommitを読み取り、現原稿と比較します。ネットワークやGitの変更は行いません。

```sh
python3 scripts/check-prose-contracts.py --base-ref 359c59a
```

今回、静的Slidevの第10・14回の教師補足/演習リンクを配布するため、`scripts/build-slides.mjs` の公開Markdownコピーを追加しました。冊子の相対参照が一時的なlocalhostへ向く問題も、`scripts/export-workbooks.mjs` で公開リポジトリへのリンクに変換しました。元Markdown、書体・余白、課題コードは保持し、両差分を独立レビューしました。比較時は根拠を記録して明示します。

```sh
python3 scripts/check-prose-contracts.py --base-ref 359c59a \
  --allow-tooling scripts/build-slides.mjs \
  --allow-tooling scripts/export-workbooks.mjs
```

作業版がcommit objectを持たない場合は、既存納品checkoutを `--baseline-dir` へ渡せます。出力を保存する `--out` は両入力ツリーの外にある新しいファイルを指定します。既存ファイルは上書きしません。

保護照合は第02回の全既存ファイル、既存コード・スタイル・設定・Library metadata、56教材のコード枠/inline code/見出し/スライド境界/表/引用/HTML/リンク/数値トークンを確認します。数値トークンの一致だけでは意味の一致を証明できません。新規ファイルも別にレビュー・公開検査してください。

```sh
python3.12 -m unittest discover -s tests -v
python3.14 -m unittest discover -s tests -v
python3.12 -m unittest discover -s tools/material-prose/tests -v
python3.14 -m unittest discover -s tools/material-prose/tests -v
python3.12 examples/15-showcase/check_compatibility.py
python3.14 examples/15-showcase/check_compatibility.py
python3 scripts/check-public.py
```

## PDF・Slidevの確認

第03〜15回の講義PDFと両冊子を生成し、第02回PDFのSHAが基準と同じであることを確認します。全講義のページ数を公式Slidev parserと照合します。

```sh
node scripts/export-pdfs.mjs 03 04 05 06 07 08 09 10 11 12 13 14 15
node scripts/export-workbooks.mjs
python3 scripts/render-pdfs.py --destination tmp/pdf-qa --scale 1600
node scripts/build-slides.mjs
```

全ページの画像を実際に開いて確認します。見本だけで全ページ目視済みとせず、確認したページ・PDFのSHA・所見・修正後の再確認を記録します。本文、コード、図、表、字形、フッターに加え、適切な余白、語の分断、見出しの孤立、段落末尾だけのページを見ます。固定した書体や字の大きさを下げる前に、説明の整理で解消できるか検討します。

実Slidevでも全ページの移動・図・表示・フッターを確認し、本文の参照リンクが配布物から開くことを確かめます。元Markdownのローカルパス、冊子の章順とPDFリンク、外部資料の到達性も確認します。ブラウザの並行QAが競合する場合はローカル描画を先に進めます。

機械的なbounds、DOMの行箱、文字数だけで可読性や美観を合格にしません。保守的な余白警告も実字形の重なりと分けて記録します。PDFを再出力したら変更ページを再目視し、他ページを画素比較することで最終版への対応を確認できます。

検証結果は [verification.md](verification.md) と `pdf-manifest.json` へ残します。前納品版を上書きせず、解析結果の個人パス・認証情報を公開物へ入れません。pushや既存Library IDの新versionへの更新は、その操作の承認範囲を別に確認します。
