// Validates tools.json against tools.schema.json and checks that README.md is generated from it.
import { readFileSync } from 'node:fs'
import { Ajv } from 'ajv'
import { readTools } from './registry.ts'
import { update } from './readme.ts'

const schema = JSON.parse(readFileSync('tools.schema.json', 'utf8')) as object
const registry = JSON.parse(readFileSync('tools.json', 'utf8')) as unknown
const ajv = new Ajv({ allErrors: true })
const validate = ajv.compile(schema)
const errors: string[] = []

if (!validate(registry)) {
  for (const error of validate.errors ?? []) errors.push(`tools.json${error.instancePath}: ${error.message}`)
}

const tools = errors.length === 0 ? readTools() : []
const ids = new Set<string>()
const repos = new Set<string>()
for (const tool of tools) {
  if (ids.has(tool.id)) errors.push(`${tool.id}: duplicate id`)
  if (repos.has(tool.repo.toLowerCase())) errors.push(`${tool.id}: duplicate repo ${tool.repo}`)
  ids.add(tool.id)
  repos.add(tool.repo.toLowerCase())
}

if (errors.length === 0) {
  const readme = readFileSync('README.md', 'utf8')
  if (update(readme, tools) !== readme) errors.push('README.md is out of date: run `npm run readme` and commit the result.')
}

if (errors.length > 0) {
  console.error(errors.join('\n'))
  process.exit(1)
}
console.log(`tools.json: ${tools.length} tools OK, README.md up to date`)
