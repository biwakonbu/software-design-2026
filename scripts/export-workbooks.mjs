import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { createServer } from 'node:http'
import { join } from 'node:path'
import MarkdownIt from 'markdown-it'
import { chromium } from 'playwright'
const md = new MarkdownIt({ html: false, linkify: true })
const lessons = JSON.parse(readFileSync('docs/curriculum.json', 'utf8'))
const packages = ['noto-sans-jp', 'jetbrains-mono']
const css = packages.map(name => [400, ...(name==='noto-sans-jp'?[600,700]:[])].map(weight =>
  readFileSync(`node_modules/@fontsource/${name}/${weight}.css`, 'utf8')
  .replace(/url\(['"]?\.\/files\//g, `url('/font/${name}/`)).join('\n')).join('\n')
const style = `${css}
@page{size:A4;margin:19mm 18mm 21mm}body{font:16px/1.75 'Noto Sans JP',sans-serif;color:#172a40;margin:0}
h1{font-size:27px;line-height:1.4;color:#154b74;margin:0 0 24px}h2{font-size:20px;line-height:1.45;color:#087d80;margin:26px 0 12px}
h3{font-size:17px;margin:20px 0 8px}p{margin:12px 0}li{margin:6px 0}section{break-before:page}section:first-child{break-before:auto}
pre{font:13px/1.6 'JetBrains Mono','Noto Sans JP',monospace;border-left:3px solid #087d80;background:#f1f4f5;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere}
code{font:0.85em 'JetBrains Mono','Noto Sans JP',monospace;overflow-wrap:anywhere;font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0}pre code{font-size:inherit}table{border-collapse:collapse;width:100%;font-size:14px;margin:18px 0}td,th{padding:8px;border-bottom:1px solid #cbd7dd;text-align:left}th{color:#154b74}
a{color:#154b74;overflow-wrap:anywhere}h1,h2,h3{break-after:avoid}pre,table,tr{break-inside:avoid}.cover{padding-top:90px}.cover h1{font-size:40px}.cover p{font-size:19px}
`
mkdirSync('output/pdf', { recursive: true });mkdirSync('tmp/workbooks',{recursive:true})
let html = ''
const server=createServer((req,res)=>{
  if(req.url==='/'){res.setHeader('Content-Type','text/html;charset=utf-8');res.end(html);return}
  const match=req.url?.match(/^\/font\/(noto-sans-jp|jetbrains-mono)\/([a-zA-Z0-9_.-]+)$/)
  if(match){try{res.setHeader('Content-Type','font/woff2');res.end(readFileSync(join('node_modules/@fontsource',match[1],'files',match[2])));return}catch{}}
  res.writeHead(404);res.end()
})
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve))
const browser=await chromium.launch({headless:true});const page=await browser.newPage()
try {
  for (const [source,name,title] of [['exercises','student-workbook','学生向け演習'],['instructor','instructor-notes','教師用補足・公開解説']]) {
    const content=lessons.map(l=>`<section>${md.render(readFileSync(`${source}/${l.id}.md`,'utf8'))}</section>`).join('\n')
    html=`<!doctype html><html lang="ja"><meta charset="utf-8"><title>${title}</title><style>${style}</style><body><section class="cover"><h1>ソフトウェアデザイン<br>2026</h1><p>${title}</p><p>第2〜15回<br>情報システム学科 3年生　選択2単位</p><p>授業で案内する提出先・期限に従って使用する。<br>演習のフォルダ構成は本教材の推奨例。</p></section>${content}</body></html>`
    writeFileSync(`tmp/workbooks/${name}.html`,html)
    await page.goto(`http://127.0.0.1:${server.address().port}/`,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready)
    await page.pdf({path:`output/pdf/${name}.pdf`,format:'A4',printBackground:true,displayHeaderFooter:true,
      headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;padding:0 18mm;font-size:9px;color:#567082;display:flex;justify-content:space-between"><span>SOFTWARE DESIGN 2026</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',preferCSSPageSize:true})
    console.log(`Exported ${name}.pdf`)
  }
} finally { await browser.close();server.close() }
