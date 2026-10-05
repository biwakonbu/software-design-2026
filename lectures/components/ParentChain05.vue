<script setup>
import data from '../data/figures05.json'
</script>
<template>
<svg class="lesson-figure" width="656" height="360" viewBox="0 0 656 360" role="img" aria-label="parentのDからB、A、Noneへたどり、逆順の経路を反転する" font-family="Noto Sans JP" fill="#173042">
 <g v-for="(key,i) in ['A','B','C','D']" :key="key"><rect :x="4+i*162" y="14" width="150" height="58" rx="6" :fill="key==='C' ? '#f0efeb' : '#e5f2f0'" stroke="#185b7a"/><text :x="79+i*162" y="53" text-anchor="middle">{{key}}: {{data.parent[key] || 'None'}}</text></g>
 <text x="12" y="130">親をたどる向き</text><text x="30" y="183">D → B → A → None</text>
 <text x="12" y="249">反転前 [D, B, A]</text><text x="12" y="300">↓ reverse</text><text x="12" y="347" fill="#185b7a">reverse後 [A, B, D]</text>
</svg>
</template>
