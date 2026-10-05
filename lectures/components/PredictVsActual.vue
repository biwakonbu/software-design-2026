<script setup>
import { useId } from 'vue'
import '../styles/learning03.css'
const id = `highest-results-${useId()}`
</script>
<template>
  <svg viewBox="0 0 1180 290" class="learning-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">期待値、予想、実行結果を別の欄で照合する</title>
    <desc :id="`${id}-desc`">マイナス3、マイナス1、マイナス5の期待値はマイナス1だが、意図的な誤り例highest_draftは0を返す。空入力は仕様ではValueErrorだが、誤り例は0を返す。自分が書いた予想は別の欄に写し、期待値との不一致と予想とのずれを分けて確かめる。</desc>
    <g v-for="(heading, n) in ['入力','期待値','予想','実行結果']" :key="heading">
      <text :x="[12,312,612,892][n]" y="34" class="label">{{ heading }}</text>
      <text :x="[12,312,612,892][n]" y="73">{{ ['', '仕様と手計算','2 で書いた値','highest_draft'][n] }}</text>
    </g>
    <g v-for="(input, n) in ['[-3, -1, -5]','[]']" :key="input">
      <text x="12" :y="146 + n * 100" class="mono">{{ input }}</text>
      <rect x="310" :y="96 + n * 100" width="280" height="80" class="expected"/><text x="450" :y="146 + n * 100" text-anchor="middle" class="mono">{{ n ? 'ValueError' : '-1' }}</text>
      <rect x="610" :y="96 + n * 100" width="260" height="80" class="prediction"/><text x="740" :y="146 + n * 100" text-anchor="middle">（各自）</text>
      <rect x="890" :y="96 + n * 100" width="288" height="80" class="mismatch"/><text x="910" :y="146 + n * 100" class="mono">0</text><text x="1148" :y="146 + n * 100" text-anchor="end" class="bad">不一致</text>
    </g>
  </svg>
</template>
<style scoped>
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }.mono { font-family:'JetBrains Mono','Noto Sans JP',monospace; }.label { font-weight:600; fill:#154b74; }.bad { fill:#a53324; font-weight:600; }
rect { stroke-width:2; }.expected { fill:#e5f2f0; stroke:#087d80; }.prediction { fill:#fff9e9; stroke:#95620a; stroke-dasharray:6 4; }.mismatch { fill:#f1f4f5; stroke:#a53324; }
</style>
