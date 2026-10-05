<script setup>
import data from '../data/figures04.json'
defineProps({reveal:Boolean})
</script>
<template>
<svg class="lesson-figure" width="1180" height="222" viewBox="0 0 1180 222" role="img" :aria-label="reveal ? '操作数モデル8、16、32と増え方' : 'nが32の操作数を予想する空欄'" font-family="JetBrains Mono, Noto Sans JP" font-size="28" fill="#173042">
 <text v-for="(n,j) in [8,16,32]" :key="n" :x="510+j*190" y="36" text-anchor="middle">n = {{n}}</text><text v-if="reveal" x="1070" y="36" text-anchor="middle">16 → 32</text>
 <g v-for="(row,i) in data.growth" :key="row.key" :transform="`translate(0,${54+i*54})`"><line x1="4" x2="1176" y1="48" y2="48" stroke="#d4d6ce"/><text x="8" y="33">{{row.key}}</text><g v-for="(value,j) in row.values" :key="j"><rect v-if="j===2 && !reveal" x="830" y="2" width="120" height="43" rx="5" fill="none" stroke="#95620a" stroke-dasharray="6 4" /><text v-else :x="510+j*190" y="33" text-anchor="middle">{{value}}</text></g><text v-if="reveal" x="1070" y="33" text-anchor="middle" fill="#a6561b">{{row.ratio}}</text></g>
</svg>
</template>
