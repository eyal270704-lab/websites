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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-900 text-white p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 pt-4">
          <Link to="/" className="text-gray-400 hover:text-white text-sm mb-4 inline-block">
            ← Back to Hub
          </Link>
          <h1 className="text-3xl font-bold">Workflow Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Latest 5 runs per workflow</p>
        </header>

        {loading && <p className="text-gray-400">Loading workflow data...</p>}
        {error && <p className="text-red-400">Error: {error}</p>}

        <div className="space-y-4">
          {workflows.map((wf) => (
            <WorkflowBlock key={wf.name} workflow={wf} />
          ))}
        </div>

        <footer className="mt-10 text-center text-gray-600 text-xs">
          Data from GitHub Actions API (public, no auth required)
        </footer>
      </div>
    </div>
  )
}

function WorkflowBlock({ workflow }: { workflow: WorkflowData }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
      <h2 className="text-lg font-semibold mb-3">{workflow.name}</h2>
      <div className="flex gap-2">
        {workflow.runs.length === 0 && (
          <span className="text-gray-500 text-sm">No runs found</span>
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
    ? 'bg-yellow-500/20 border-yellow-500/40 text-yellow-400'
    : success
      ? 'bg-green-500/20 border-green-500/40 text-green-400'
      : 'bg-red-500/20 border-red-500/40 text-red-400'

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
        className={`w-10 h-10 rounded-lg border ${bgColor} font-bold text-lg flex items-center justify-center hover:scale-110 transition-transform`}
      >
        {icon}
      </button>
      {showTime && (
        <div className="absolute top-12 left-1/2 -translate-x-1/2 bg-gray-800 border border-gray-600 text-xs text-gray-200 rounded px-2 py-1 whitespace-nowrap z-10">
          {time}
        </div>
      )}
    </div>
  )
}
