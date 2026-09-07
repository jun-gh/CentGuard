import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const SUGGESTIONS = [
  "How much did I spend last month?",
  "Break down my spending by category this month",
  "Any unusual transactions I should know about?",
  "What's my net savings this month?",
];

const BAR_COLORS = ["#3b82f6", "#60a5fa", "#818cf8", "#a78bfa", "#c084fc", "#e879f9", "#f472b6", "#fb923c"];

function formatPeso(value) {
  return `₱${value.toLocaleString("en-PH", { maximumFractionDigits: 0 })}`;
}

function SpendingChart() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchSummary() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/spending-summary`);
        if (!res.ok) throw new Error("Could not load spending summary");
        const json = await res.json();
        if (!cancelled) setData(json);
      } catch (err) {
        if (!cancelled) setError(err.message);
      }
    }

    fetchSummary();
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) return null; // fail quietly — chart is a nice-to-have, not critical
  if (!data) return <div className="chart-loading">Loading spending summary…</div>;

  const chartData = Object.entries(data.totals_by_category || {})
    .map(([category, amount]) => ({ category, amount }))
    .sort((a, b) => b.amount - a.amount);

  if (chartData.length === 0) {
    return (
      <div className="chart-empty">No spending recorded for {data.month} yet.</div>
    );
  }

  return (
    <div className="spending-chart">
      <div className="spending-chart-header">
        <span>Spending by category — {data.month}</span>
        <span className="spending-chart-total">{formatPeso(data.total_spent)} total</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="category"
            width={110}
            tick={{ fill: "#9aa0ab", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value) => formatPeso(value)}
            contentStyle={{ background: "#1c1f27", border: "1px solid #2c3038", borderRadius: 8 }}
            labelStyle={{ color: "#e6e6e6" }}
          />
          <Bar dataKey="amount" radius={[0, 6, 6, 0]}>
            {chartData.map((_, index) => (
              <Cell key={index} fill={BAR_COLORS[index % BAR_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function SpendingSummary({ onPick }) {
  return (
    <div className="suggestions">
      <SpendingChart />
      <p className="suggestions-title">Try asking:</p>
      <div className="suggestions-list">
        {SUGGESTIONS.map((text) => (
          <button key={text} className="suggestion-chip" onClick={() => onPick(text)}>
            {text}
          </button>
        ))}
      </div>
    </div>
  );
}