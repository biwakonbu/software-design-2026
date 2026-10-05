<script setup>
import { useId } from 'vue'
import '../styles/learning03.css'
const id = `highest-trace-${useId()}`
const rows = [['初期','-','0'],['3','3 > 0 True','3'],['7','7 > 3 True','7'],['5','5 > 7 False','7']]
</script>
<template>
  <svg viewBox="0 0 1180 350" class="learning-figure" role="img" :aria-labelledby="`${id}-title ${id}-desc`">
    <title :id="`${id}-title`">期待値と予想を分けて、初期値0の比較を手で追う</title>
    <desc :id="`${id}-desc`">左は3、7、5を順に比較した完成例。bestは0、3、7、7となり戻り値7は期待値7と一致する。右はマイナス3、マイナス1、マイナス5を自分で追う空欄。仕様から求めた期待値はマイナス1。コードが返す値の予想は、自分で記入する。</desc>
    <g v-for="(offset, side) in [0, 620]" :key="offset">
      <text :x="offset" y="32" class="label">{{ side ? '[-3, -1, -5] を自分で追う' : '[3, 7, 5] を手で追った例' }}</text>
      <rect :x="offset" y="44" width="560" height="48" class="header"/>
      <text v-for="(heading, col) in ['t','t > best','best']" :key="heading" :x="offset + [12,132,372][col]" y="78" class="mono">{{ heading }}</text>
      <g v-for="(row, n) in rows" :key="n">
        <line :x1="offset" :x2="offset + 560" :y1="144 + n * 52" :y2="144 + n * 52" class="line"/>
        <text :x="offset + 12" :y="130 + n * 52" :class="n ? 'mono' : ''">{{ side && n ? [-3,-1,-5][n - 1] : row[0] }}</text>
        <g v-for="col in [1,2]" :key="col">
          <rect v-if="side && n" :x="offset + [0,124,364][col]" :y="96 + n * 52" :width="col === 1 ? 232 : 192" height="44" class="blank"/>
          <text :x="offset + [0,132,372][col]" :y="130 + n * 52" class="mono">{{ side && n ? '?' : row[col] }}</text>
        </g>
      </g>
    </g>
    <text x="0" y="338" class="label">戻り値 7 = 期待値 7</text>
    <text x="620" y="338" class="label">期待値 -1（仕様）</text><text x="885" y="338">予想：</text><rect x="982" y="306" width="192" height="40" class="blank"/>
  </svg>
</template>
<style scoped>
text { font:28px 'Noto Sans JP',sans-serif; fill:#172a40; }.mono { font-family:'JetBrains Mono','Noto Sans JP',monospace; }.label { fill:#087d80; font-weight:600; }
.header { fill:#e9eff0; }.line { stroke:#cbd7dd; }.blank { fill:#fff9e9; stroke:#95620a; stroke-width:2; stroke-dasharray:6 4; }
</style>
