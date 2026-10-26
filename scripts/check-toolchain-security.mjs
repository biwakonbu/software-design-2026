import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { createServer } from 'node:net'
import { readFileSync, mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'
import { parseSync } from '@slidev/parser'

const root = fileURLToPath(new URL('../', import.meta.url))
const reservation = createServer()
await new Promise((resolve, reject) => {
  reservation.once('error', reject)
  reservation.listen(0, '127.0.0.1', resolve)
})
const port = reservation.address().port
await new Promise(resolve => reservation.close(resolve))
const base = `http://localhost:${port}`
const server = spawn(process.execPath, [
  'node_modules/@slidev/cli/bin/slidev.mjs', 'lectures/05.md', '--port', String(port),
], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] })
let output = ''
server.stdout.on('data', chunk => { output += chunk })
server.stderr.on('data', chunk => { output += chunk })
let browser, page
try {
  let ready = false
  for (let attempt = 0; attempt < 120; attempt++) {
    if (server.exitCode !== null) throw new Error(`Slidev exited: ${output}`)
    try {
      if ((await fetch(base, { signal: AbortSignal.timeout(1000) })).ok) {
        ready = true
        break
      }
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 250))
  }
  assert.ok(ready, `Slidev did not start: ${output}`)
  for (const path of ['/__mcp', '/__mcp/', '/__mcp?test=1']) {
    for (const method of ['GET', 'POST']) {
      const response = await fetch(base + path, {
        method,
        ...(method === 'POST' ? {
          headers: { 'Content-Type': 'application/json' },
          body: '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}',
        } : {}),
        signal: AbortSignal.timeout(5000),
      })
      assert.equal(response.status, 403, `${method} ${path}`)
      assert.match(await response.text(), /does not expose MCP editing tools/)
    }
  }

  // Inspect Monaco's actual transformed import, not just package-lock.json:
  // Monaco also ships a vulnerable bundled copy that npm audit cannot replace.
  const source = await fetch(new URL('/@fs' + root + 'node_modules/monaco-editor/esm/vs/base/browser/domSanitize.js', base))
  const transformed = await source.text()
  assert.ok(source.ok, `Monaco module: ${source.status} ${transformed.slice(0,200)}`)
  const purifierImport = transformed.match(/import\s+\w+\s+from\s+["']([^"']*dompurify[^"']*)["']/)
  assert.ok(purifierImport, 'Monaco sanitizer import was not found')
  assert.ok(!purifierImport[1].includes('/browser/dompurify/'), 'Monaco still uses its vendored sanitizer')

  const mermaidSource = await fetch(new URL('/@fs' + root + 'node_modules/@slidev/client/modules/mermaid.ts', base))
  assert.ok(mermaidSource.ok)
  const mermaidTransformed = await mermaidSource.text()
  assert.doesNotMatch(mermaidTransformed, /mermaid\.esm(?:\.min)?\.mjs/, 'Mermaid must import patched external dependencies')
  const mermaidImport = mermaidTransformed.match(/import\s+\w+\s+from\s+["']([^"']*mermaid[^"']*)["']/)
  assert.ok(mermaidImport)

  browser = await chromium.launch({ headless: true })
  page = await browser.newPage()
  page.on('pageerror', error => console.error('Browser error:', error.message))
  page.on('console', event => { if (event.type() === 'warning') console.error('Browser warning:', event.text()) })
  await page.goto(base + '/1', { waitUntil: 'networkidle' })
  await page.locator('[data-slidev-no="1"] .slidev-layout').waitFor({ state: 'visible' })
  const slides = parseSync(readFileSync(root + 'lectures/05.md', 'utf8'), 'lectures/05.md').slides
  const diagram = slides.findIndex(slide => slide.content.includes('```mermaid')) + 1
  assert.ok(diagram > 0)
  await page.goto(`${base}/${diagram}`, { waitUntil: 'networkidle' })
  await page.locator(`[data-slidev-no="${diagram}"] .slidev-layout svg.lesson-figure`).first().waitFor({ state: 'visible' })
  assert.doesNotMatch(await page.locator(`[data-slidev-no="${diagram}"] .slidev-layout`).innerText(), /An error occurred on this slide/)
  const result = await page.evaluate(async urls => {
    const purifier = (await import(urls.purifier)).default
    const mermaid = (await import(urls.mermaid)).default
    mermaid.initialize({ startOnLoad: false })
    const graph = await mermaid.render('course-security-smoke', 'flowchart LR; A-->B')
    const graphDocument = new DOMParser().parseFromString(graph.svg, 'image/svg+xml')
    const mermaidNodes = graphDocument.querySelectorAll('g.node').length
    const root = document.createElement('div')
    root.innerHTML = '<figure><span class="trigger"></span><img onclick="0"></figure>'
    document.body.append(root)
    const removed = root.firstElementChild
    purifier.addHook('uponSanitizeElement', node => {
      if (node instanceof Element && node.classList.contains('trigger')) removed.remove()
    })
    try {
      purifier.sanitize(root, { IN_PLACE: true })
      return { version: purifier.version, mermaidNodes, detachedHandlerRemoved: !removed.querySelector('img').hasAttribute('onclick') }
    } finally {
      purifier.removeAllHooks()
      root.remove()
    }
  }, { purifier: new URL(purifierImport[1], base).href, mermaid: new URL(mermaidImport[1], base).href })
  assert.equal(result.version, '3.4.17')
  assert.equal(result.mermaidNodes, 2, 'The externalized Mermaid entry must render a real graph')
  assert.equal(result.detachedHandlerRemoved, true, 'Detached subtrees must be neutralized (GHSA-mrv2-3pqr-j5jr)')
  console.log(JSON.stringify({ mcpRequestsBlocked: 6, monacoPurifier: result.version, mermaidEntry: 'core', detachedSubtreeRegression: 'passed', preview: 'passed' }))
} catch (error) {
  console.error(output.slice(-6000))
  if (page) {
    mkdirSync(root + 'tmp', { recursive: true })
    await page.screenshot({ path: root + 'tmp/toolchain-security-failure.png' }).catch(() => {})
    console.error((await page.locator('body').innerText()).slice(0, 1500))
  }
  throw error
} finally {
  if (browser) await browser.close()
  server.kill('SIGTERM')
  if (server.exitCode === null && server.signalCode === null)
    await new Promise(resolve => server.once('exit', resolve))
}
