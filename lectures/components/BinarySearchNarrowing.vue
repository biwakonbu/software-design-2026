<script setup>
import { useId } from 'vue'
import '../styles/visual03.css'
const id = `narrowing-${useId()}`
</script>

<template>
  <svg viewBox="0 0 1152 370" class="search-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">1、3、5から5を探す候補区間の縮小</title>
    <desc :id="`${id}-desc`">修正版の探索。最初の候補は添字0から2。middle=1の値3はtarget=5より小さい。整列済みなので添字0と1を捨て、low=middle+1=2にする。次の候補は添字2だけ。low=high=middle=2で値5と一致し、添字2を返す。意図的な誤りのbuggyは2&lt;2がFalseとなり、この候補を調べずにNoneを返す。</desc>
    <defs>
      <marker :id="id" viewBox="0 0 8 8" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="14" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#154b74" /></marker>
      <pattern :id="`${id}-hatch`" patternUnits="userSpaceOnUse" width="12" height="12"><path d="M0 12 L12 0" stroke="#9baeb8" stroke-width="1"/></pattern>
    </defs>
    <text x="12" y="29" class="mono">corrected: values = [1, 3, 5], target = 5</text>
    <g v-for="step in [1, 2]" :key="step" :transform="`translate(0, ${(step - 1) * 152})`">
      <text x="12" y="79" class="label">{{ step === 1 ? '① 候補 [0, 2]' : '② 候補 [2, 2]' }}</text>
      <text x="382" y="65" class="mono">{{ step === 1 ? 'low' : '' }}</text>
      <text x="512" y="65" class="mono">{{ step === 1 ? 'middle' : '' }}</text>
      <text :x="step === 1 ? 678 : 370" y="65" class="mono">{{ step === 1 ? 'high' : 'low = high = middle = 2' }}</text>
      <g v-for="(value, index) in [1, 3, 5]" :key="value">
        <rect :x="370 + index * 150" y="89" width="130" height="57" :fill="step === 2 && index < 2 ? `url(#${id}-hatch)` : '#e5f2f0'" class="cell"/>
        <text :x="435 + index * 150" y="129" text-anchor="middle" class="mono">{{ value }}</text>
        <text :x="388 + index * 150" y="182">添字 {{ index }}</text>
        <path v-if="step === 1 || index === 2" :d="`M${435 + index * 150} 68 L${435 + index * 150} 83`" class="arrow" :marker-end="`url(#${id})`"/>
      </g>
      <text x="20" y="126">{{ step === 1 ? 'values[1] = 3 &lt; 5' : 'values[2] = 5 == 5' }}</text>
      <text x="854" y="121" class="label">{{ step === 1 ? '残す：添字2' : 'OK：return 2' }}</text>
      <text x="20" y="169">{{ step === 1 ? '添字0・1を捨てる' : '中央の値と一致' }}</text>
    </g>
    <path d="M1110 150 L1110 226" class="arrow" :marker-end="`url(#${id})`"/>
    <text x="840" y="198" class="mono">low = 1 + 1 = 2</text>
    <text x="20" y="367">buggy（意図的な誤り）は 2 &lt; 2 がFalseで、最後の候補を調べない。</text>
  </svg>
</template>

<style scoped>
.search-figure { display:block; width:1152px; height:370px; max-width:100%; }
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }
.mono { font-family:'JetBrains Mono','Noto Sans JP',monospace; }
.label { font-weight:600; fill:#154b74; }
.cell { stroke:#154b74; stroke-width:3; }
.arrow { fill:none; stroke:#154b74; stroke-width:3; }
</style>
