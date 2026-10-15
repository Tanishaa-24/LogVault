import { Line, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, BarElement,
  ArcElement, Title, Tooltip, Legend, Filler,
)

const SEVERITY_COLORS = {
  FATAL: '#dc2626',
  ERROR: '#ef4444',
  WARNING: '#f59e0b',
  INFO: '#3b82f6',
  DEBUG: '#6b7280',
}

const CHART_OPTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#d1d5db' } },
    tooltip: { backgroundColor: '#1f2937' },
  },
  scales: {
    x: { ticks: { color: '#9ca3af', maxTicksLimit: 8 }, grid: { color: '#1f2937' } },
    y: { ticks: { color: '#9ca3af' }, grid: { color: '#1f2937' }, beginAtZero: true },
  },
}

export function TrendChart({ data }) {
  if (!data || !data.hours || !data.hours.length) {
    return <div className="empty">No data in this window</div>
  }
  const labels = data.hours.map(h => {
    const d = new Date(h.hour)
    return `${d.getHours()}:00`
  })
  const datasets = data.severities.map(sev => ({
    label: sev,
    data: data.hours.map(h => h[sev] || 0),
    borderColor: SEVERITY_COLORS[sev] || '#60a5fa',
    backgroundColor: (SEVERITY_COLORS[sev] || '#60a5fa') + '22',
    fill: true,
    tension: 0.3,
  }))
  return (
    <div style={{ height: 240 }}>
      <Line data={{ labels, datasets }} options={CHART_OPTS} />
    </div>
  )
}

export function SeverityChart({ data }) {
  if (!data || !data.length) {
    return <div className="empty">No data</div>
  }
  const chartData = {
    labels: data.map(d => d.severity),
    datasets: [
      {
        data: data.map(d => d.count),
        backgroundColor: data.map(d => SEVERITY_COLORS[d.severity] || '#60a5fa'),
        borderColor: '#141821',
        borderWidth: 2,
      },
    ],
  }
  const opts = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#d1d5db' } } },
  }
  return (
    <div style={{ height: 240 }}>
      <Doughnut data={chartData} options={opts} />
    </div>
  )
}
