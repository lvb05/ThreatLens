import { useState, useEffect, useRef } from "react"

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
const WS = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000")
  .replace("https://", "wss://")
  .replace("http://", "ws://") + "/ws/alerts"

const SEVERITY_COLOR = {
  critical: { bg: "#2d1b1b", border: "#ef4444", text: "#f87171", badge: "#ef4444" },
  high:     { bg: "#2d2010", border: "#f97316", text: "#fb923c", badge: "#f97316" },
  medium:   { bg: "#1e2a1e", border: "#22c55e", text: "#4ade80", badge: "#22c55e" },
  low:      { bg: "#1a2035", border: "#3b82f6", text: "#60a5fa", badge: "#3b82f6" },
}

const ATTACK_LABELS = {
  card_testing:    "Card Testing",
  velocity_abuse:  "Velocity Abuse",
  large_fraud:     "Large Fraud",
  account_takeover:"Account Takeover",
  bot_attack:      "Bot Attack",
}

function SeverityBadge({ severity }) {
  const c = SEVERITY_COLOR[severity] || SEVERITY_COLOR.low
  return (
    <span style={{
      background: c.badge + "22", color: c.badge,
      border: `1px solid ${c.badge}44`,
      borderRadius: 20, padding: "2px 10px",
      fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: 1
    }}>{severity}</span>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      background: "#111827", border: "1px solid #1f2937",
      borderRadius: 12, padding: "18px 22px", flex: 1, minWidth: 140
    }}>
      <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: color || "#e2e8f0" }}>{value}</div>
    </div>
  )
}

function AlertCard({ alert, onClick, selected }) {
  const c = SEVERITY_COLOR[alert.severity] || SEVERITY_COLOR.low
  return (
    <div onClick={() => onClick(alert)} style={{
      background: selected ? c.bg : "#111827",
      border: `1px solid ${selected ? c.border : "#1f2937"}`,
      borderRadius: 10, padding: "14px 16px", cursor: "pointer",
      marginBottom: 8, transition: "all .2s"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: c.text }}>
          {ATTACK_LABELS[alert.attack_type] || alert.attack_type}
        </span>
        <SeverityBadge severity={alert.severity} />
      </div>
      <div style={{ display: "flex", gap: 16, fontSize: 12, color: "#9ca3af" }}>
        <span>₹{Number(alert.amount).toLocaleString("en-IN")}</span>
        <span>Score: {Number(alert.fraud_score).toFixed(3)}</span>
        <span>{alert.account_id}</span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 11, color: "#4b5563" }}>
        <span>{alert.mitre_tag}</span>
        <span style={{
          color: alert.source === "wazuh" ? "#a78bfa" : "#38bdf8",
          fontWeight: 500
        }}>{alert.source === "wazuh" ? "⚡ Wazuh SIEM" : "🤖 ML Model"}</span>
      </div>
    </div>
  )
}

function ShapChart({ shapJson }) {
  if (!shapJson) return null
  let data
  try { data = JSON.parse(shapJson) } catch { return null }

  const max = Math.max(...data.map(d => Math.abs(d.shap_value)))

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 8 }}>
        WHY THIS WAS FLAGGED — SHAP Explanation
      </div>
      {data.map((d, i) => (
        <div key={i} style={{ marginBottom: 6 }}>
          <div style={{ display: "flex", justifyContent: "space-between",
            fontSize: 11, marginBottom: 3 }}>
            <span style={{ color: "#9ca3af", fontFamily: "monospace" }}>{d.feature}</span>
            <span style={{ color: d.direction === "fraud" ? "#ef4444" : "#22c55e",
              fontWeight: 600 }}>
              {d.direction === "fraud" ? "▲" : "▼"} {d.shap_value.toFixed(4)}
            </span>
          </div>
          <div style={{ height: 6, background: "#1f2937", borderRadius: 3, overflow: "hidden" }}>
            <div style={{
              height: "100%", borderRadius: 3,
              width: `${(Math.abs(d.shap_value) / max) * 100}%`,
              background: d.direction === "fraud"
                ? "linear-gradient(90deg, #ef4444, #f97316)"
                : "linear-gradient(90deg, #22c55e, #38bdf8)"
            }} />
          </div>
        </div>
      ))}
      <div style={{ fontSize: 10, color: "#4b5563", marginTop: 4 }}>
        🔴 pushes toward fraud &nbsp; 🟢 pushes toward normal
      </div>
    </div>
  )
}

function AlertDetail({ alert, onClose, onStatusChange }) {
  if (!alert) return null
  const c = SEVERITY_COLOR[alert.severity] || SEVERITY_COLOR.low
  const [updating, setUpdating] = useState(false)
  const [ariaAnalysis, setAriaAnalysis] = useState("")
  const [ariaLoading, setAriaLoading] = useState(false)

  const handleStatus = async (newStatus) => {
    setUpdating(true)
    try {
      const res = await fetch(`${API}/api/v1/alerts/${alert.id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      })
      if (res.ok) onStatusChange(alert.id, newStatus)
    } finally { setUpdating(false) }
  }

  const handleARIA = async () => {
    setAriaLoading(true)

    try {
      const res = await fetch(`${API}/api/v1/alerts/${alert.id}/analyze`, {
        method: "POST"
      })

      const data = await res.json()
      setAriaAnalysis(data.analysis || "No analysis returned.")

    } catch (err) {
      setAriaAnalysis("ARIA failed to analyze this alert.")

    } finally {
      setAriaLoading(false)
    }
  }

  const handlePDFExport = () => {
    window.open(`${API}/api/v1/alerts/${alert.id}/report`, "_blank")
  }

  return (
    <div style={{
      background: "#111827", border: `1px solid ${c.border}`,
      borderRadius: 12, padding: 20, height: "100%"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{ fontSize: 16, fontWeight: 700, color: c.text }}>
          {ATTACK_LABELS[alert.attack_type] || alert.attack_type}
        </span>
        <button onClick={onClose} style={{
          background: "none", border: "none", color: "#6b7280",
          fontSize: 18, cursor: "pointer"
        }}>✕</button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 16 }}>
        {[
          ["Amount", `₹${Number(alert.amount).toLocaleString("en-IN")}`],
          ["Fraud Score", Number(alert.fraud_score).toFixed(4)],
          ["Severity", <SeverityBadge severity={alert.severity} />],
          ["Source", alert.source === "wazuh" ? "⚡ Wazuh SIEM" : "🤖 ML Model"],
          ["MITRE Tag", alert.mitre_tag || "—"],
          ["Account", alert.account_id || "—"],
          ["IP Address", alert.ip_address || "—"],
          ["Status", alert.status],
          ["Abuse Score", alert.abuse_score ?? "N/A"],
          ["Country", alert.country || "Unknown"],
          ["ISP", alert.isp || "Unknown"],
        ].map(([k, v]) => (
          <div key={k} style={{
            background: "#0d1117", borderRadius: 8,
            padding: "10px 12px", border: "1px solid #1f2937"
          }}>
            <div style={{ fontSize: 11, color: "#6b7280", marginBottom: 3 }}>{k}</div>
            <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 500 }}>{v}</div>
          </div>
        ))}
      </div>

      <ShapChart shapJson={alert.shap_json} />

      <div style={{ marginBottom: 14 }}>
        <button
          onClick={handleARIA}
          disabled={ariaLoading}
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: 8,
            border: "none",
            background: "#7c3aed",
            color: "white",
            fontWeight: 600,
            cursor: "pointer"
          }}
        >
          {ariaLoading ? "ARIA Analyzing..." : "Analyze with ARIA"}
        </button>
      </div>

      <div style={{ marginBottom: 14 }}>
        <button
          onClick={handlePDFExport}
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: 8,
            border: "none",
            background: "#2563eb",
            color: "white",
            fontWeight: 600,
            cursor: "pointer"
          }}
        >
          Export PDF Incident Report
        </button>
      </div>

      {ariaAnalysis && (
        <div style={{
          background: "#0d1117",
          border: "1px solid #1f2937",
          borderRadius: 8,
          padding: 14,
          marginBottom: 16
        }}>

      <div style={{
        fontSize: 12,
        color: "#a78bfa",
        marginBottom: 8,
        fontWeight: 600
      }}>
        ARIA AI ANALYST REPORT
      </div>

      <div style={{
        whiteSpace: "pre-wrap",
        fontSize: 12,
        color: "#d1d5db",
        lineHeight: 1.6
      }}>
        {ariaAnalysis}
      </div>
    </div>
  )}

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 8 }}>Update Status</div>
        <div style={{ display: "flex", gap: 8 }}>
          {["open", "investigating", "resolved"].map(s => (
            <button key={s} onClick={() => handleStatus(s)} disabled={updating || alert.status === s}
              style={{
                flex: 1, padding: "8px 0", borderRadius: 8, border: "1px solid #1f2937",
                background: alert.status === s ? "#1f2937" : "#0d1117",
                color: alert.status === s ? "#e2e8f0" : "#6b7280",
                cursor: alert.status === s ? "default" : "pointer",
                fontSize: 12, fontWeight: 500, textTransform: "capitalize"
              }}>{s}</button>
          ))}
        </div>
      </div>

      <div style={{
        background: "#0d1117", borderRadius: 8, padding: 12,
        border: "1px solid #1f2937", fontSize: 11, color: "#4b5563", wordBreak: "break-all"
      }}>
        Alert ID: {alert.id}
      </div>
    </div>
  )
}

export default function App() {
  const [alerts, setAlerts] = useState([])
  const [selected, setSelected] = useState(null)
  const [connected, setConnected] = useState(false)
  const [totalCount, setTotalCount] = useState(0)
  const wsRef = useRef(null)

  // Load initial alerts
  useEffect(() => {
    fetch(`${API}/api/v1/alerts/?limit=50`)
      .then(r => r.json())
      .then(data => {
        setAlerts(data.alerts || [])
        setTotalCount(data.total || 0)
      })
      .catch(console.error)
  }, [])

  // WebSocket live feed
  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(WS)
      wsRef.current = ws

      ws.onopen = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        setTimeout(connect, 3000) // auto-reconnect
      }
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if (msg.type === "new_alert") {
          setAlerts(prev => [msg.alert, ...prev].slice(0, 100))
          setTotalCount(prev => prev + 1)
        }
      }
    }
    connect()
    return () => wsRef.current?.close()
  }, [])

  const handleStatusChange = (id, newStatus) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: newStatus } : a))
    if (selected?.id === id) setSelected(prev => ({ ...prev, status: newStatus }))
  }

  const counts = {
    critical: alerts.filter(a => a.severity === "critical").length,
    high: alerts.filter(a => a.severity === "high").length,
    open: alerts.filter(a => a.status === "open").length,
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0a0e1a" }}>
      {/* Header */}
      <div style={{
        background: "#111827", borderBottom: "1px solid #1f2937",
        padding: "14px 24px", display: "flex", alignItems: "center", justifyContent: "space-between"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 20, fontWeight: 700, color: "#38bdf8" }}>🛡 ThreatLens</span>
          <span style={{ fontSize: 12, color: "#4b5563" }}>Security Operations Center</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 8, height: 8, borderRadius: "50%",
            background: connected ? "#22c55e" : "#ef4444",
            boxShadow: connected ? "0 0 6px #22c55e" : "none"
          }} />
          <span style={{ fontSize: 12, color: connected ? "#22c55e" : "#ef4444" }}>
            {connected ? "LIVE" : "Reconnecting..."}
          </span>
        </div>
      </div>

      <div style={{ padding: 24 }}>
        {/* Stats */}
        <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
          <StatCard label="Total Alerts" value={totalCount} color="#38bdf8" />
          <StatCard label="Critical" value={counts.critical} color="#ef4444" />
          <StatCard label="High" value={counts.high} color="#f97316" />
          <StatCard label="Open Cases" value={counts.open} color="#facc15" />
        </div>

        {/* Main content */}
        <div style={{ display: "grid", gridTemplateColumns: selected ? "1fr 1fr" : "1fr", gap: 16 }}>
          {/* Alert queue */}
          <div>
            <div style={{ fontSize: 13, color: "#6b7280", marginBottom: 12, fontWeight: 500 }}>
              LIVE ALERT QUEUE — {alerts.length} alerts loaded
            </div>
            <div style={{ maxHeight: "70vh", overflowY: "auto", paddingRight: 4 }}>
              {alerts.length === 0 ? (
                <div style={{ color: "#4b5563", textAlign: "center", padding: 40 }}>
                  Waiting for alerts...
                </div>
              ) : alerts.map(alert => (
                <AlertCard
                  key={alert.id} alert={alert}
                  onClick={setSelected}
                  selected={selected?.id === alert.id}
                />
              ))}
            </div>
          </div>

          {/* Alert detail */}
          {selected && (
            <AlertDetail
              alert={selected}
              onClose={() => setSelected(null)}
              onStatusChange={handleStatusChange}
            />
          )}
        </div>
      </div>
    </div>
  )
}
