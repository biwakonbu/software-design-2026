<script setup>
import { useId } from 'vue'
import '../styles/visual03.css'
const id = `expectation-${useId()}`
const rows = [
  ['空', '[], 1', 'None', 'None  OK', 'None  OK'],
  ['1個', '[1], 1', '0', '0  OK', 'None  NG'],
  ['末尾', '[1, 3, 5], 5', '2', '2  OK', 'None  NG'],
  ['不在', '[1, 3, 5], 4', 'None', 'None  OK', 'None  OK'],
  ['重複', '[2, 2, 2], 2', '0, 1, 2のどれか', '1  OK', '1  OK'],
]
const positions = [12, 115, 400, 698, 933]
</script>

<template>
  <svg viewBox="0 0 1152 370" class="search-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">仕様から期待値を作り実行結果と照合する</title>
    <desc :id="`${id}-desc`">仕様、手計算、実行結果の順に照合する。空リストはNone、1個の1を探すと添字0、1・3・5の5を探すと添字2、不在の4はNone、重複の2は添字0・1・2のどれでもよい。修正版は順にNone、0、2、None、1を返す。意図的な誤りのbuggyはNone、None、None、None、1を返し、1個と末尾でNGになる。有限個のテストは全入力の証明ではない。</desc>
    <defs><marker :id="id" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#154b74" /></marker></defs>
    <rect x="2" y="4" width="367" height="48" class="box"/><text x="20" y="38" class="label">① 仕様：入力と戻り値</text>
    <rect x="399" y="4" width="257" height="48" class="box"/><text x="415" y="38" class="label">② 手計算</text>
    <rect x="686" y="4" width="463" height="48" class="box"/><text x="705" y="38" class="label">③ 実行結果と照合</text>
    <path d="M372 28 L395 28" class="arrow" :marker-end="`url(#${id})`"/><path d="M659 28 L682 28" class="arrow" :marker-end="`url(#${id})`"/>
    <g class="label">
      <text x="12" y="92">分類</text><text x="115" y="92">入力, target</text><text x="400" y="92">期待値</text>
      <text x="698" y="92">修正版</text><text x="933" y="92">buggy ※</text>
    </g>
    <line x1="2" y1="103" x2="1150" y2="103" class="line"/>
    <g v-for="(row, rowIndex) in rows" :key="row[0]">
      <rect v-if="rowIndex === 1 || rowIndex === 2" x="925" :y="110 + rowIndex * 47" width="220" height="40" class="ng"/>
      <text v-for="(cell, column) in row" :key="column" :x="positions[column]" :y="140 + rowIndex * 47" :class="column === 1 ? 'mono' : ''">{{ cell }}</text>
      <line x1="2" :y1="153 + rowIndex * 47" x2="1150" :y2="153 + rowIndex * 47" class="line"/>
    </g>
    <text x="12" y="366">※ buggyは意図的な誤りの教材例。重複時はどちらも先頭の添字0を保証しない。</text>
  </svg>
</template>

<style scoped>
.search-figure { display:block; width:1152px; height:370px; max-width:100%; }
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }
.mono { font-family:'JetBrains Mono','Noto Sans JP',monospace; }
.label { font-weight:600; fill:#154b74; }
.box { fill:#e5f2f0; stroke:#154b74; stroke-width:2; }
.ng { fill:#f1f4f5; stroke:#154b74; stroke-width:2; stroke-dasharray:6 4; }
.line { stroke:#cbd7dd; stroke-width:2; }
.arrow { fill:none; stroke:#154b74; stroke-width:2; }
</style>
