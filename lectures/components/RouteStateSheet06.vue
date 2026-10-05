<template>
<svg class="lesson-figure" width="1180" height="340" viewBox="0 0 1180 340" role="img" aria-label="自分の実装の取り出し、処理後キュー、新しい親を記録する空欄。開始状態だけAとA:None" font-family="Noto Sans JP" fill="#173042">
 <text x="8" y="34">取り出した駅</text><text x="280" y="34">処理後のキュー</text><text x="650" y="34">新しい parent</text>
 <text x="24" y="88">（なし）</text><text x="294" y="88">A</text><text x="662" y="88">A: None</text>
 <g v-for="i in 4" :key="i" :transform="`translate(0,${102+(i-1)*58})`"><rect v-for="(col,j) in [{x:8,w:248},{x:272,w:352},{x:640,w:532}]" :key="j" :x="col.x" y="4" :width="col.w" height="46" rx="5" fill="none" stroke="#95620a" stroke-dasharray="6 4"/></g>
</svg>
</template>
