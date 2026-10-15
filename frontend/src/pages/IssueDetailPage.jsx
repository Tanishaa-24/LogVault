import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getIssue, updateIssue, deleteIssue } from '../api'
import Sparkline from '../components/Sparkline'

export default function IssueDetailPage() {
  const { id } = useParams()
  const nav = useNavigate()
  const [data, setData] = useState(null)
  const [note, setNote] = useState('')
  const [status, setStatus] = useState('unresolved')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    getIssue(id).then(d => {
      setData(d)
      setNote(d.issue.note || '')
      setStatus(d.issue.status || 'unresolved')
    })
  }, [id])

  if (!data) return <div className="spinner">Loading…</div>
  const { issue, events, sparkline } = data

  async function save() {
    setSaving(true)
    try {
      await updateIssue(id, { status, note })
      const fresh = await getIssue(id)
      setData(fresh)
    } finally {
      setSaving(false)
    }
  }

  async function remove() {
    if (!window.confirm('Delete this issue? Events will remain until TTL expires.')) return
    await deleteIssue(id)
    nav('/')
  }

  return (
    <>
      <div className="header">
        <div>
          <Link to="/">← Back</Link>
          <h2 style={{ margin: '8px 0 0' }}>
            <span className={`sev sev-${issue.severity}`}>{issue.severity}</span>{' '}
            {issue.exception_type}
          </h2>
          <div className="meta">
            {issue.app} · First seen {new Date(issue.first_seen).toLocaleString()} · Last seen {new Date(issue.last_seen).toLocaleString()}
          </div>
        </div>
        <div>
          <Sparkline data={sparkline} color="#f59e0b" />
          <div className="meta" style={{ textAlign: 'right' }}>Last 24h</div>
        </div>
      </div>

      <div className="panel" style={{ marginBottom: 16 }}>
        <h3>Message</h3>
        <div style={{ padding: '4px 0' }}>{issue.message}</div>
        <h3 style={{ marginTop: 16 }}>Deepest frame (used for grouping)</h3>
        <div className="stack">{issue.first_frame}</div>
      </div>

      <div className="panel" style={{ marginBottom: 16 }}>
        <h3>Issue management</h3>
        <div style={{ marginBottom: 10 }}>
          <label style={{ marginRight: 10 }}>Status:</label>
          <select value={status} onChange={e => setStatus(e.target.value)}
            style={{ background: '#1f2937', color: '#e5e7eb', border: '1px solid #374151', padding: '6px 10px', borderRadius: 6 }}>
            <option value="unresolved">Unresolved</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
        <label>Developer note:</label>
        <textarea className="textarea" value={note} onChange={e => setNote(e.target.value)}
          placeholder="Root cause, fix PR link, workaround, etc." />
        <div style={{ marginTop: 10, display: 'flex', gap: 10 }}>
          <button className="btn" onClick={save} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button className="btn btn-danger" onClick={remove}>Delete issue</button>
        </div>
      </div>

      <div className="panel">
        <h3>Recent events ({events.length})</h3>
        {events.length === 0 ? (
          <div className="empty">No events (may have expired via TTL)</div>
        ) : (
          <table>
            <thead>
              <tr><th>Time</th><th>Severity</th><th>Message</th><th></th></tr>
            </thead>
            <tbody>
              {events.map(e => (
                <EventRow key={e.event_id} e={e} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}

function EventRow({ e }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <tr>
        <td style={{ fontSize: 12 }}>{new Date(e.event_time).toLocaleString()}</td>
        <td><span className={`sev sev-${e.severity}`}>{e.severity}</span></td>
        <td style={{ fontSize: 13 }}>{e.message.slice(0, 160)}</td>
        <td>
          <button className="btn btn-ghost" onClick={() => setOpen(o => !o)}>
            {open ? 'Hide stack' : 'Show stack'}
          </button>
        </td>
      </tr>
      {open && (
        <tr><td colSpan={4}><div className="stack">{e.stack || '(no stack provided)'}</div></td></tr>
      )}
    </>
  )
}
