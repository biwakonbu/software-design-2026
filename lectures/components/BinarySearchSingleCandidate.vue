<script setup>
import { useId } from 'vue'
import '../styles/visual03.css'
defineProps({ gistUrl: { type: String, required: true } })
const id = `single-candidate-${useId()}`
</script>

<template>
  <svg viewBox="0 0 1152 370" class="search-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">候補1個でのbuggyとcorrectedの比較</title>
    <desc :id="`${id}-desc`">values=[1]、target=1。low=high=0の閉区間に候補が1個ある。意図的な誤りのbuggyは0&lt;0がFalseで値の比較をせずNoneを返す。修正版は0&lt;=0がTrueでvalues[0]と1を比較し、添字0を返す。</desc>
    <defs><marker :id="id" viewBox="0 0 8 8" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#154b74" /></marker></defs>
    <text x="12" y="30" class="mono">values = [1], target = 1　期待値 0</text>
    <a :href="gistUrl" target="_blank" rel="noopener"><text x="985" y="30" class="gist-link">公開Gist</text></a>
    <g v-for="(panel, index) in ['buggy', 'corrected']" :key="panel" :transform="`translate(${index * 590}, 0)`">
      <rect x="2" y="53" width="558" height="277" rx="10" :class="index === 0 ? 'buggy' : 'corrected'"/>
      <text x="18" y="89" class="label">{{ index === 0 ? 'A  buggy（意図的な誤り）' : 'B  corrected（修正版）' }}</text>
      <text x="18" y="129" class="mono">low = high = 0</text>
      <path d="M230 132 L260 150" :marker-end="`url(#${id})`" class="arrow"/>
      <rect x="270" y="109" width="84" height="56" class="cell"/>
      <text x="312" y="148" text-anchor="middle" class="mono">1</text>
      <text x="275" y="197">添字 0</text><text x="388" y="149">候補1個</text>
      <text x="18" y="237" class="mono">{{ index === 0 ? '① 0 &lt; 0 : False' : '① 0 &lt;= 0 : True' }}</text>
      <text x="18" y="277" class="mono">{{ index === 0 ? '② 比較0回 → return None' : '② 比較1回 → return 0' }}</text>
      <text x="18" y="317" class="label">{{ index === 0 ? 'NG：期待値0と不一致' : 'OK：期待値0と一致' }}</text>
    </g>
    <text x="12" y="364">比較回数：中央の値 values[middle] と target を調べた回数</text>
  </svg>
</template>

<style scoped>
.search-figure { display:block; width:1152px; height:370px; max-width:100%; }
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }
.mono { font-family:'JetBrains Mono','Noto Sans JP',monospace; }
.gist-link { fill:#154b74; text-decoration:underline; font-weight:600; }
.label { font-weight:600; fill:#154b74; }
.cell,.corrected { fill:#e5f2f0; stroke:#154b74; stroke-width:3; }
.buggy { fill:#f1f4f5; stroke:#154b74; stroke-width:3; stroke-dasharray:9 6; }
.arrow { fill:none; stroke:#154b74; stroke-width:3; }
</style>
