import { readFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import { parseSync } from '@slidev/parser'
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs'

export async function checkSlidesPdf(source, pdf) {
  const expected = parseSync(readFileSync(source, 'utf8'), source).slides.length
  const task = getDocument({ data: new Uint8Array(readFileSync(pdf)), disableFontFace: true, useSystemFonts: true })
  try {
    const document = await task.promise
    if (document.numPages !== expected) throw new Error(`${pdf}: ${document.numPages} PDF pages for ${expected} source slides`)
    for (let index = 1; index <= document.numPages; index++) {
      const page = await document.getPage(index)
      const content = await page.getTextContent()
      const text = content.items.map(item => item.str ?? '').join(' ')
      if (/An error occurred on this slide|Check the terminal for more information/i.test(text)) throw new Error(`${pdf}: render error on page ${index}`)
    }
    console.log(`Checked ${pdf}: ${expected} pages, no render error pages`)
  } finally {
    await task.destroy()
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [source, pdf] = process.argv.slice(2)
  if (!source || !pdf) throw new Error('Usage: node scripts/check-slides-pdf.mjs SOURCE PDF')
  await checkSlidesPdf(source, pdf)
}
