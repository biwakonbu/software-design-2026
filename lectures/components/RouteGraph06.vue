<script setup>
import data from '../data/figures06.json'
const edge=pair=>{
 const p=data.nodes.find(n=>n.id===pair[0]),q=data.nodes.find(n=>n.id===pair[1])
 const dx=q.x-p.x,dy=q.y-p.y,d=Math.hypot(dx,dy)
 return{x1:p.x+dx*38/d,y1:p.y+dy*38/d,x2:q.x-dx*38/d,y2:q.y-dy*38/d}
}
</script>
<template>
<svg class="lesson-figure" width="1180" height="310" viewBox="0 0 1180 310" role="img" aria-label="架空駅A B D E C Aの無向の循環と、孤立駅X。各辺は移動1回" font-family="Noto Sans JP" fill="#173042">
 <line v-for="(pair,i) in data.edges" :key="i" v-bind="edge(pair)" stroke="#185b7a" stroke-width="3"/>
 <g v-for="n in data.nodes" :key="n.id"><circle :cx="n.x" :cy="n.y" r="36" :fill="n.isolated ? '#f0efeb' : '#e5f2f0'" stroke="#185b7a" stroke-width="2" :stroke-dasharray="n.isolated ? '6 4' : undefined"/><text :x="n.x" :y="n.y+10" text-anchor="middle">{{n.id}}</text><text v-if="n.isolated" :x="n.x+46" :y="n.y+10">（孤立）</text></g>
</svg>
</template>
