# 全回の学習・図・表示の完成記録

本人の2026-10-06の全体調整依頼に基づき、第03回31ページ（基準commit dcee23f）を固定し、第04〜15回を完成しました。リポジトリを正本とし、ZIP/Libraryは更新していません。第02回60ページは既存の表示と内容を保持しました。

各回の到達目標に沿って「説明→自分で予想/操作→確かめる→自分で説明/別入力へ応用」をつなぎました。実Opus5.5の設計からCodexが図を実装し、元のコード・図の途中状態・実行結果を同じ例で照合しています。完成回への追加任意改善は行っていません。

| 回 | PDF頁数 | 完成commit・PDF | レビュー |
|---|---:|---|---|
| 04 | 47 | [PDF・`f68adc6`](https://github.com/biwakonbu/software-design-2026/blob/f68adc6917e170d7670a645d76d46bed8f1e9f12/output/pdf/04-algorithms.pdf) | [実画面・コード照合](lesson04-visual-review.md) |
| 05 | 28 | [PDF・`a4e5089`](https://github.com/biwakonbu/software-design-2026/blob/a4e5089331baa47282b2cbbc506028b4032a9169/output/pdf/05-graphs.pdf) | [実画面・コード照合](lesson05-visual-review.md) |
| 06 | 26 | [PDF・`078f4e9`](https://github.com/biwakonbu/software-design-2026/blob/078f4e9e31d648bbe2e7ed46b409344c9a735b40/output/pdf/06-route-project.pdf) | [実画面・コード照合](lesson06-visual-review.md) |
| 07 | 27 | [PDF・`c761e73`](https://github.com/biwakonbu/software-design-2026/blob/c761e7300425a84725d05c553ebd1d6fc6a3e403/output/pdf/07-review.pdf) | [実画面・コード照合](lesson07-visual-review.md) |
| 08 | 40 | [PDF・`fa4a840`](https://github.com/biwakonbu/software-design-2026/blob/fa4a84024d9eaf77dfbc34d3f8e0b66b2f1bc23a/output/pdf/08-calculator.pdf) | [実画面・コード照合](lesson08-visual-review.md) |
| 09 | 29 | [PDF・`428b947`](https://github.com/biwakonbu/software-design-2026/blob/428b9479ecd589aad4a21d0647b175d4c2c5fa62/output/pdf/09-lisp-arithmetic.pdf) | [実画面・コード照合](lesson09-visual-review.md) |
| 10 | 40 | [PDF・`919abc1`](https://github.com/biwakonbu/software-design-2026/blob/919abc13221ce2da87d557ca7c75e25822d3fef4/output/pdf/10-lisp-functions.pdf) | [実画面・コード照合](lesson10-visual-review.md) |
| 11 | 38 | [PDF・`a64a869`](https://github.com/biwakonbu/software-design-2026/blob/a64a8695c852283aaa24048ec2035775d9edb7d7/output/pdf/11-lisp-scripts.pdf) | [実画面・コード照合](lesson11-visual-review.md) |
| 12 | 39 | [PDF・`b7a64e4`](https://github.com/biwakonbu/software-design-2026/blob/b7a64e4840df8f92a8c24e4205447b0f6111dfb5/output/pdf/12-meta-evaluator.pdf) | [実画面・コード照合](lesson12-visual-review.md) |
| 13 | 28 | [PDF・`3a6854d`](https://github.com/biwakonbu/software-design-2026/blob/3a6854d5c1eac0b0dd86e9820364c13900467587/output/pdf/13-language-review.pdf) | [実画面・コード照合](lesson13-visual-review.md) |
| 14 | 45 | [PDF・`2210cb3`](https://github.com/biwakonbu/software-design-2026/blob/2210cb3d0c2abe1297dac034fe7c188008b09a8c/output/pdf/14-selfhosting.pdf) | [実画面・コード照合](lesson14-visual-review.md) |
| 15 | 28 | [PDF・`075701f`](https://github.com/biwakonbu/software-design-2026/blob/075701fb717fbb13e32acab42443e3ca5de74dc3/output/pdf/15-showcase.pdf) | [実画面・コード照合](lesson15-visual-review.md) |

第04〜15回の全415ページを描画し、実画面で確認しました。独立Opusは初回に各回の全ページを画像で読み、修正後は変更ページを再確認しています。変更外ページは画素照合で保護しました。全ページの実Slidev範囲・可視図数・キー移動、図の節点/ラベル/別辺との干渉・矢印・所属距離も検査しました。本文/図28px・コード26pxを基本とし、投影とPDF自習の読み順・余白を確認しています。第02/03回、別冊、既存サンプル・演習・提出/必須/発展/採点条件、既存画像を保持しました。原本92ファイルと依存監査gateは基準SHA一致です。

今回の図設計に生成画像指示はなく、第04〜15回で新規imagegenを実行していません。既存画像を保持してコード・図との意味を確認しています。指定画像モデル名を実行済みモデルとして記録していません。Codexの実モデル設定は実行環境で確認できないため、指定名を検証済みの実行名として記録していません。Opusの実呼出しはclaude-opus-5-5 / firstParty、内部advisor claude-fable-5-1の使用がある記録も保持しています。

[公開Gist一覧とSHA](gist-samples.md)は第03/04/05/08/09/10〜11回です。第10/11回は一つのセットで重複を避けています。本人所有public、保存後の全ファイルをreadbackし、Python3.12.13/3.14.7で正常・境界・失敗、期待出力・出力先・終了コードを照合しました。有限の検証範囲と実装制約を各GistのREADMEに明記し、未公開資料・学生情報・教員専用解答・既存非公開Gistを転載していません。

全14回の静的Slidevビルド、14スライドPDFの原稿ページ数照合と16PDF・613ページの描画エラー検査、PDF-manifestの全バイト数/SHAは合格しました。両Pythonで既存回帰213件・互換fixture15件、各図の実行照合と公開用テストが合格しています。共通runner1.1.0の21件は合格、大学profileで56ファイルから482抽出文書を新規出力しました。新規jaio診断の実行とは記録しません。旧文章構造検査は第10〜15回のページ・図・表・リンクの意図差分を報告し（意図差分を含むため判定はfalse）、欠落・許可外変更は0件でした。

各回を個別commit/pushし、GitHub mainのSHAとPDF全バイトを読戻しました。第04〜15回のGitHub ActionsはPython3.12/3.14 jobsが成功し、exportsは既存bracesのGHSA-vfj7-8cjw-p6xmでnpm auditが停止しています。遠隔のPDF再生成成功とは記録せず、ローカルPDF/Slidev検証と区別します。依存監査を弱めていません。

[機械照合の記録](course-rollout-verification.json)に、各回のcommit・PDF SHA・Actions URLと検証件数を収録しています。
