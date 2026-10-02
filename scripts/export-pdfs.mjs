import { spawnSync } from 'node:child_process'
import { mkdirSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
const lessons = JSON.parse(readFileSync('docs/curriculum.json', 'utf8'))
const selected = process.argv.slice(2)
mkdirSync('output/pdf', { recursive: true })
for (const lesson of lessons) {
  if (selected.length && !selected.includes(lesson.id)) continue
  console.log(`Export ${lesson.id}: ${lesson.title}`)
  const result = spawnSync(process.execPath, ['node_modules/@slidev/cli/bin/slidev.mjs', 'export',
    `lectures/${lesson.id}.md`, '--output', resolve(lesson.pdf), '--with-toc', '--timeout', '60000', '--wait', '500'],
    { stdio: 'inherit' })
  if (result.status !== 0) process.exit(result.status || 1)
}
