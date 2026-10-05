# 第03回: 5ステップの挿絵設計（生成前）

実Claude Opus 5.5 / firstPartyによる設計です。実行278,432ms、CLI内部advisor claude-fable-5-1の利用記録もあります。画像生成・挿入は未実施です。

GPT Image 2.5の存在は[OpenAI公式の画像プロンプトガイド](https://developers.openai.com/api/docs/guides/image-prompting)で確認しました。一方、現在の組み込み生成ツールにはモデル指定引数や実モデルIDの返却がなく、指定モデルで実行したと照合できません。この画像工程だけ保留し、以下を次の生成・レビューの指示として保持します。本文・31ページの構成は固定です。

## 学習目標

最高気温の例でfor文を学び直す前に、5つの行為の分担を1枚で予告する。学生が疑問を持つ→手で予想する→AIからはヒントだけ受け取る→自分で照合する→自分の言葉で言い直す、という流れ。AIが関わるのは3の1コマだけで、残り4コマは学生の行為だと見て分かることが目的。装飾ではなく、LearningLoopと同じ色の約束(navy/teal=自分、amber=AI)で分担を示す。

## 挿入候補と紙面条件

p6『今日の例: 最高気温を求める』の『主例の highest.py と test_highest.py を…』の直後に、左揃えで <img> を1枚置く。表示は幅1024px・高さ180pxで、使える高さ(約454〜654px、約199px)に収まる。altは『学習相手にする5ステップ：1 言葉にする、2 予想する、3 AIに聞く、4 確かめる、5 言い直す』とし、steps配列の文字列をそのまま使う。合格条件は img.getBoundingClientRect().bottom ≤ 654、31ページのまま、本文の変更なし。投影で180pxでは小さすぎた場合は、p29まとめ(空き約300px)へ移す。p5は空き約60pxしかないので置かない。

## キャンバス

1536x1024で生成する(背景は透過PNGが使えれば透過、使えなければ #faf9f6 の平塗り)。y=377〜647の帯(1536x270)に5コマを1列で描き、上下の領域は無地にする。その帯を切り抜いて1024x180で表示する。各コマは約270x270、コマ間は約46px。各コマ内に8%(約22px)の安全余白をとり、帯の上下にも人物や物が切れない余白を残す。

## 構図

左から右へ1→5の順に5コマ。どのコマにも同じ学生(中性的、特定の人物に似せない)が描かれる。1: 机で考え込み、頭上に疑問の吹き出しがある。2: 紙に鉛筆で手書きで予想している。紙には抽象的な線だけを描き、キーボードは打っていない。3: ノートPCの横にamberの小さな吹き出しがあり、中身は電球マークのみ。学生はそれを読んでいて、コピーはしていない。4: 自分の手書きの紙と画面上の抽象的な出力を、虫眼鏡で見比べている。チェックマークも×印も付けない。5: 学生が自分の言葉で説明している(navyかtealの吹き出し、中身は抽象線)。手元には新しい小さなカードがある。1へ戻る矢印は画像に入れない(p5の図が担当する)。

## 画像内の文字

画像内には文字・数字・コード・UI・ロゴを一切入れない。1コマ目の疑問は、文字ではなく吹き出しの形と表情で表す。コマにキャプションは付けない。p6には余白が無く、p7〜p18の帯が各段の名前を示しているため。正確な日本語はaltとSlidev本文で担保し、新しい講義文言は作らない。

## 生成指示

```text
A single horizontal row of five equal square panels centered vertically on a 1536x1024 canvas, occupying only the band from y=377 to y=647; everything above and below is plain flat #faf9f6 empty background. Flat vector educational illustration, clean lines, limited palette: navy #154b74 and teal #087d80 for the student and their materials, light gray #f1f4f5 surfaces, amber #95620a with fill #fff5dc used ONLY for the AI element. The same gender-neutral university student appears in every panel, left to right: (1) sitting at a desk, puzzled, an empty thought bubble above the head; (2) writing a prediction by hand with a pencil on paper, paper shows only abstract squiggle lines; (3) looking at a laptop while a small amber speech bubble containing only a lightbulb icon floats beside it, the student is reading, not copying; (4) holding their handwritten paper next to the laptop and comparing the two with a magnifying glass, no check marks, no crosses; (5) explaining in their own words with a navy speech bubble of abstract lines, a small blank new card in hand. Absolutely no text, letters, numbers, digits, code, UI widgets, logos, or brand marks anywhere. No robot or humanoid AI, no AI handing over a document or code, no thumbs up. Generous inner margin in each panel, nothing touching panel edges.
```

## 意味・画素・投影の合格条件

1) 左→右が1→5の順になっている。2) 学生が5コマすべてに居る。AI要素(amber)は3コマ目にだけ1回現れ、中身はヒント記号のみ。3) 文字・数字・コード・ロゴ・偽の文字が混入していない(拡大して確認)。4) 完成コードや書類をAIから受け取る・貼り付ける描写が無い。5) 4コマ目に正解マークが無く、照合の行為として読める。6) 2コマ目は手書き。7) 手指の破綻が無い。8) 帯の切り抜き線上に物が無い。9) 1024x180の表示とp6の投影で、5つの行為が識別できる。10) 色の約束がp5の図(自分=navy、AI=amber)と一致している。11) DOMで下端が654以下、31ページのまま。
