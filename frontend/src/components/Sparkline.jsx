export default function Sparkline({ data = [], color = '#60a5fa' }) {
  if (!data.length) return <span className="sparkline" />
  const w = 120, h = 32, pad = 2
  const max = Math.max(1, ...data.map(d => d.count))
  const step = (w - pad * 2) / Math.max(1, data.length - 1)
  const points = data
    .map((d, i) => {
      const x = pad + i * step
      const y = h - pad - (d.count / max) * (h - pad * 2)
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
  const last = data[data.length - 1]
  const lastX = pad + (data.length - 1) * step
  const lastY = h - pad - (last.count / max) * (h - pad * 2)
  return (
    <svg className="sparkline" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <polyline fill="none" stroke={color} strokeWidth="1.5" points={points} />
      <circle cx={lastX} cy={lastY} r="2.5" fill={color} />
    </svg>
  )
}
