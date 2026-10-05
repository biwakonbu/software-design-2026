<script setup>
import { useId } from 'vue'
import '../styles/learning03.css'
const id = `adoption-gate-${useId()}`
const questions = ['Q1 各行・各文の意味が言える？','Q2 選んだ入力の結果を予想できる？','Q3 誤りそうな入力を1つ挙げられる？']
</script>
<template>
  <svg viewBox="0 0 1180 400" class="learning-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">コードや説明を採用する前に、3つの問いで理解を確認する</title>
    <desc :id="`${id}-desc`">各行の役割、選んだ入力の結果の予想、誤りそうな入力を答えられるか。答えられない問いがあれば、そのまま貼らずにAIへ分からない行の説明を求める段に戻る。3つ答えられても正しさの保証ではなく、次に実行で確かめる。</desc>
    <defs><marker :id="id" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto"><path d="M0 0 L14 7 L0 14 Z" fill="#154b74"/></marker></defs>
    <rect x="720" y="2" width="458" height="308" class="back"/>
    <text v-for="(line, n) in ['そのまま貼らない','3 に戻り、','分からない行の','説明を求める']" :key="line" x="950" :y="70 + n * 52" text-anchor="middle">{{ line }}</text>
    <g v-for="(question, n) in questions" :key="question">
      <rect x="2" :y="n * 115 + 2" width="616" height="76" class="question"/>
      <text x="24" :y="n * 115 + 49">{{ question }}</text>
      <path :d="`M620 ${n * 115 + 40} H712`" class="arrow" :marker-end="`url(#${id})`"/>
      <text x="668" :y="n * 115 + 24" text-anchor="middle" class="branch">いいえ</text>
      <path :d="`M310 ${n * 115 + 81} V${n * 115 + 110}`" class="arrow" :marker-end="`url(#${id})`"/>
      <text x="326" :y="n * 115 + 107" class="label">はい</text>
    </g>
    <rect x="2" y="342" width="616" height="54" class="proceed"/><text x="24" y="378">次へ進み、4 で実行して確かめる</text>
  </svg>
</template>
<style scoped>
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }.label { fill:#087d80; }.branch { fill:#95620a; }
rect { stroke-width:2; rx:8; }.question { fill:#f1f4f5; stroke:#154b74; }.back { fill:#fff5dc; stroke:#95620a; }.proceed { fill:#e5f2f0; stroke:#087d80; }.arrow { fill:none; stroke:#154b74; stroke-width:2; }
</style>
