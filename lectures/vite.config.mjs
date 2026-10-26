import { fileURLToPath } from 'node:url'

export default {
  resolve: {
    alias: [
      // Slidev imports Mermaid's self-contained bundle, which embeds an older
      // sanitizer/KaTeX. The official core entry imports our patched packages.
      {
        find: 'mermaid/dist/mermaid.esm.mjs',
        replacement: fileURLToPath(import.meta.resolve('mermaid')),
      },
      // Monaco 0.57.0 vendors DOMPurify 3.4.15 instead of importing its dependency.
      // Use the patched package for this internal import in dev and static builds.
      {
        find: './dompurify/dompurify.js',
        replacement: fileURLToPath(import.meta.resolve('dompurify')),
      },
    ],
  },
  plugins: [
    {
      name: 'course-optimize-mermaid-core',
      enforce: 'post',
      config(config) {
        // Slidev excludes its self-contained Mermaid bundle from optimization.
        // The core entry needs CommonJS dependencies (such as dayjs) optimized.
        config.optimizeDeps ??= {}
        config.optimizeDeps.exclude = config.optimizeDeps.exclude?.filter(id => id !== 'mermaid')
        config.optimizeDeps.include = [...(config.optimizeDeps.include || []), 'mermaid']
      },
    },
    {
      name: 'course-disable-unused-mcp',
      enforce: 'pre',
      configureServer(server) {
        // The course uses preview/export, not Slidev's HTTP editing tools.
        // Reject before the SDK parses any tool arguments. SDK upgrades alone
        // do not enable its new request/element or audience checks.
        server.middlewares.use((request, response, next) => {
          const pathname = request.url?.split('?')[0]?.replace(/\/$/, '')
          if (pathname !== '/__mcp') return next()
          response.statusCode = 403
          response.setHeader('Content-Type', 'text/plain; charset=utf-8')
          response.end('The course preview does not expose MCP editing tools.\n')
        })
      },
    },
  ],
}
