<script setup>
import { useId } from 'vue'
import '../styles/learning03.css'
const id = `ai-use-${useId()}`
const steps = ['1 言葉にする', '2 予想する', '3 AIに聞く', '4 確かめる', '5 言い直す']
</script>
<template>
  <svg viewBox="0 0 1180 380" class="learning-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">AIの使い方と手元に残すものを比較する</title>
    <desc :id="`${id}-desc`">コードを依頼して受け取り、そのまま貼るだけでは説明できない場合がある。学習相手にするときは、自分で疑問を言葉にし、予想し、AIに聞き、確かめ、言い直す。説明できる理解と確かめた証拠を残す。</desc>
    <defs><marker :id="id" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto"><path d="M0 0 L14 7 L0 14 Z" fill="#154b74"/></marker></defs>
    <text x="0" y="30" class="muted">答えを受け取って、確かめずに使う</text>
    <g v-for="(label, i) in ['コードを依頼する','コードを受け取る','そのまま貼る']" :key="label">
      <rect :x="i * 400" y="48" :width="i === 2 ? 380 : 320" height="80" class="unchecked"/>
      <text :x="i * 400 + (i === 2 ? 190 : 160)" y="97" text-anchor="middle">{{ label }}</text>
      <path v-if="i < 2" :d="`M${i * 400 + 327} 88 H${i * 400 + 392}`" class="arrow" :marker-end="`url(#${id})`"/>
    </g>
    <text x="0" y="169" class="muted">コードは残るが、理由を説明できないことがある</text>
    <text x="0" y="228" class="label">学習相手として使う</text>
    <g v-for="(label, i) in steps" :key="label">
      <rect :x="i * 245" y="246" width="200" height="80" :class="i === 2 ? 'ai' : 'learner'"/>
      <text :x="i * 245 + 100" y="295" text-anchor="middle">{{ label }}</text>
      <path v-if="i < 4" :d="`M${i * 245 + 207} 286 H${i * 245 + 237}`" class="arrow" :marker-end="`url(#${id})`"/>
    </g>
    <text x="0" y="367" class="label">残すもの：自分の説明と、確かめた証拠</text>
  </svg>
</template>
<style scoped>
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }
.label { fill:#087d80; font-weight:700; }.muted { fill:#475569; }
rect { stroke-width:2; rx:8; }.unchecked { fill:#f1f4f5; stroke:#475569; stroke-dasharray:8 6; }
.learner { fill:#e5f2f0; stroke:#087d80; }.ai { fill:#fff5dc; stroke:#95620a; }
.arrow { fill:none; stroke:#154b74; stroke-width:2; }
</style>
