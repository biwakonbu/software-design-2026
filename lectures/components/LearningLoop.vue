<script setup>
import { useId } from 'vue'
import '../styles/learning03.css'
const props = defineProps({ current: { type:Number, default:0 }, strip:Boolean })
const id = `learning-loop-${useId()}`
const steps = ['1 言葉にする','2 予想する','3 AIに聞く','4 確かめる','5 言い直す']
const owners = ['自分','自分','AIと','自分','自分']
const records = [['疑問を','1文で書く'],['期待値と','予想'],['説明・','ヒント'],['実行結果・','反例・資料'],['自分の説明・','新しい入力']]
</script>
<template>
  <svg :viewBox="props.strip ? '0 0 1180 64' : '0 0 1180 380'" class="learning-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">学習相手にする5ステップ{{ props.current ? `：現在は${steps[props.current - 1]}` : '' }}</title>
    <desc :id="`${id}-desc`">自分で疑問を言葉にする。期待値とコードの動作の予想を分ける。AIには説明やヒントを求める。実行、反例、資料で確かめる。自分の言葉と新しい入力で説明し直す。説明できない点が残れば疑問を書く段へ戻る。</desc>
    <defs><marker :id="id" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="12" refY="7" orient="auto"><path d="M0 0 L14 7 L0 14 Z" fill="#154b74"/></marker></defs>
    <g v-if="!props.strip"><path d="M1080 68 V49 H100 V66" class="arrow" :marker-end="`url(#${id})`"/><text x="590" y="32" text-anchor="middle">説明できない点が残れば、1へ戻る</text></g>
    <g v-for="(label, i) in steps" :key="label">
      <rect :x="i * 245" :y="props.strip ? 4 : 70" width="200" :height="props.strip ? 56 : 130" :class="[i === 2 ? 'ai' : 'learner', props.current === i + 1 ? 'current' : '']"/>
      <text v-if="!props.strip" :x="i * 245 + 100" y="115" text-anchor="middle" class="owner">{{ owners[i] }}</text>
      <text :x="i * 245 + 100" :y="props.strip ? 42 : 165" text-anchor="middle" :class="props.strip && props.current === i + 1 ? 'active-label' : 'label'">{{ label }}</text>
      <path v-if="i < 4" :d="`M${i * 245 + 206} ${props.strip ? 32 : 135} H${i * 245 + 237}`" class="arrow" :marker-end="`url(#${id})`"/>
      <g v-if="!props.strip"><text v-for="(line, n) in records[i]" :key="line" :x="i * 245 + 100" :y="250 + n * 40" text-anchor="middle">{{ line }}</text></g>
    </g>
    <text v-if="!props.strip" x="0" y="360" class="owner">下段：その段で手元に残すもの</text>
  </svg>
</template>
<style scoped>
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }.label { font-weight:600; }.owner { fill:#475569; }
rect { stroke-width:2; rx:8; }.learner { fill:#f1f4f5; stroke:#154b74; }.ai { fill:#fff5dc; stroke:#95620a; }
.current { fill:#154b74; stroke-width:3; }.active-label { fill:white; font-weight:600; }.arrow { fill:none; stroke:#154b74; stroke-width:2; }
</style>
