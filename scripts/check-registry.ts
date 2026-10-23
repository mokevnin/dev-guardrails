// Validates tools.json and checks that README.md and the registry agree.
import { readFileSync } from 'node:fs'
import { readTools, type Tool } from './registry.ts'

const REQUIRED = ['id', 'repo', 'category', 'last_reviewed', 'sources', 'rationale', 'limitations'] as const

const tools = readTools()
const readme = readFileSync('README.md', 'utf8')
const errors: string[] = []
const ids = new Set<string>()

for (const tool of tools) {
  const name = tool.id ?? '(no id)'
  for (const field of REQUIRED) {
    const value: Tool[typeof field] | undefined = tool[field]
    if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) {
      errors.push(`${name}: missing "${field}"`)
    }
  }
  if (ids.has(tool.id)) errors.push(`${name}: duplicate id`)
  ids.add(tool.id)
  if (!/^[\w.-]+\/[\w.-]+$/.test(tool.repo ?? '')) errors.push(`${name}: repo must be "owner/repo"`)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(tool.last_reviewed ?? '')) errors.push(`${name}: last_reviewed must be YYYY-MM-DD`)
  if (!readme.includes(`](https://github.com/${tool.repo})`)) errors.push(`${name}: README has no link to https://github.com/${tool.repo}`)
}

if (errors.length > 0) {
  console.error(errors.join('\n'))
  process.exit(1)
}
console.log(`tools.json: ${tools.length} tools OK`)
