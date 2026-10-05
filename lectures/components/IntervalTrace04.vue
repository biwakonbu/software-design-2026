<script setup>
import { computed } from 'vue'
import data from '../data/figures04.json'
const props = defineProps({ kind:String })
const half = computed(() => props.kind === 'half-open')
const rows = computed(() => half.value ? data.halfOpen : data.closed)
const updates = computed(() => half.value ? ['5 < 6 → hi = 2','5 > 4 → lo = 2','lo < hi が偽 → None'] : ['5 > 4 → low = 2','5 < 6 → high = 1','low ≤ high が偽 → None'])
</script>
<template>
<svg class="lesson-figure" width="1180" height="356" viewBox="0 0 1180 356" role="img" :aria-label="half ? '半開区間で5の不在まで追う' : '閉区間で5の不在まで追う'" font-family="Noto Sans JP" font-size="28" fill="#173042">
  <text x="8" y="32">比較前の範囲</text><text x="260" y="32">添字</text><text v-for="i in 4" :key="i" :x="340+(i-1)*100" y="32" text-anchor="middle">{{i-1}}</text>
  <text v-if="half" x="744" y="32" text-anchor="middle">4 (len)</text>
  <g v-for="(row,i) in rows" :key="i" :transform="`translate(0,${48+i*102})`">
    <text x="8" y="32">{{half ? `lo=${row[0]}, hi=${row[1]}` : `low=${row[0]}, high=${row[1]}`}}</text>
    <g v-for="(value,j) in data.values" :key="j">
      <rect :x="290+j*100" y="2" width="96" height="50" rx="5" :fill="(j>=row[0] && (half ? j<row[1] : j<=row[1])) ? '#e5f2f0' : '#f0efeb'" :stroke="j===row[2] ? '#a6561b' : '#83929a'" :stroke-width="j===row[2] ? 4 : 1.5" />
      <text :x="338+j*100" y="36" text-anchor="middle">{{value}}</text>
    </g>
    <line v-if="half" :x1="290+row[0]*100" y1="0" :x2="290+row[0]*100" y2="56" stroke="#185b7a" stroke-width="3" />
    <line v-if="half" :x1="290+row[1]*100" y1="0" :x2="290+row[1]*100" y2="56" stroke="#a6561b" stroke-width="3" stroke-dasharray="6 4" />
    <text :x="half ? 290+row[0]*100 : 338+row[0]*100" y="85" :text-anchor="half && row[0]===row[1] ? 'end' : 'middle'">{{half ? 'lo' : 'low'}}</text>
    <text :x="half ? 290+row[1]*100+(row[0]===row[1] ? 6 : 0) : 338+row[1]*100" y="85" :text-anchor="half && row[0]===row[1] ? 'start' : 'middle'" fill="#a6561b">{{half && row[0]===row[1] ? '= hi' : (half ? 'hi' : 'high')}}</text>
    <text x="774" y="30">{{row[2]===null ? '候補なし' : `${half ? 'mid' : 'middle'}=${row[2]} → ${data.values[row[2]]}`}}</text>
    <text x="774" y="72">{{updates[i]}}</text>
  </g>
</svg>
</template>
