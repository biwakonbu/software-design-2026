<template>
<svg class="lesson-figure" width="1180" height="250" viewBox="0 0 1180 250" role="img" aria-label="AからDへ直行なら1辺10分、B経由なら2辺4分。辺数と時間は異なる" font-family="Noto Sans JP" fill="#173042">
 <path d="M158 110 L552 50 M628 50 L1022 110" fill="none" stroke="#185b7a" stroke-width="3"/>
 <path d="M130 148 Q590 285 1050 148" fill="none" stroke="#a6561b" stroke-width="3"/>
 <g v-for="(n,i) in ['A','B','D']" :key="n"><circle :cx="[120,590,1060][i]" :cy="[110,50,110][i]" r="36" fill="#e5f2f0" stroke="#185b7a" stroke-width="2"/><text :x="[120,590,1060][i]" :y="[120,60,120][i]" text-anchor="middle">{{n}}</text></g>
 <g v-for="x in [350,830]" :key="x"><rect :x="x-46" y="39" width="92" height="42" fill="#fbfaf6"/><text :x="x" y="71" text-anchor="middle">2分</text></g>
 <rect x="536" y="185" width="108" height="44" fill="#fbfaf6"/><text x="590" y="216" text-anchor="middle" fill="#a6561b">10分</text>
</svg>
</template>
