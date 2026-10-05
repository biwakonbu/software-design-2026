<script setup>
import data from '../data/figures06.json'
defineProps({full:Boolean,current:Number})
</script>
<template>
<svg class="lesson-figure" width="1180" :height="full ? 170 : 84" :viewBox="full ? '0 0 1180 170' : '0 0 1180 84'" role="img" :aria-label="`実装の段階。${current ? '現在は段階'+current : '仕様、初期状態、発見、停止、復元、検証と提出'}`" font-family="Noto Sans JP" fill="#173042">
 <g v-for="(name,i) in data.stages" :key="i"><rect :x="8+i*160" y="8" :width="i===6 ? 196 : 148" height="64" rx="7" :fill="current===i ? '#185b7a' : '#e5f2f0'" stroke="#185b7a" stroke-width="2"/><text :x="8+i*160+(i===6 ? 98 : 74)" y="50" text-anchor="middle" :fill="current===i ? 'white' : '#173042'">{{name}}</text></g>
 <g v-if="full"><path d="M176 91 H308 M336 91 H948 M976 91 H1160" fill="none" stroke="#185b7a" stroke-width="2"/><text x="242" y="135" text-anchor="middle">演習 段階1</text><text x="642" y="135" text-anchor="middle">演習 段階2（作業中に戻って読む）</text><text x="1066" y="135" text-anchor="middle">演習 段階3・4</text></g>
</svg>
</template>
