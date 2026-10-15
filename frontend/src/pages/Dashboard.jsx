import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listIssues, trend, severity, topIssues, updateIssue, deleteIssue } from '../api'
import Filters from '../components/Filters'
import { TrendChart, SeverityChart } from '../components/Charts'
import Benchmark from '../components/Benchmark'
import AppSettings from '../components/AppSettings'
import FireTestError from '../components/FireTestError'

export default function Dashboard({ app, appRecord, onAppRecordChanged }) {
  const [issues, setIssues] = useState([])
  const [trendData, setTrendData] = useState(null)
  const [sevData, setSevData] = useState([])
  const [top, setTop] = useState([])
  const [filters, setFilters] = useState({ severity: '', status: '', hours: 24 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!app) return
    setLoading(true)
    Promise.all([
      listIssues(app, { severity: filters.severity, status: filters.status, limit: 100 }),
      trend(app, filters.hours),
      severity(app, filters.hours),
      topIssues(app, 5),
    ])
      .then(([i, t, s, tp]) => {
        setIssues(i); setTrendData(t); setSevData(s); setTop(tp)
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false))

    const t = setInterval(() => {
      listIssues(app, filters).then(setIssues).catch(() => {})
      trend(app, filters.hours).then(setTrendData).catch(() => {})
    }, 5000)
    return () => clearInterval(t)
  }, [app, filters.severity, filters.status, filters.hours])

  const totalEvents = trendData?.hours.reduce((acc, h) => acc + h.total, 0) || 0
  const unresolved = issues.filter(i => i.status === 'unresolved').length
  const spiking = issues.filter(i => i.is_spiking).length

  return (
    <>
      <div className="header">
        <h2>Dashboard · {app}</h2>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <FireTestError app={app} apiKey={appRecord?.api_key} onFired={() => {
            listIssues(app, filters).then(setIssues).catch(() => {})
          }} />
          <div className="meta">Auto-refreshing every 5s</div>
        </div>
      </div>

      <Filters
        severity={filters.severity}
        status={filters.status}
        hours={filters.hours}
        onChange={partial => setFilters(f => ({ ...f, ...partial }))}
      />

      <div className="cards">
        <div className="card"><div className="label">Events in window</div><div className="value">{totalEvents}</div></div>
        <div className="card"><div className="label">Issues</div><div className="value">{issues.length}</div></div>
        <div className="card"><div className="label">Unresolved</div><div className="value">{unresolved}</div></div>
        <div className="card"><div className="label">Spiking now</div><div className="value" style={{ color: spiking ? '#f87171' : '#e5e7eb' }}>{spiking}</div></div>
      </div>

      <Benchmark />

      <AppSettings app={app} appRecord={appRecord} onSaved={onAppRecordChanged} />

      <div className="chart-row">
        <div className="panel">
          <h3>Errors over time (by severity)</h3>
          <TrendChart data={trendData} />
        </div>
        <div className="panel">
          <h3>Severity breakdown</h3>
          <SeverityChart data={sevData} />
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 24 }}>
        <h3>Top 5 noisiest issues</h3>
        {top.length === 0 ? <div className="empty">No issues yet</div> : (
          <table>
            <thead><tr><th>#</th><th>Issue</th><th>Severity</th><th>Count</th><th></th></tr></thead>
            <tbody>
              {top.map((t, i) => (
                <tr key={t.issue_id}>
                  <td>{i + 1}</td>
                  <td><Link to={`/issue/${t.issue_id}`}>{t.exception_type}: {t.message.slice(0, 80)}</Link></td>
                  <td><span className={`sev sev-${t.severity}`}>{t.severity}</span></td>
                  <td>{t.count}</td>
                  <td><span className={`status-badge status-${t.status}`}>{t.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <IssuesTable
        issues={issues}
        loading={loading}
        onRefresh={() => listIssues(app, filters).then(setIssues).catch(() => {})}
      />
    </>
  )
}

function IssuesTable({ issues, loading, onRefresh }) {
  async function toggleStatus(issue) {
    const next = issue.status === 'resolved' ? 'unresolved' : 'resolved'
    await updateIssue(issue.issue_id, { status: next, note: '' })
    onRefresh && onRefresh()
  }
  async function remove(issue) {
    if (!window.confirm(`Delete issue "${issue.exception_type}"? This removes the grouped issue; raw events TTL out.`)) return
    await deleteIssue(issue.issue_id)
    onRefresh && onRefresh()
  }

  return (
    <div className="panel">
      <h3>All issues · inline Update + Delete</h3>
      {loading ? <div className="spinner">Loading…</div> : issues.length === 0 ? (
        <div className="empty">No issues match the current filters</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Severity</th><th>Issue</th><th>Count</th><th>Last seen</th><th>Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {issues.map(i => (
              <tr key={i.issue_id}>
                <td><span className={`sev sev-${i.severity}`}>{i.severity}</span></td>
                <td>
                  <Link to={`/issue/${i.issue_id}`}>
                    <strong>{i.exception_type}</strong>: {i.message.slice(0, 120)}
                  </Link>
                  {i.is_spiking && <span className="spike-badge">SPIKE</span>}
                </td>
                <td>{i.total_count}</td>
                <td>{i.last_seen ? new Date(i.last_seen).toLocaleString() : '—'}</td>
                <td><span className={`status-badge status-${i.status}`}>{i.status}</span></td>
                <td style={{ whiteSpace: 'nowrap' }}>
                  <button
                    className="btn btn-ghost"
                    onClick={() => toggleStatus(i)}
                    style={{ padding: '4px 10px', fontSize: 12, marginRight: 6 }}
                    title={`Mark as ${i.status === 'resolved' ? 'unresolved' : 'resolved'}`}
                  >
                    {i.status === 'resolved' ? '↩ Reopen' : '✓ Resolve'}
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => remove(i)}
                    style={{ padding: '4px 10px', fontSize: 12 }}
                    title="Delete this issue"
                  >
                    🗑
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
