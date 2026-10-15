import { useState } from 'react'
import { createApp } from '../api'

/** Modal form for registering a new application (Create in CRUD). */
export default function NewAppModal({ onClose, onCreated }) {
  const [appName, setAppName] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [webhookUrl, setWebhookUrl] = useState('')
  const [err, setErr] = useState('')
  const [saving, setSaving] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setSaving(true)
    setErr('')
    try {
      const payload = { app_name: appName.trim() }
      if (apiKey.trim()) payload.api_key = apiKey.trim()
      if (webhookUrl.trim()) payload.webhook_url = webhookUrl.trim()
      const created = await createApp(payload)
      onCreated && onCreated(created)
      onClose()
    } catch (e) {
      setErr(e.response?.data?.error || e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 50,
      }}
    >
      <form
        onClick={e => e.stopPropagation()}
        onSubmit={submit}
        className="panel"
        style={{ minWidth: 420, maxWidth: 520, background: '#141821' }}
      >
        <h3>Register new application</h3>
        <div style={{ color: '#9ca3af', fontSize: 13, marginBottom: 14 }}>
          Give the app a name. If you leave the API key blank, LogVault generates one.
        </div>

        <label style={{ fontSize: 12, color: '#9ca3af' }}>App name <span style={{ color: '#f87171' }}>*</span></label>
        <input
          autoFocus required value={appName} onChange={e => setAppName(e.target.value)}
          placeholder="e.g. billing-service"
          style={inputStyle}
        />

        <label style={{ fontSize: 12, color: '#9ca3af', marginTop: 10, display: 'block' }}>API key (optional)</label>
        <input
          value={apiKey} onChange={e => setApiKey(e.target.value)}
          placeholder="leave empty to auto-generate"
          style={inputStyle}
        />

        <label style={{ fontSize: 12, color: '#9ca3af', marginTop: 10, display: 'block' }}>Webhook URL (optional)</label>
        <input
          value={webhookUrl} onChange={e => setWebhookUrl(e.target.value)}
          placeholder="https://webhook.site/..."
          style={inputStyle}
        />

        {err && <div style={{ color: '#f87171', fontSize: 13, marginTop: 10 }}>{err}</div>}

        <div style={{ display: 'flex', gap: 8, marginTop: 16, justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn" disabled={saving || !appName.trim()}>
            {saving ? 'Creating…' : 'Create app'}
          </button>
        </div>
      </form>
    </div>
  )
}

const inputStyle = {
  width: '100%',
  background: '#1f2937',
  color: '#e5e7eb',
  border: '1px solid #374151',
  padding: '8px 12px',
  borderRadius: 6,
  fontSize: 14,
  fontFamily: 'ui-monospace, Menlo, monospace',
  marginTop: 4,
}
