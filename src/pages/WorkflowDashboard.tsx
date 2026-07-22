import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface WorkflowRun {
  status: string
  conclusion: string | null
  created_at: string
}

interface WorkflowData {
  name: string
  runs: WorkflowRun[]
}

const WORKFLOWS = [
  { name: 'Generate NBA News', key: 'nba-news' },
  { name: 'Generate Stock Market News', key: 'stock-news' },
  { name: 'Generate Trade Watcher Data', key: 'trade-watcher' },
  { name: 'Ticker Scout', key: 'ticker-scout' },
  { name: 'Auto-Monitor and Fix Workflows', key: 'monitor-and-fix' },
  { name: 'Deploy to GitHub Pages', key: 'deploy' },
]

const API_BASE = 'https://api.github.com/repos/eyal270704-lab/websites/actions/workflows'

export default function WorkflowDashboard() {
  const [workflows, setWorkflows] = useState<WorkflowData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchAll() {
      try {
        const results = await Promise.all(
          WORKFLOWS.map(async (wf) => {
            const res = await fetch(
              `${API_BASE}/${wf.key}.yml/runs?per_page=5&exclude_pull_requests=true`
            )
            if (!res.ok) throw new Error(`Failed to fetch ${wf.name}`)
            const data = await res.json()
            return {
              name: wf.name,
              runs: (data.workflow_runs || []).map((r: any) => ({
                status: r.status,
                conclusion: r.conclusion,
                created_at: r.created_at,
              })),
            }
          })
        )
        setWorkflows(results)
      } catch (e: any) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [])

  return (
    <div className="min-h-screen text-text-main">
      <div className="mx-auto max-w-4xl px-5 py-8 md:px-8">
        <header className="mb-10 mt-2 animate-fade-in">
          <Link to="/" className="inline-flex items-center gap-2 text-sm font-medium text-text-muted transition-colors hover:text-text-main">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Newsroom
          </Link>
          <h1 className="mt-6 text-3xl font-extrabold tracking-tight md:text-4xl">Pipeline status</h1>
          <p className="mt-2 text-sm text-text-muted">The last five runs of every agent and deploy workflow, live from GitHub Actions.</p>
        </header>

        {loading && <p className="text-text-muted">Loading workflow data…</p>}
        {error && <p className="text-red-300">Error: {error}</p>}

        <div className="space-y-3">
          {workflows.map((wf) => (
            <WorkflowBlock key={wf.name} workflow={wf} />
          ))}
        </div>

        <footer className="mt-12 border-t border-white/[0.06] py-8 text-center text-xs text-text-faint">
          Data from the GitHub Actions API · public, no auth required
        </footer>
      </div>
    </div>
  )
}

function WorkflowBlock({ workflow }: { workflow: WorkflowData }) {
  return (
    <div className="surface-card p-5">
      <h2 className="mb-3 text-base font-semibold tracking-tight">{workflow.name}</h2>
      <div className="flex flex-wrap gap-2">
        {workflow.runs.length === 0 && (
          <span className="text-sm text-text-faint">No runs found</span>
        )}
        {workflow.runs.map((run, i) => (
          <RunBadge key={i} run={run} />
        ))}
      </div>
    </div>
  )
}

function RunBadge({ run }: { run: WorkflowRun }) {
  const [showTime, setShowTime] = useState(false)

  const isRunning = run.status === 'in_progress' || run.status === 'queued'
  const success = run.conclusion === 'success'
  const icon = isRunning ? '⏳' : success ? '✓' : '✗'

  const bgColor = isRunning
    ? 'bg-amber-400/15 border-amber-400/40 text-amber-300'
    : success
      ? 'bg-emerald-400/15 border-emerald-400/40 text-emerald-300'
      : 'bg-red-400/15 border-red-400/40 text-red-300'

  const time = new Date(run.created_at).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className="relative">
      <button
        onClick={() => setShowTime(!showTime)}
        className={`flex h-9 w-9 items-center justify-center rounded-lg border ${bgColor} text-base font-bold transition-transform hover:scale-110`}
      >
        {icon}
      </button>
      {showTime && (
        <div className="absolute left-1/2 top-11 z-10 -translate-x-1/2 whitespace-nowrap rounded-md border border-white/15 bg-surface-2 px-2 py-1 text-xs text-text-muted">
          {time}
        </div>
      )}
    </div>
  )
}
