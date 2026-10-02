# 出典とフォント

新作の本文・図・架空データ・コードを用いている。2026年度シラバスと本人の過年度教材を制作の要件として確認したが、原ファイル・抽出全文・コード画像・第三者図版・連絡先・学生の回答や採点結果は公開しない。

## 公式の参考文書

- [Python 3.12 チュートリアル](https://docs.python.org/3.12/tutorial/)
- [Python 3.12 組み込み型](https://docs.python.org/3.12/library/stdtypes.html)
- [Python 3.12 collections](https://docs.python.org/3.12/library/collections.html)
- [Python 3.12 unittest](https://docs.python.org/3.12/library/unittest.html)
- [Python 3.12 re](https://docs.python.org/3.12/library/re.html)
- [Python 3.12 浮動小数点の問題と制限](https://docs.python.org/3.12/tutorial/floatingpoint.html)
- [SlidevのPDF出力](https://sli.dev/guide/exporting.html)

アルゴリズムは教材の小さな問題に合わせて実装した。Lispは教材独自の小さな方言であり、特定文書のコードを転載したものではない。一般的な言語の考え方と、この処理系の仕様を区別する。

## フォント

- Noto Sans JP: @fontsource/noto-sans-jp 5.3.0、SIL Open Font License 1.1。[原ライセンス](LICENSE-NotoSansJP.txt)。
- JetBrains Mono: @fontsource/jetbrains-mono 5.3.0、SIL Open Font License 1.1。[原ライセンス](LICENSE-JetBrainsMono.txt)。

フォントはnpmのローカル依存から読み込む。PDFには使用する字形を埋め込む。外部のフォント配信サーバーへ依存しない。フォントそのものを独自のライセンスに変更しない。

Slidevなどの依存パッケージのライセンスは各パッケージに含まれるものを保持する。新作教材全体の包括的な再利用ライセンスは未指定であり、依存のライセンスと混同しない。
