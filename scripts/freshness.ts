// Flags tools in tools.json that need a human look. A flag is a signal, not a verdict:
// a quiet repository can be finished, and an active one can still be the wrong choice.
import { appendFileSync } from 'node:fs'
import { readTools } from './registry.ts'

// CONTRIBUTING.md asks for a closer look at 30 days when a tool is admitted; listed tools are flagged at 90,
// so a project that releases every few weeks or months does not turn the nightly run red.
const PUSH_DAYS = 90
const RELEASE_DAYS = 365
const REVIEW_DAYS = 180

interface Repo {
  full_name: string
  archived: boolean
  pushed_at: string
}
interface Release {
  published_at: string
  prerelease: boolean
}
interface Issue {
  number: number
  title: string
  pull_request?: unknown
}
type Failure = { status: number }

const token = process.env.GITHUB_TOKEN
const headers: Record<string, string> = {
  Accept: 'application/vnd.github+json',
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
}
const days = (iso: string): number => Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000)

async function api<T>(path: string): Promise<T | Failure> {
  const res = await fetch(`https://api.github.com/${path}`, { headers })
  return res.ok ? ((await res.json()) as T) : { status: res.status }
}
const failed = (value: unknown): value is Failure => typeof value === 'object' && value !== null && 'status' in value

const rows: { id: string; repo: string; flags: string[] }[] = []
for (const tool of readTools()) {
  const flags: string[] = []
  const repo = await api<Repo>(`repos/${tool.repo}`)
  if (failed(repo)) {
    flags.push(`repository lookup failed (HTTP ${repo.status}): moved or deleted?`)
  } else {
    if (repo.archived) flags.push('ARCHIVED')
    if (repo.full_name.toLowerCase() !== tool.repo.toLowerCase()) flags.push(`renamed to ${repo.full_name}`)
    if (!tool.stable_exception && days(repo.pushed_at) > PUSH_DAYS) flags.push(`no push for ${days(repo.pushed_at)} days`)
    // The newest release, pre-releases included: `releases/latest` skips them, and a line that is only in pre-release
    // (detekt 2.0) would look abandoned.
    const releases = await api<Release[]>(`repos/${tool.repo}/releases?per_page=1`)
    const release = failed(releases) ? undefined : releases[0]
    if (release && !tool.stable_exception && days(release.published_at) > RELEASE_DAYS) {
      flags.push(`last release ${days(release.published_at)} days ago${release.prerelease ? ' (pre-release)' : ''}`)
    }
  }
  if (days(tool.last_reviewed) > REVIEW_DAYS) flags.push(`last reviewed ${days(tool.last_reviewed)} days ago`)
  rows.push({ id: tool.id, repo: tool.repo, flags })
}

const flagged = rows.filter((row) => row.flags.length > 0)
const report = [
  '## Tool freshness',
  '',
  'A flag is a signal for a human review, not a verdict. See CONTRIBUTING.md.',
  '',
  flagged.length === 0 ? 'No tool needs attention.' : '| Tool | Flags |\n|---|---|',
  ...flagged.map((row) => `| [${row.id}](https://github.com/${row.repo}) | ${row.flags.join('; ')} |`),
].join('\n')
console.log(report)
if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, `${report}\n`)

// A red cron run is easy to miss, so the report goes to one tracking issue:
// opened or updated when something is flagged, closed when nothing is.
const TITLE = 'Tool freshness report'
const slug = process.env.GITHUB_REPOSITORY
if (slug && token) {
  const send = (path: string, method: string, body: object) =>
    fetch(`https://api.github.com/${path}`, { method, headers, body: JSON.stringify(body) })
  const open = await api<Issue[]>(`repos/${slug}/issues?state=open&per_page=100`)
  const existing = failed(open) ? undefined : open.find((issue) => issue.title === TITLE && !issue.pull_request)
  if (flagged.length > 0 && existing) await send(`repos/${slug}/issues/${existing.number}`, 'PATCH', { body: report })
  else if (flagged.length > 0) await send(`repos/${slug}/issues`, 'POST', { title: TITLE, body: report })
  else if (existing) await send(`repos/${slug}/issues/${existing.number}`, 'PATCH', { state: 'closed', state_reason: 'completed' })
}
process.exit(flagged.length > 0 ? 1 : 0)
