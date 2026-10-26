# 依存関係の脆弱性修正（2026-10-27）

第05回完成版のcommit `da0fa045044e03332c1de6f90a92620bd62ccebf` を基準に、公式npm監査の12件を修復しました。監査を無効化せず、CIの `npm audit --audit-level=low` を保持しています。Slidev本体は53.0.0を維持しました。

## 対象と修正

| 対象 | 更新前 | 更新後・対策 |
| --- | --- | --- |
| DOMPurify | 依存3.4.16、Monaco内蔵3.4.15、Mermaid配布bundle内蔵3.4.12 | 3.4.17へ統一。Monacoの内部importを修正版へ解決し、Mermaidは外部依存を使う公式core入口へ切替 |
| markdown-it | 直接15.0.2、Slidev配下など14.3.2 | 15.0.3、14.3.3 |
| MCP server SDK | 2.2.0 | 2.4.0。不要なHTTP編集入口 `/__mcp` はSDKが入力を解析する前に403で拒否 |
| Vite | 8.3.2 | 8.3.5 |
| Zod | 4.6.5 | 4.6.7 |
| Mermaid / KaTeX | Mermaid12.1.0配下にKaTeX0.16.47 | Mermaid12.2.0の公式coreと、修正済みKaTeX0.18.10を使用。古い入れ子のKaTeXを削除 |

更新対象を指定した通常のnpm更新を行い、各親パッケージの互換範囲内でlockfileを更新しました。`npm audit fix --force` は使用していません。DOMPurifyとMermaidは共通Vite設定から直接参照するため、明示依存にしています。

## 影響条件と教材での扱い

- DOMPurifyの指摘は、shadow rootとテンプレート処理、IN_PLACEのhookで取り外した部分木、XHTMLとSMIL属性などの条件を伴います。MonacoとMermaidは配布ファイルにも古いコピーを内蔵するため、npmの依存解決だけで修復済みとは判定せず、ブラウザ内の実体と生成bundleも検査します。
- markdown-itには、HTML有効時の解析と、既定設定でも発生する未完結の複数行リンク定義の処理時間に関する指摘があります。冊子生成はHTML無効ですが、後者もあるため直接・推移依存を更新しました。
- MCPのHTTP共有server/transport、入力要素数、bearer tokenの宛先検査には、それぞれ構成上の条件があります。公式資料は一部対策について「更新だけでは有効にならない」と説明しています。Slidevの実装はリクエストごとにserver/transportを作りますが、この教材ではHTTP編集機能自体を使わないため、共通設定で入口を閉じました。stdioのCLI機能を新たに公開する変更はありません。
- Viteの指摘は、開発サーバーを公開する構成、特定のmiddleware、Windowsのエディター起動などが対象です。公式の修正版へ更新し、新しい外部公開設定は追加していません。
- Zodの指摘は、大きな配列などの不正入力に対する検証エラーの蓄積が対象です。
- KaTeXの指摘には、先行するprototype pollution、攻撃者の数式入力、別のsanitizerがないHTML挿入という条件があります。Mermaidの依存と配布入口を更新し、古い内蔵コピーを生成物へ取り込まないようにしました。

これらは生成環境・開発プレビュー・ブラウザ版Slidevで使うJavaScriptの修正です。配布PDFの閲覧時にNodeのSDKや開発サーバーが起動するわけではありません。教材のMarkdown、Pythonコード、演習、採点条件、共通CSS、図版は保持しています。

## 回帰検証

`npm run check:toolchain` を追加し、CIでも実行します。実Slidevに対するGET/POSTの6ケースでMCP拒否を確認し、Monacoの実importがDOMPurify3.4.17を使うことをブラウザ内で確認します。取り外された部分木のイベント属性が無効化されること、公式Mermaid coreで2頂点のグラフを描けること、既存の第05回の図が表示されることも検証します。

Mermaid coreのCommonJS依存は開発時の最適化を有効にします。静的buildだけが成功し、PDF出力時にdayjsなどが読み込めない状態を防ぐため、プレビューとPDF出力を両方確認します。

## 検証結果とPDF正本

- `npm ci --ignore-scripts` で依存を再現し、最終 `npm audit --json` は全severityで0件でした。
- Python3.12/3.14の既存213テストと互換性確認は両方成功しました。
- 新規JavaScriptの構文検査、全14講義の静的build、全14講義と2冊子のPDF生成が成功しました。個別のlint scriptはありません。
- 全570スライドを1280×720でブラウザ操作し、文字境界、コード幅、画像読込みと各回1→2の移動を確認しました。表示上の問題は0ページです。最終buildの実行用2092ファイルは、この検査に使ったものとbyte一致しました。
- 新しい静的bundleに含まれるDOMPurifyは3.4.17だけで、古い内蔵版やKaTeX0.16.47は取り込まれていません。
- 全16冊・677ページをPNGへ描画し、676ページは以前の正本PDFの描画とbyte一致しました。差分の1ページと、第05回の循環・変数名・経路復元・演習境界例などの実画像を確認し、文字切れ・重なり・コードの読みにくさはありませんでした。

教師用冊子の15ページには、既存原稿 `instructor/06.md` が「全ページ」なのに旧PDFが「25ページ」のままという生成物のずれがありました。原稿を変更せず、43ページの新しい冊子PDFを保存し、manifestの該当1項目を更新しています。それ以外の15冊は、再生成結果の表示一致を確認したうえで既存正本のbyteを保持しました。第05回も67ページ、SHA-256 `89563cee6246d9f2e588801295449b991a20636505dc4c5fcfc80cb5874666e9` を維持しています。

headlessブラウザのWake Lock権限エラーと、改修前にも記録されていたFloatingVueの警告は残ります。前者は全ページ共通の実行環境上の制約で、表示・移動・PDF生成は成功しています。コンソールにエラーがないという判定にはしていません。

## 公式資料

- DOMPurify: [shadow root](https://github.com/advisories/GHSA-cg2g-xh64-v4q7)、[取り外した部分木](https://github.com/advisories/GHSA-mrv2-3pqr-j5jr)、[XHTML/SMIL](https://github.com/advisories/GHSA-c6gr-qvv4-5v3f)
- markdown-it: [HTML解析](https://github.com/advisories/GHSA-vfgh-jcmw-g37q)、[複数行リンク定義](https://github.com/advisories/GHSA-gfr2-rv44-r23c)
- MCP: [共有instance](https://github.com/advisories/GHSA-jm63-cq47-j5jp)、[入力要素数](https://github.com/advisories/GHSA-46jr-4wx8-v453)、[token宛先](https://github.com/advisories/GHSA-rvq5-wwqv-78pq)
- Vite: [Windowsの%展開](https://github.com/advisories/GHSA-698v-4r3x-3vcv)、[エディター引数](https://github.com/advisories/GHSA-r825-w8mm-5pxw)、[存在確認](https://github.com/advisories/GHSA-587h-7wmj-h5pm)、[middleware](https://github.com/advisories/GHSA-9jrq-w75r-8gcw)、[fs.allow](https://github.com/advisories/GHSA-rq7h-c2jc-7f22)、[Wasm読込み](https://github.com/advisories/GHSA-vfpm-58rq-9qcg)
- [Zod](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5)、[KaTeX](https://github.com/advisories/GHSA-238p-pmpm-9mq7)
- [Viteの依存最適化](https://vite.dev/config/dep-optimization-options)
