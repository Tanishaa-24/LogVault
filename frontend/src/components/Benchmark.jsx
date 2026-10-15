import { useEffect, useState } from 'react'
import { throughput } from '../api'

/** Live ingest performance over the last 60 seconds. Polls every 2s. */
export default function Benchmark() {
  const [snap, setSnap] = useState(null)

  useEffect(() => {
    let alive = true
    const tick = () => throughput().then(d => alive && setSnap(d)).catch(() => {})
    tick()
    const t = setInterval(tick, 2000)
    return () => { alive = false; clearInterval(t) }
  }, [])

  if (!snap) return null

  const Cell = ({ label, value, hint }) => (
    <div style={{ flex: 1, minWidth: 140 }}>
      <div className="label">{label}</div>
      <div className="value" style={{ fontSize: 22 }}>{value}</div>
      {hint && <div style={{ color: '#6b7280', fontSize: 11, marginTop: 2 }}>{hint}</div>}
    </div>
  )

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        Live ingest performance
        <span style={{ fontSize: 11, color: '#9ca3af', fontWeight: 400 }}>
          · last {snap.window_seconds}s · updates every 2s
        </span>
      </h3>
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
        <Cell label="Events / second" value={snap.events_per_second} hint={`${snap.events_in_window} events in window`} />
        <Cell label="Avg write latency" value={`${snap.avg_latency_ms} ms`} hint="Flask + Cassandra round-trip" />
        <Cell label="P99 write latency" value={`${snap.p99_latency_ms} ms`} hint="99th percentile" />
        <Cell label="Lifetime events ingested" value={snap.lifetime_events.toLocaleString()} hint="Since backend start" />
      </div>
    </div>
  )
}
