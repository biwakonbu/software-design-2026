<script setup>
import data from '../data/figures04.json'
defineProps({kind:String})
</script>
<template>
<svg class="lesson-figure" width="696" :height="kind==='stack' ? 280 : 260" :viewBox="kind==='stack' ? '0 0 696 280' : '0 0 696 260'" role="img" :aria-label="kind==='stack' ? '末尾に入れて末尾から取り出すスタックの状態' : '先頭から取り出すキューの状態'" font-family="Noto Sans JP" font-size="28" fill="#173042">
 <g v-if="kind==='stack'">
  <g v-for="(row,i) in data.stack" :key="i" :transform="`translate(${8+i*170},0)`"><text x="76" y="40" text-anchor="middle">{{['append A','append B','pop → B','pop → A'][i]}}</text><path d="M12 80 V220 H140 V80" fill="none" stroke="#185b7a" stroke-width="2"/><g v-for="(v,j) in row" :key="j"><rect x="18" :y="162-j*60" width="116" height="54" rx="5" fill="#e5f2f0" stroke="#185b7a"/><text x="76" :y="198-j*60" text-anchor="middle">{{v}}</text></g><text v-if="!row.length" x="76" y="198" text-anchor="middle">空</text></g>
 </g>
 <g v-else>
  <text x="282" y="34">先頭 →</text><g v-for="(row,i) in data.queue" :key="i" :transform="`translate(0,${44+i*70})`"><text x="8" y="36">{{['初期','append C','popleft → A'][i]}}</text><g v-for="(v,j) in row" :key="j"><rect :x="278+j*120" y="2" width="110" height="54" rx="5" fill="#e5f2f0" stroke="#185b7a"/><text :x="333+j*120" y="38" text-anchor="middle">{{v}}</text></g></g>
 </g>
</svg>
</template>
