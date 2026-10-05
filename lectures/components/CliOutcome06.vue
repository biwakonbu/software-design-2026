<script setup>
import data from '../data/figures06.json'
const result=row=>Array.isArray(row.result) ? `[${row.result.map(s=>`'${s}'`).join(', ')}]` : row.result===null ? 'None' : row.result
const lines=row=>row.stdout ? row.stdout.trim().split('\n') : row.args[0]==='UNKNOWN' ? ['入力エラー:','未知の駅IDです'] : [row.stderr.trim()]
</script>
<template>
<svg class="lesson-figure" width="1180" height="436" viewBox="0 0 1180 436" role="img" aria-label="正常、同駅、隣駅、到達不能、未知の駅で関数結果とCLI表示と終了コードを区別する" font-family="Noto Sans JP" fill="#173042">
 <text x="8" y="34">入力</text><text x="220" y="34">関数の結果</text><text x="554" y="34">CLIの表示</text><text x="1035" y="34">終了コード</text>
 <g v-for="(row,i) in data.outcomes" :key="i" :transform="`translate(0,${48+i*76})`"><line x1="4" x2="1176" y1="73" y2="73" stroke="#d4d6ce"/><text x="8" y="36">{{row.args.join(' ')}}</text><text x="220" y="36">{{result(row)}}</text><text v-for="(line,j) in lines(row)" :key="j" x="554" :y="lines(row).length===1 ? 36 : 26+j*36">{{line}}</text><text x="1095" y="36" text-anchor="middle" :fill="row.exit ? '#a6561b' : '#185b7a'">{{row.exit}}</text></g>
</svg>
</template>
