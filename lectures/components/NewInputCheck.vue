<script setup>
import { useId } from 'vue'
import '../styles/learning03.css'
const props = defineProps({ reveal:Boolean })
const id = `highest-new-input-${useId()}`
const inputs = ['[5]', '[2, 9, 9]', '[0, -2]']
const results = [5, 9, 0]
const notes = [['修正版は比較0回','先頭が答えになる'],['同じ最大値が2つ','> のままでよいか'],['0 が答えなので','誤り版も正しく見える']]
</script>
<template>
  <svg viewBox="0 0 1180 360" class="learning-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">新しい入力の結果と理由を、実行前に予想する</title>
    <desc :id="`${id}-desc`">5だけの入力、2・9・9の入力、0・マイナス2の入力について予想を空欄に書く。結果を表示したら修正版と誤り版を照合する。正しい予想だけで理解を断定せず、初期値と更新の理由も説明する。</desc>
    <g v-for="(input, n) in inputs" :key="input">
      <rect :x="n * 405 + 2" y="2" width="366" height="356" class="card"/>
      <text :x="n * 405 + 185" y="48" text-anchor="middle" class="mono label">{{ input }}</text>
      <text :x="n * 405 + 24" y="104">予想</text><rect :x="n * 405 + 100" y="74" width="246" height="44" class="prediction"/>
      <g v-if="props.reveal">
        <rect :x="n * 405 + 16" y="142" width="338" height="90" class="result"/>
        <text :x="n * 405 + 24" y="178">修正版：{{ results[n] }}</text><text :x="n * 405 + 24" y="218">誤り版：{{ results[n] }}</text>
      </g>
      <text v-if="props.reveal" v-for="(line, k) in notes[n]" :key="line" :x="n * 405 + 24" :y="290 + k * 40">{{ line }}</text>
      <g v-if="!props.reveal">
        <text :x="n * 405 + 24" y="176">理由：</text>
        <line :x1="n * 405 + 24" :x2="n * 405 + 344" y1="220" y2="220" class="writing"/>
        <text :x="n * 405 + 24" y="290">初期値と更新を</text>
        <text :x="n * 405 + 24" y="330">1文で説明する</text>
      </g>
    </g>
  </svg>
</template>
<style scoped>
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }.mono { font-family:'JetBrains Mono','Noto Sans JP',monospace; }.label { font-weight:600; }
.card { fill:#f1f4f5; stroke:#154b74; stroke-width:2; rx:8; }.prediction { fill:#fff9e9; stroke:#95620a; stroke-width:2; stroke-dasharray:6 4; }.result { fill:#e5f2f0; }.writing { stroke:#95620a; stroke-width:2; stroke-dasharray:6 4; }
</style>
