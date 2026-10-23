// Flags tools in tools.json that need a human look. A flag is a signal, not a verdict:
// a quiet repository can be finished, and an active one can still be the wrong choice.
import { appendFileSync, readFileSync } from 'node:fs'

// Matches CONTRIBUTING.md: activity older than 30 days is a reason to look closer.
const PUSH_DAYS = 30
const RELEASE_DAYS = 365
const REVIEW_DAYS = 180
const { tools } = JSON.parse(readFileSync('tools.json', 'utf8'))
const token = process.env.GITHUB_TOKEN
const headers = { Accept: 'application/vnd.github+json', ...(token && { Authorization: `Bearer ${token}` }) }
const days = (iso) => Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000)

async function api(path) {
  const res = await fetch(`https://api.github.com/${path}`, { headers })
  return res.ok ? res.json() : { status: res.status }
}

const rows = []
for (const tool of tools) {
  const flags = []
  const repo = await api(`repos/${tool.repo}`)
  if (repo.status) {
    flags.push(`repository lookup failed (HTTP ${repo.status}): moved or deleted?`)
  } else {
    if (repo.archived) flags.push('ARCHIVED')
    if (repo.full_name.toLowerCase() !== tool.repo.toLowerCase()) flags.push(`renamed to ${repo.full_name}`)
    if (!tool.stable_exception && days(repo.pushed_at) > PUSH_DAYS) flags.push(`no push for ${days(repo.pushed_at)} days`)
    const release = await api(`repos/${tool.repo}/releases/latest`)
    if (!release.status && !tool.stable_exception && days(release.published_at) > RELEASE_DAYS) flags.push(`last release ${days(release.published_at)} days ago`)
  }
  if (days(tool.last_reviewed) > REVIEW_DAYS) flags.push(`last reviewed ${days(tool.last_reviewed)} days ago`)
  rows.push({ id: tool.id, repo: tool.repo, flags })
}

const flagged = rows.filter((row) => row.flags.length > 0)
const lines = [
  '## Tool freshness',
  '',
  'A flag is a signal for a human review, not a verdict. See CONTRIBUTING.md.',
  '',
  flagged.length === 0 ? 'No tool needs attention.' : '| Tool | Flags |\n|---|---|',
  ...flagged.map((row) => `| [${row.id}](https://github.com/${row.repo}) | ${row.flags.join('; ')} |`),
]
const report = lines.join('\n')
console.log(report)
if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, `${report}\n`)
// A red cron run is easy to miss, so the report goes to one tracking issue:
// opened or updated when something is flagged, closed when nothing is.
const TITLE = 'Tool freshness report'
const slug = process.env.GITHUB_REPOSITORY
if (slug && token) {
  const send = (path, method, body) =>
    fetch(`https://api.github.com/${path}`, { method, headers, body: JSON.stringify(body) })
  const open = await api(`repos/${slug}/issues?state=open&per_page=100`)
  const existing = Array.isArray(open) ? open.find((issue) => issue.title === TITLE && !issue.pull_request) : undefined
  if (flagged.length > 0 && existing) await send(`repos/${slug}/issues/${existing.number}`, 'PATCH', { body: report })
  else if (flagged.length > 0) await send(`repos/${slug}/issues`, 'POST', { title: TITLE, body: report })
  else if (existing) await send(`repos/${slug}/issues/${existing.number}`, 'PATCH', { state: 'closed', state_reason: 'completed' })
}
process.exit(flagged.length > 0 ? 1 : 0)
