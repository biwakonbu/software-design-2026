<script setup>
import { computed } from 'vue'
const props=defineProps({diagram:Object,uid:String})
const d=computed(()=>props.diagram)
const point=id=>d.value.nodes.find(n=>n.id===id)
const center=n=>({x:n.x+n.w/2,y:n.y+n.h/2})
const toPoint=p=>Array.isArray(p)?{x:p[0],y:p[1]}:p
const height=computed(()=>Number(d.value.viewBox.split(/\s+/)[3]))
function boundary(n,toward,offset={x:0,y:0}){const base=center(n),c={x:base.x+offset.x,y:base.y+offset.y},dx=toward.x-c.x,dy=toward.y-c.y;const horizontal=dx>0?(n.x+n.w-c.x)/dx:dx<0?(n.x-c.x)/dx:Infinity;const vertical=dy>0?(n.y+n.h-c.y)/dy:dy<0?(n.y-c.y)/dy:Infinity;const ratio=Math.min(horizontal,vertical);return{x:c.x+dx*ratio,y:c.y+dy*ratio}}
function pairShift(e){
 const pair=[e.from,e.to].sort(),matching=d.value.edges.filter(x=>[x.from,x.to].sort().join('|')===pair.join('|')),offset=(matching.indexOf(e)-(matching.length-1)/2)*24
 const p=center(point(pair[0])),q=center(point(pair[1])),dx=q.x-p.x,dy=q.y-p.y,length=Math.hypot(dx,dy),shift={x:-dy*offset/length,y:dx*offset/length}
 return shift
}
function route(e){
 if(e.points)return e.points.map(toPoint)
 const a=point(e.from),b=point(e.to),ca=center(a),cb=center(b),via=(e.via||[]).map(toPoint)
 const shift=pairShift(e)
 const first=via[0]||{x:cb.x+shift.x,y:cb.y+shift.y},last=via.at(-1)||{x:ca.x+shift.x,y:ca.y+shift.y}
 return[boundary(a,first,shift),...via,boundary(b,last,shift)]
}
function path(e){return route(e).map((p,i)=>`${i?'L':'M'} ${p.x} ${p.y}`).join(' ')}
function label(e){
 if(e.labelAt){const p=toPoint(e.labelAt);return{...p,anchor:e.labelAnchor||'middle'}}
 const r=route(e);let best=0,distance=-1
 for(let i=0;i<r.length-1;i++){const dx=r[i+1].x-r[i].x,dy=r[i+1].y-r[i].y,l=Math.hypot(dx,dy);if(l>distance){distance=l;best=i}}
 const a=r[best],b=r[best+1],dx=b.x-a.x,dy=b.y-a.y,middle={x:(a.x+b.x)/2,y:(a.y+b.y)/2}
 const shift=pairShift(e),offset=Math.hypot(shift.x,shift.y)
 if(offset)return{x:middle.x+shift.x*22/offset,y:middle.y+shift.y*22/offset+10,anchor:'middle'}
 return Math.abs(dx)>=Math.abs(dy)?{x:middle.x,y:middle.y-14,anchor:'middle'}:{x:middle.x+12,y:middle.y+10,anchor:'start'}
}
const color=e=>e.type==='return'||e.kind==='counterfactual'?'#a6561b':'#185b7a'
const dash=e=>e.type==='reference'||e.type==='return'||e.kind==='counterfactual'?'8 5':null
const labelWidth=t=>[...t].reduce((w,c)=>w+(c.charCodeAt(0)>255?28:17),0)+14
const labelLeft=e=>label(e).x-(label(e).anchor==='start'?7:labelWidth(e.label)/2)
const textLines=t=>String(t||'').split('\n')
const tokens=n=>n.label.trim().split(/\s+/)
const tokenX=(n,i)=>n.x+12+(i+.5)*(n.w-24)/tokens(n).length
</script>
<template>
<svg class="course-diagram" width="1180" :height="height" :viewBox="d.viewBox" role="img" :aria-label="d.new_title" xmlns="http://www.w3.org/2000/svg">
<title>{{d.new_title}}</title><desc>{{d.explanation}} {{d.footer_check}}</desc>
<defs><marker v-for="c in ['blue','amber']" :key="c" :id="`${uid}-${c}`" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10" fill="none" :stroke="c==='blue'?'#185b7a':'#a6561b'" stroke-width="1.5" /></marker></defs>
<g v-for="(g,i) in d.groups||[]" :key="g.id||i"><rect :x="g.x+1" :y="g.y+1" :width="g.w-2" :height="g.h-2" rx="10" fill="#f0f6f8" stroke="#185b7a" stroke-width="2"/><text class="diagram-group-label" :x="g.x+16" :y="g.y+35" fill="#185b7a">{{g.label}}</text></g>
<g v-for="(e,i) in d.edges" :key="i"><path class="diagram-edge" :data-edge-index="i" :data-from="e.from" :data-to="e.to" :data-type="e.type" :d="path(e)" fill="none" :stroke="color(e)" :stroke-width="e.type==='contains'?(e.width||2):3" :stroke-dasharray="dash(e)" :marker-end="e.type==='contains'?null:`url(#${uid}-${color(e)==='#185b7a'?'blue':'amber'})`"/></g>
<g v-for="n in d.nodes" :key="n.id"><rect class="diagram-node" :data-node-id="n.id" :x="n.x" :y="n.y" :width="n.w" :height="n.h" rx="8" :fill="n.kind==='host'?'#fff2e8':'#fffdf8'" :stroke="n.kind==='host'||n.kind==='counterfactual'?'#a6561b':'#185b7a'" :stroke-width="n.kind==='host'?3:2" :stroke-dasharray="n.kind==='skipped'||n.kind==='counterfactual'?'7 5':null"/>
<g v-if="n.kind==='tokens'" class="diagram-tokens"><g v-for="(token,i) in tokens(n)" :key="i"><text class="diagram-token" :data-token-index="i" :x="tokenX(n,i)" :y="n.y+34" text-anchor="middle">{{token}}</text><text class="diagram-token-index" :data-token-index="i" :x="tokenX(n,i)" :y="n.y+78" text-anchor="middle">{{i}}</text></g></g>
<g v-else><text :x="n.x+n.w/2" :y="n.detail?n.y+34:n.y+n.h/2+10" text-anchor="middle" fill="#173042"><tspan v-for="(line,j) in textLines(n.label)" :key="j" :x="n.x+n.w/2" :dy="j?34:0">{{line}}</tspan></text>
<text v-if="n.detail" :x="n.x+n.w/2" :y="n.y+70" text-anchor="middle" fill="#173042"><tspan v-for="(line,j) in textLines(n.detail)" :key="j" :x="n.x+n.w/2" :dy="j?34:0">{{line}}</tspan></text></g></g>
<g v-for="(e,i) in d.edges" :key="`label-${i}`"><g v-if="e.label" class="diagram-edge-label" :data-edge-index="i"><rect :x="labelLeft(e)" :y="label(e).y-28" :width="labelWidth(e.label)" height="36" fill="#fffdf8"/><text :x="label(e).x" :y="label(e).y" :text-anchor="label(e).anchor" :fill="color(e)">{{e.label}}</text></g></g>
</svg>
</template>
