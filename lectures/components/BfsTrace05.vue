<script setup>
import data from '../data/figures05.json'
defineProps({reveal:Boolean})
const label=(row)=>Object.entries(row.new).map(([k,v])=>`${k}: ${v || 'None'}`).join(', ')
</script>
<template>
<svg class="lesson-figure" width="1180" height="336" viewBox="0 0 1180 336" role="img" :aria-label="reveal ? 'BFSの取り出し、処理後キュー、新しい親の答え合わせ' : 'BFSの状態を予想する空欄'" font-family="Noto Sans JP" fill="#173042">
 <text x="8" y="34">取り出し</text><text x="226" y="34">処理後のキュー</text><text x="576" y="34">新しく記録した parent</text>
 <g v-for="(row,i) in data.trace" :key="i" :transform="`translate(0,${48+i*56})`"><line x1="4" x2="1176" y1="52" y2="52" stroke="#d4d6ce"/>
  <g v-if="reveal || i===0"><text x="24" y="35">{{row.node}}</text><text x="240" y="35">{{row.queue.join(', ') || '空'}}</text><text x="580" y="35">{{i===4 ? 'D が goal → 復元へ' : i===3 ? 'なし（Dは発見済み）' : label(row)}}</text></g>
  <g v-else><rect v-for="(col,j) in [{x:8,w:188},{x:216,w:334},{x:566,w:608}]" :key="j" :x="col.x" y="4" :width="col.w" height="44" rx="5" fill="none" stroke="#95620a" stroke-dasharray="6 4"/></g>
 </g>
</svg>
</template>
