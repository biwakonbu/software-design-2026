<script setup>
import { useId } from 'vue'
defineProps({ kind: { type: String, required: true } })
const markerId = `py-arrow-${useId()}`
</script>

<template>
  <div class="study-diagram">
    <svg viewBox="0 0 600 360" role="img" :aria-label="`Pythonの${kind}図解`" :style="{ '--py-arrow-marker': `url(#${markerId})` }">
      <defs><marker :id="markerId" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#087d80" /></marker></defs>
      <g v-if="kind === 'binding'">
        <text x="20" y="38" class="label">① b = a の直後</text>
        <rect x="24" y="67" width="120" height="60" class="name"/><text x="68" y="108" class="mono">a</text>
        <rect x="24" y="150" width="120" height="60" class="name"/><text x="68" y="191" class="mono">b</text>
        <path d="M144 97 L315 124" class="arrow"/><path d="M144 180 L315 142" class="arrow"/>
        <rect x="330" y="100" width="210" height="72" class="value"/><text x="350" y="147" class="mono">[200, 120]</text>
        <text x="24" y="260">名前は2つ、リストは1つ。</text>
        <text x="24" y="305">bからの変更をaからも読める。</text>
      </g>
      <g v-else-if="kind === 'rebind'">
        <text x="20" y="38" class="label">② a = a + 1 の後</text>
        <rect x="24" y="73" width="120" height="60" class="name"/><text x="68" y="114" class="mono">a</text>
        <rect x="24" y="163" width="120" height="60" class="name"/><text x="68" y="204" class="mono">b</text>
        <path d="M144 103 L315 103" class="arrow"/><path d="M144 193 L315 193" class="arrow"/>
        <rect x="330" y="70" width="160" height="65" class="value"/><text x="393" y="115" class="mono">3</text>
        <rect x="330" y="160" width="160" height="65" class="value"/><text x="393" y="205" class="mono">2</text>
        <text x="24" y="280">整数2を書き換える処理ではない。</text>
        <text x="24" y="325">aだけが別の整数3を指す。</text>
      </g>
      <g v-else-if="kind === 'loop'">
        <text x="20" y="38" class="label">各要素を1つずつ受け取る</text>
        <rect x="22" y="63" width="540" height="65" class="value"/>
        <text x="76" y="107" class="mono">200</text><text x="251" y="107" class="mono">120</text><text x="444" y="107" class="mono">80</text>
        <path d="M192 64 L192 128 M382 64 L382 128" class="line"/>
        <path d="M113 134 L113 186" class="arrow"/><path d="M290 134 L290 186" class="arrow"/><path d="M463 134 L463 186" class="arrow"/>
        <text x="58" y="231" class="mono">0+200</text><text x="228" y="231" class="mono">200+120</text><text x="428" y="231" class="mono">320+80</text>
        <text x="75" y="279" class="label mono">200</text><text x="253" y="279" class="label mono">320</text><text x="441" y="279" class="label mono">400</text>
        <text x="22" y="335">前回のtotalを次の計算に使う。</text>
      </g>
      <g v-else-if="kind === 'indices'">
        <text x="20" y="38" class="label">位置を示す整数が添字</text>
        <text x="82" y="106" class="mono">0</text><text x="275" y="106" class="mono">1</text><text x="472" y="106" class="mono">2</text>
        <rect x="22" y="132" width="540" height="75" class="value"/><path d="M202 132 L202 207 M382 132 L382 207" class="line"/>
        <text x="74" y="183" class="mono">200</text><text x="253" y="183" class="mono">120</text><text x="458" y="183" class="mono">80</text>
        <text x="73" y="260" class="mono">-3</text><text x="266" y="260" class="mono">-2</text><text x="462" y="260" class="mono">-1</text>
        <text x="22" y="325">3個の要素。添字3の位置はない。</text>
      </g>
      <g v-else-if="kind === 'copy'">
        <text x="20" y="38" class="label">copyで外側のリストを複製</text>
        <rect x="22" y="78" width="105" height="58" class="name"/><text x="62" y="119" class="mono">a</text>
        <rect x="22" y="162" width="105" height="58" class="name"/><text x="62" y="203" class="mono">c</text>
        <path d="M127 107 L239 107" class="arrow"/><path d="M127 191 L239 191" class="arrow"/>
        <rect x="254" y="73" width="316" height="67" class="value"/><text x="275" y="118" class="mono">[200, 120]</text>
        <rect x="254" y="156" width="316" height="67" class="value"/><text x="275" y="201" class="mono">[200, 120, 80]</text>
        <text x="22" y="281">c.append(80)でcだけが変わる。</text>
        <text x="22" y="327">整数の要素は変更できない値。</text>
      </g>
      <g v-else-if="kind === 'shallow'">
        <text x="20" y="38" class="label">内側の辞書は同じ対象を指す</text>
        <rect x="22" y="73" width="170" height="62" class="name"/><text x="46" y="115" class="mono">a : [・]</text>
        <rect x="22" y="181" width="170" height="62" class="name"/><text x="46" y="223" class="mono">c : [・]</text>
        <path d="M192 104 L332 153" class="arrow"/><path d="M192 213 L332 172" class="arrow"/>
        <rect x="348" y="112" width="230" height="100" class="value"/><text x="370" y="154" class="mono">quantity</text><text x="446" y="194" class="mono">3</text>
        <text x="22" y="296">外側は別でも、内側は共有する。</text>
        <text x="22" y="340">浅いcopyは入れ子を複製しない。</text>
      </g>
      <g v-else-if="kind === 'dictionary'">
        <text x="20" y="38" class="label">keyから対応するvalueを読む</text>
        <text x="30" y="88" class="label">キー</text><text x="353" y="88" class="label">値</text>
        <rect x="22" y="110" width="230" height="59" class="name"/><text x="43" y="151" class="mono">"name"</text><path d="M252 140 L324 140" class="arrow"/><text x="355" y="151">"ノート"</text>
        <rect x="22" y="185" width="230" height="59" class="name"/><text x="43" y="226" class="mono">"price"</text><path d="M252 215 L324 215" class="arrow"/><text x="355" y="226" class="mono">200</text>
        <rect x="22" y="260" width="230" height="59" class="name"/><text x="43" y="301" class="mono">"quantity"</text><path d="M252 290 L324 290" class="arrow"/><text x="355" y="301" class="mono">2</text>
      </g>
      <g v-else-if="kind === 'if-flow'">
        <text x="20" y="38" class="label">条件を上から順に調べる</text>
        <rect x="22" y="66" width="258" height="63" class="value"/><text x="38" y="109" class="mono">quantity &lt; 0</text>
        <path d="M280 97 L371 97" class="arrow"/><text x="290" y="81" class="tiny">True</text><text x="404" y="109">負数</text>
        <path d="M142 136 L142 189" class="arrow"/><text x="173" y="170" class="tiny">False</text>
        <rect x="22" y="202" width="258" height="63" class="value"/><text x="38" y="245" class="mono">quantity == 0</text>
        <path d="M280 233 L371 233" class="arrow"/><text x="290" y="217" class="tiny">True</text><text x="404" y="245">注文なし</text>
        <path d="M142 272 L142 317 L368 317" class="arrow"/><text x="178" y="307" class="tiny">False</text><text x="404" y="327">注文あり</text>
      </g>
      <g v-else-if="kind === 'while-flow'">
        <text x="20" y="38" class="label">判定を繰り返す順序</text>
        <rect x="155" y="67" width="225" height="60" class="value"/><text x="173" y="108" class="mono">count &lt; 3</text>
        <path d="M269 133 L269 179" class="arrow"/><text x="303" y="163" class="tiny">True</text>
        <rect x="153" y="192" width="230" height="91" class="value"/><text x="172" y="229" class="mono">print(count)</text><text x="172" y="268" class="mono">count += 1</text>
        <path d="M153 237 L49 237 L49 97 L145 97" class="arrow"/>
        <path d="M380 97 L475 97 L475 289" class="arrow"/><text x="392" y="82" class="tiny">False</text><text x="427" y="336">終了</text>
      </g>
      <g v-else-if="kind === 'scope'">
        <text x="20" y="38" class="label">同じ名前でも、所属が異なる</text>
        <rect x="22" y="78" width="540" height="72" class="value"/><text x="42" y="123" class="mono">外側 : price = 100</text>
        <rect x="22" y="178" width="540" height="112" class="name"/><text x="42" y="223" class="mono">関数内 : price = 250</text><text x="42" y="266" class="mono">quantity = 2</text>
        <text x="22" y="338">関数のpriceへの代入は外側に届かない。</text>
      </g>
      <g v-else-if="kind === 'nested-access'">
        <text x="20" y="38" class="label">添字で辞書、キーで値を選ぶ</text>
        <text x="24" y="94" class="mono">orders[1]</text>
        <path d="M162 108 L162 154" class="arrow"/>
        <rect x="22" y="166" width="540" height="87" class="value"/><text x="43" y="203">2件目の辞書</text><text x="43" y="240" class="mono">name : "ペン"</text>
        <path d="M421 261 L421 303" class="arrow"/><text x="250" y="295" class="mono">["name"]</text>
        <text x="370" y="346" class="label">"ペン"</text>
      </g>
      <g v-else-if="kind === 'orders'">
        <text x="20" y="38" class="label">1件ずつ小計を求めて加える</text>
        <rect x="22" y="71" width="245" height="92" class="value"/><text x="44" y="109">ノート</text><text x="44" y="148" class="mono">200 × 2</text>
        <rect x="311" y="71" width="251" height="92" class="value"/><text x="334" y="109">ペン</text><text x="334" y="148" class="mono">120 × 3</text>
        <path d="M144 169 L144 226" class="arrow"/><path d="M436 169 L436 226" class="arrow"/>
        <text x="92" y="270" class="label mono">400</text><text x="396" y="270" class="label mono">360</text>
        <text x="126" y="336" class="mono">400 + 360 = 760</text>
      </g>
      <g v-else-if="kind === 'call'">
        <text x="20" y="38" class="label">呼び出しの入力と結果</text>
        <text x="20" y="88" class="mono">subtotal(200, 2)</text>
        <path d="M210 105 L210 148" class="arrow"/>
        <rect x="22" y="161" width="540" height="121" class="value"/>
        <text x="46" y="198" class="mono">price = 200</text>
        <text x="46" y="236" class="mono">quantity = 2</text>
        <text x="46" y="274" class="mono">return price * quantity</text>
        <path d="M405 288 L405 310" class="arrow"/>
        <text x="22" y="343" class="mono">amount = 400</text><text x="330" y="343" class="label">結果を代入</text>
      </g>
    </svg>
  </div>
</template>
