import { useEffect, useState } from 'react'
import { updateApp } from '../api'

/** Edit the webhook URL for the current app. Fires a POST on brand-new issues. */
export default function AppSettings({ app, appRecord, onSaved }) {
  const [url, setUrl] = useState('')
  const [saving, setSaving] = useState(false)
  const [status, setStatus] = useState('')

  useEffect(() => {
    setUrl(appRecord?.webhook_url || '')
    setStatus('')
  }, [app, appRecord])

  async function save() {
    setSaving(true)
    setStatus('')
    try {
      await updateApp(app, { webhook_url: url })
      setStatus(url ? 'Saved. New issues will POST to this URL.' : 'Saved. Webhook disabled.')
      onSaved && onSaved()
    } catch (e) {
      setStatus('Save failed: ' + (e.response?.data?.error || e.message))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <h3>Webhook (fires once per brand-new issue)</h3>
      <div style={{ color: '#9ca3af', fontSize: 13, marginBottom: 10 }}>
        Paste a URL from <a href="https://webhook.site" target="_blank" rel="noreferrer">webhook.site</a>, Slack, or your own HTTP endpoint.
        LogVault will POST the issue details there the first time it sees a new error type.
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          placeholder="https://webhook.site/your-unique-id"
          value={url}
          onChange={e => setUrl(e.target.value)}
          style={{
            flex: 1,
            background: '#1f2937',
            color: '#e5e7eb',
            border: '1px solid #374151',
            padding: '8px 12px',
            borderRadius: 6,
            fontSize: 14,
            fontFamily: 'ui-monospace, Menlo, monospace',
          }}
        />
        <button className="btn" onClick={save} disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
      {status && (
        <div style={{ color: status.startsWith('Save failed') ? '#f87171' : '#6ee7b7', fontSize: 13, marginTop: 8 }}>
          {status}
        </div>
      )}
    </div>
  )
}
