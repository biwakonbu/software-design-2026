<script setup>
import data from '../data/figures04.json'
const props=defineProps({mode:String})
const point=n=>data.treeNodes.find(x=>x.name===n)
const edge=(a,b)=>{
  const p=point(a), q=point(b)
  const dx=q.x-p.x, dy=q.y-p.y, distance=Math.hypot(dx,dy)
  return {x1:p.x+dx*36/distance,y1:p.y+dy*36/distance,x2:q.x-dx*42/distance,y2:q.y-dy*42/distance}
}
const badge=n=>['C','E'].includes(n.name) ? {x:n.x+30,y:n.y-34} : {x:n.x-28,y:n.y-28}
</script>
<template>
<svg class="lesson-figure" :width="mode==='bfs' ? 600 : 1180" :height="mode==='bfs' ? 380 : 360" :viewBox="mode==='bfs' ? '0 0 600 380' : '0 0 1180 360'" role="img" :aria-label="`木の${mode==='predict' ? '訪問順を予想する' : mode==='dfs' ? 'DFSと呼出しの積み重ね' : 'BFSの待機列'}`" font-family="Noto Sans JP" font-size="28" fill="#173042">
 <defs><marker :id="`tree-${mode}`" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10" fill="none" stroke="#185b7a" stroke-width="1.5" /></marker></defs>
 <g v-if="mode!=='bfs'">
  <line v-for="(e,i) in data.treeEdges" :key="i" v-bind="edge(...e)" stroke="#185b7a" stroke-width="2.5" :marker-end="`url(#tree-${mode})`" />
  <g v-for="n in data.treeNodes" :key="n.name">
    <circle :cx="n.x" :cy="n.y" r="34" fill="#e5f2f0" stroke="#185b7a" stroke-width="2" />
    <text :x="n.x" :y="n.y+10" text-anchor="middle">{{n.name}}</text>
    <text v-if="n.name==='A' || ['D','E','F'].includes(n.name)" :x="n.x+42" :y="n.y+10">{{n.name==='A' ? '根' : '葉'}}</text>
    <g v-if="mode==='dfs'"><circle :cx="badge(n).x" :cy="badge(n).y" r="20" fill="#a6561b" /><text :x="badge(n).x" :y="badge(n).y+10" text-anchor="middle" fill="white">{{data.dfs.indexOf(n.name)+1}}</text></g>
  </g>
 </g>
 <g v-if="mode==='predict'">
   <g v-for="(label,j) in ['DFSの順','BFSの順']" :key="label" :transform="`translate(600,${65+j*140})`">
    <text x="0" y="0">{{label}}</text><rect v-for="i in 6" :key="i" :x="(i-1)*92" y="24" width="80" height="56" rx="6" fill="none" stroke="#95620a" stroke-dasharray="6 4" stroke-width="2" />
   </g>
 </g>
 <g v-else-if="mode==='dfs'">
   <text x="600" y="38">visit の呼出し（下から積む）</text>
   <g v-for="(calls,i) in data.dfsCalls" :key="i" :transform="`translate(${600+i*94},0)`">
     <g v-for="(name,j) in calls" :key="j"><rect x="1" :y="245-j*62" width="80" height="56" rx="6" fill="#e5f2f0" stroke="#185b7a" stroke-width="2" /><text x="41" :y="281-j*62" text-anchor="middle">{{name}}</text></g>
     <text x="41" y="347" text-anchor="middle">{{data.dfs[i]}}</text>
   </g>
 </g>
 <g v-else>
   <text x="8" y="34">取り出す</text><text x="190" y="34">子を足した後のキュー</text>
   <g v-for="(name,i) in data.bfs" :key="name" :transform="`translate(0,${60+i*49})`"><line x1="4" x2="590" y1="38" y2="38" stroke="#d4d6ce" /><text x="66" y="26" text-anchor="middle">{{name}}</text><text x="208" y="26">{{data.bfsAfter[i].join('  ') || '（空）'}}</text></g>
 </g>
</svg>
</template>
