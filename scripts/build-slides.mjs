import { spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
const lessons = JSON.parse(readFileSync('docs/curriculum.json', 'utf8'))
const selected = process.argv.slice(2)
for (const lesson of lessons) {
  if (selected.length && !selected.includes(lesson.id)) continue
  const result = spawnSync(process.execPath, ['node_modules/@slidev/cli/bin/slidev.mjs', 'build',
    `lectures/${lesson.id}.md`, '--out', resolve(`dist/${lesson.id}`), '--base', `/${lesson.id}/`], { stdio: 'inherit' })
  if (result.status !== 0) process.exit(result.status || 1)
}
