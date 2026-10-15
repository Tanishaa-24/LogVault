import { useState } from 'react'
import { logEvent } from '../api'

/** A UI button that creates an issue (demonstrates CRUD Create for Issues). */
export default function FireTestError({ app, apiKey, onFired }) {
  const [firing, setFiring] = useState(false)
  const [last, setLast] = useState(null)

  const SAMPLES = [
    {
      severity: 'ERROR',
      message: "KeyError: 'checkout_token'",
      stack:
        'Traceback (most recent call last):\n' +
        '  File "/app/checkout.py", line 87, in finalize\n' +
        '    token = payload["checkout_token"]\n' +
        "KeyError: 'checkout_token'",
    },
    {
      severity: 'ERROR',
      message: 'ValueError: invalid literal for int() with base 10: \'abc\'',
      stack:
        'Traceback (most recent call last):\n' +
        '  File "/app/pricing.py", line 42, in to_cents\n' +
        '    return int(amount)\n' +
        'ValueError: invalid literal for int() with base 10: \'abc\'',
    },
    {
      severity: 'FATAL',
      message: 'ConnectionError: Lost connection to primary db-node-1',
      stack:
        'Traceback (most recent call last):\n' +
        '  File "/app/db.py", line 203, in query\n' +
        '    cursor.execute(sql)\n' +
        'ConnectionError: Lost connection to primary db-node-1',
    },
    {
      severity: 'WARNING',
      message: 'Slow endpoint: /api/report took 3400ms',
      stack: '(no stack)',
    },
  ]

  async function fire() {
    const sample = SAMPLES[Math.floor(Math.random() * SAMPLES.length)]
    setFiring(true)
    try {
      const res = await logEvent(apiKey, { app, ...sample })
      setLast({ ...res, severity: sample.severity, message: sample.message })
      onFired && onFired()
    } catch (e) {
      setLast({ error: e.response?.data?.error || e.message })
    } finally {
      setFiring(false)
    }
  }

  return (
    <div style={{ display: 'inline-block' }}>
      <button className="btn" onClick={fire} disabled={firing || !apiKey}
        title="Create a fake exception event using this app's API key"
        style={{ background: '#b91c1c' }}>
        {firing ? 'Firing…' : '⚡ Fire test error'}
      </button>
      {last && !last.error && (
        <div style={{ color: '#6ee7b7', fontSize: 12, marginTop: 6 }}>
          {last.is_new_issue ? '✨ New issue created' : '↻ Repeated existing issue'} · {last.issue_id}
        </div>
      )}
      {last?.error && (
        <div style={{ color: '#f87171', fontSize: 12, marginTop: 6 }}>Error: {last.error}</div>
      )}
    </div>
  )
}
