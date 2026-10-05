<script setup>
import {computed} from 'vue'
import data from '../data/figures05.json'
const props=defineProps({variant:String})
const graph=computed(()=>data[props.variant])
const edge=(pair)=>{
 const p=graph.value.nodes.find(n=>n.id===pair[0]),q=graph.value.nodes.find(n=>n.id===pair[1])
 const dx=q.x-p.x,dy=q.y-p.y,d=Math.hypot(dx,dy),pr=p.rect ? 104 : 38,qr=q.rect ? 108 : 40
 return{x1:p.x+dx*pr/d,y1:p.y+dy*pr/d,x2:q.x-dx*qr/d,y2:q.y-dy*qr/d}
}
</script>
<template>
<svg class="lesson-figure" :width="graph.width" :height="graph.height" :viewBox="`0 0 ${graph.width} ${graph.height}`" role="img" :aria-label="`グラフの${variant}図。線は辺、矢印は移動できる向き`" font-family="Noto Sans JP" fill="#173042">
 <defs><marker :id="`graph05-${variant}`" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10" fill="#185b7a"/></marker></defs>
 <line v-for="(pair,i) in graph.edges" :key="i" v-bind="edge(pair)" stroke="#185b7a" stroke-width="3" :marker-end="graph.directed ? `url(#graph05-${variant})` : undefined"/>
 <g v-for="n in graph.nodes" :key="n.id">
  <rect v-if="n.rect" :x="n.x-100" :y="n.y-32" width="200" height="64" rx="8" fill="#e5f2f0" stroke="#185b7a" stroke-width="2"/>
  <circle v-else :cx="n.x" :cy="n.y" r="36" :fill="n.isolated ? '#f0efeb' : '#e5f2f0'" stroke="#185b7a" stroke-width="2" :stroke-dasharray="n.isolated ? '6 4' : undefined"/>
  <text :x="n.x" :y="n.y+10" text-anchor="middle">{{n.label || n.id}}</text>
  <text v-if="n.isolated && variant==='adjacency'" :x="n.x" :y="n.y+78" text-anchor="middle">辺なし</text>
 </g>
 <g v-if="variant==='layersDiagram'"><text v-for="(label,i) in ['距離 0','距離 1','距離 2','到達不能']" :key="label" :x="[150,470,790,1060][i]" y="34" text-anchor="middle">{{label}}</text></g>
</svg>
</template>
