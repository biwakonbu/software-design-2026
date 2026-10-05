# 第03回: 学生の5つの学習行為を示す挿絵

本人の指示により、実Opus 5.5の設計・Codex向け指示から、Codexの組み込み画像生成、実画像確認、教材への挿入を実施しました。画像のbackendモデルIDは返却されていないためunknownです。GPT Image 2.5で実行したと照合できたという記録にはしません。本文・31ページの構成は保持しています。

## 学習目標

同じ学生が、疑問を持つ、手で予想する、AIからヒントを読む、自分の紙と画面を照合する、自分の言葉で説明する、という5つの行為を左から右へ行います。完成コードを受け取る描写はなく、AIのヒントだけをamberで示します。正確な5ステップの文言と数値・コードは既存本文と編集可能な図が担保します。

## 実施した工程

既存の実Opus 5.5設計（278,432ms、CLI内部advisor claude-fable-5-1を含む）を再利用しました。実Opus 5.5 / firstPartyが29,455msでCodex6.1Sol宛ての具体的な生成指示を作成しました。この実行にはOpus 5.5のみが記録されています。宛先の指定と画像backendの実識別は別に扱っています。

その指示を受けてCodexが組み込みimagegenを1回呼びました。初稿の小物の欠けと色を実画像で確認し、同じimagegenを1回使って編集しました。初稿・改訂画像の原本は保持しています。画像をコードや別の加工ツールで切り抜いたりリサイズしたりしていません。

## 最終の挿入

[最終画像](../lectures/assets/illustrations/learning-five-actions.png)の実寸は2117×743pxです。生成指示より縦の大きい比率になったため、元設計の代替候補だったp29「まとめと次回」へ挿入しました。実Opusが原寸画像とp29を24,264msで直接読んで合格し、幅840px・比例縮小・切り抜きなしの配置をCodexへ指示しました。p6の文章は変更していません。

表示は840×294.81px、左端50px、上端335.66px、下端630.47pxです。フッター罫線667pxとの間は約36.5pxあります。全画像が見え、CSSの固定高さや内部切り取りに依存しません。altは「学習相手にする5ステップ：1 言葉にする、2 予想する、3 AIに聞く、4 確かめる、5 言い直す」です。

## 意味と実紙面の確認

独立contextの実Opus 5.5 / firstPartyが完成PDFのp29、原寸画像、既存p5の5ステップ図を直接読み、31,588msで合格しました。文字・コード・値・誤った承認記号・robot・完成答案の受け渡しは画像にありません。手指と5つの姿勢の違い、紙・PC・吹き出しの全体表示を確認しました。PCの画面の向きと薄い背景色の差には軽微な所見があり、意味・判読性・見切れに影響しないため必須修正ではありません。

紙面に収まるDOM値、PDF全31ページのテキスト保持、他30ページの画素一致、他15PDFのbyte保持、配布版の画像読み込みは別検査で確認しています。レビューの画像からの投影判読性評価を、実教室での投影実験とは記載していません。

画像SHA-256: `b50416152a50471accb16eca2d0472eacd5fd103648ee45623c53d5e5abe9683`。公開検査にはこの1パス・1SHAだけを追加し、未知の画像と内容変更は引き続き失敗します。

## 実OpusからCodexへの生成指示

```text
Wide panoramic banner, aspect ratio 1536x270 (about 5.7:1), landscape, the whole canvas is the content band with no extra empty space above or below. Plain flat #faf9f6 background. A single horizontal row of five equal square panels, each about 270x270, separated by gaps of about 46 px, read left to right as steps 1 to 5. Leave about 8% safe margin inside every panel and keep every figure, object and bubble fully inside its panel; nothing touches or is cut off at the top, bottom, left or right edges of the canvas. Flat vector educational illustration, clean lines, limited palette: navy #154b74 and teal #087d80 for the student, their clothes, pencil, paper and materials; light gray #f1f4f5 for surfaces such as desk and laptop; amber #95620a with fill #fff5dc used ONLY ONCE in the entire image, for the single AI hint bubble in panel 3. No other amber, orange or yellow anywhere. The same gender-neutral university student, not resembling any real person, appears in all five panels. (1) The student sits at a desk looking puzzled, an empty rounded thought bubble above the head; the question is shown only by the bubble shape and the facial expression, no question mark. (2) The student writes a prediction by hand with a navy pencil on a sheet of paper; the paper shows only abstract squiggle lines; hands are on the pencil and paper, not on a keyboard. (3) The student sits in front of a laptop whose screen is plain light gray, and reads a small amber speech bubble floating beside the laptop that contains only a simple lightbulb icon; the student is reading, not copying, not typing, not receiving any document. (4) The student holds their own handwritten paper next to the laptop and compares it with a few abstract gray lines on the laptop screen using a magnifying glass; no check marks, no crosses, no ticks, no stars, no approval symbols. (5) The student explains in their own words with a navy speech bubble filled with abstract lines, holding a small blank new card in the other hand. No arrow back to the first panel and no arrows between panels. Absolutely no text, letters, numbers, digits, captions, panel labels, code, UI widgets, window chrome, buttons, logos or brand marks anywhere, including on the paper, card and laptop. No robot or humanoid AI, no AI handing over a document or code, no copy-paste gesture, no thumbs up. Natural, correctly formed hands with five fingers. Minimal decoration, no background scenery.
```
