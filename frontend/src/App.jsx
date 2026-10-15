import { useEffect, useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { listApps, deleteApp } from './api'
import Dashboard from './pages/Dashboard'
import IssueDetailPage from './pages/IssueDetailPage'
import NewAppModal from './components/NewAppModal'

export default function App() {
  const [apps, setApps] = useState([])
  const [current, setCurrent] = useState(null)
  const nav = useNavigate()

  const [showNewApp, setShowNewApp] = useState(false)

  const refreshApps = () => listApps().then(list => {
    setApps(list)
    if (list.length && !current) setCurrent(list[0].app_name)
  })

  useEffect(() => { refreshApps() }, [])

  const currentRecord = apps.find(a => a.app_name === current) || null

  async function handleDelete(appName, e) {
    e.stopPropagation()
    if (!window.confirm(`Delete app "${appName}" and all its issues? Events will TTL out.`)) return
    await deleteApp(appName)
    const next = apps.find(a => a.app_name !== appName)
    setCurrent(next ? next.app_name : null)
    refreshApps()
    nav('/')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Log<span>Vault</span></h1>
        <div className="section-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Applications</span>
          <button
            onClick={() => setShowNewApp(true)}
            title="Register a new app"
            style={{
              background: '#2563eb', color: '#fff', border: 0,
              borderRadius: 4, padding: '2px 8px', fontSize: 11, cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            + New
          </button>
        </div>
        <div className="app-list">
          {apps.map(a => (
            <div key={a.app_name} style={{ display: 'flex', alignItems: 'center' }}>
              <button
                className={a.app_name === current ? 'active' : ''}
                onClick={() => { setCurrent(a.app_name); nav('/') }}
                style={{ flex: 1 }}
              >
                {a.app_name}
              </button>
              <button
                onClick={e => handleDelete(a.app_name, e)}
                title={`Delete ${a.app_name}`}
                style={{
                  background: 'transparent', border: 0, color: '#6b7280',
                  cursor: 'pointer', padding: '4px 6px', fontSize: 14,
                }}
                onMouseEnter={e => (e.target.style.color = '#f87171')}
                onMouseLeave={e => (e.target.style.color = '#6b7280')}
              >
                🗑
              </button>
            </div>
          ))}
          {apps.length === 0 && <div className="meta">No apps registered</div>}
        </div>
        <div className="section-label">About</div>
        <div style={{ fontSize: 12, color: '#9ca3af', lineHeight: 1.5 }}>
          Write-optimized error tracking backed by Apache Cassandra.
          Events auto-expire via per-row TTL.
        </div>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={current ? <Dashboard app={current} appRecord={currentRecord} onAppRecordChanged={refreshApps} /> : (
            <div style={{ padding: 40, textAlign: 'center' }}>
              <div className="empty" style={{ marginBottom: 16 }}>No applications registered yet.</div>
              <button className="btn" onClick={() => setShowNewApp(true)}>+ Register your first app</button>
            </div>
          )} />
          <Route path="/issue/:id" element={<IssueDetailPage />} />
        </Routes>
      </main>
      {showNewApp && (
        <NewAppModal
          onClose={() => setShowNewApp(false)}
          onCreated={() => { refreshApps() }}
        />
      )}
    </div>
  )
}
