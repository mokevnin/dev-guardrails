import { readFileSync } from 'node:fs'

export interface Tool {
  id: string
  name: string
  repo: string
  category: string
  last_reviewed: string
  sources: string[]
  rationale: string
  limitations: string
  details?: string
  stable_exception?: boolean
}

export function readTools(path = 'tools.json'): Tool[] {
  const registry = JSON.parse(readFileSync(path, 'utf8')) as { tools: Tool[] }
  return registry.tools
}
