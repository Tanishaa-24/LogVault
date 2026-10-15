export default function Filters({ severity, status, hours, onChange }) {
  return (
    <div className="filters">
      <label>Severity:</label>
      <select value={severity} onChange={e => onChange({ severity: e.target.value })}>
        <option value="">All</option>
        <option value="FATAL">FATAL</option>
        <option value="ERROR">ERROR</option>
        <option value="WARNING">WARNING</option>
        <option value="INFO">INFO</option>
        <option value="DEBUG">DEBUG</option>
      </select>
      <label>Status:</label>
      <select value={status} onChange={e => onChange({ status: e.target.value })}>
        <option value="">All</option>
        <option value="unresolved">Unresolved</option>
        <option value="resolved">Resolved</option>
      </select>
      <label>Window:</label>
      <select value={hours} onChange={e => onChange({ hours: Number(e.target.value) })}>
        <option value={1}>Last 1h</option>
        <option value={6}>Last 6h</option>
        <option value={24}>Last 24h</option>
        <option value={72}>Last 3d</option>
        <option value={168}>Last 7d</option>
      </select>
    </div>
  )
}
