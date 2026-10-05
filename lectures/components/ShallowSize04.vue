<template>
<svg class="lesson-figure" width="616" height="340" viewBox="0 0 616 340" role="img" aria-label="getsizeofはリスト本体を測り、参照先の整数を合計しない" font-family="Noto Sans JP" font-size="28" fill="#173042">
 <defs><marker id="shallow04" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0 L10 5 L0 10" fill="#185b7a"/></marker></defs>
 <text x="8" y="34">getsizeof(items)</text><rect x="5" y="44" width="256" height="280" rx="8" fill="#e5f2f0" stroke="#185b7a" stroke-width="2" stroke-dasharray="7 4"/><text x="26" y="84">list本体</text>
 <text x="296" y="80">getsizeof(items[0])</text>
 <g v-for="(v,i) in [10,20,30]" :key="v"><rect x="36" :y="104+i*66" width="180" height="48" rx="5" fill="white" stroke="#185b7a"/><circle cx="170" :cy="128+i*66" r="5" fill="#185b7a"/><line x1="180" :y1="128+i*66" x2="420" :y2="128+i*66" stroke="#185b7a" stroke-width="2" marker-end="url(#shallow04)"/><rect x="428" :y="104+i*66" width="168" height="48" rx="5" :fill="i===0 ? '#fff1df' : 'white'" :stroke="i===0 ? '#a6561b' : '#83929a'" :stroke-width="i===0 ? 3 : 1.5" :stroke-dasharray="i===0 ? '6 4' : undefined"/><text x="512" :y="138+i*66" text-anchor="middle">int {{v}}</text></g>
</svg>
</template>
