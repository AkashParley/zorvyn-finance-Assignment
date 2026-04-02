import { useEffect, useState } from "react";
import { dashApi } from "../services/api";
import { Card, Badge, Spinner, EmptyState } from "../components/ui";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, CartesianGrid, Cell, PieChart, Pie, Legend
} from "recharts";

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function StatCard({ label, value, sub, accent, delay = 0, format = "currency" }) {
  const main =
    format === "percent"
      ? `${Number(value || 0).toFixed(1)}%`
      : `₹${Number(value || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
  return (
    <Card className="animate-fade-up" style={{ animationDelay: `${delay}ms`, animationFillMode: "both", opacity: 0 }}>
      <p className="text-xs font-medium text-slate-500 uppercase tracking-widest mb-3">{label}</p>
      <p className={`font-display font-bold text-2xl ${accent}`}>{main}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </Card>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs">
      <p className="text-slate-400 mb-1">{label}</p>
      {payload.map(p => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: ₹{Number(p.value).toLocaleString("en-IN")}
        </p>
      ))}
    </div>
  );
};

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashApi.summary()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Spinner size="lg" />
    </div>
  );

  if (!data) return <EmptyState icon="📊" title="Could not load dashboard" subtitle="Check your connection." />;

  const trends = (data.monthly_trends || []).map(t => ({
    name: `${MONTHS[t.month - 1]} ${t.year}`,
    income: Number(t.income),
    expense: Number(t.expense),
    net: Number(t.net),
  }));

  const incomeCategories = (data.income_by_category || []).slice(0, 6);
  const expenseCategories = (data.expense_by_category || []).slice(0, 6);

  const PIE_COLORS_INCOME  = ["#10b981","#34d399","#6ee7b7","#a7f3d0","#d1fae5","#ecfdf5"];
  const PIE_COLORS_EXPENSE = ["#f43f5e","#fb7185","#fda4af","#fecdd3","#ffe4e6","#fff1f2"];

  return (
    <div>
      {/* Header */}
      <div className="mb-8 animate-fade-up">
        <h1 className="font-display font-bold text-2xl tracking-tight">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Financial overview at a glance</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Income"   value={data.total_income}   accent="text-emerald-400" delay={0}   sub={`${data.total_transactions} total transactions`} />
        <StatCard label="Total Expenses" value={data.total_expenses} accent="text-rose-400"    delay={80} />
        <StatCard
          label="Net Balance"
          value={data.net_balance}
          accent={Number(data.net_balance) >= 0 ? "text-emerald-400" : "text-rose-400"}
          delay={160}
          sub={Number(data.net_balance) >= 0 ? "Surplus" : "Deficit"}
        />
        <StatCard
          label="Savings Rate"
          value={data.savings_rate}
          accent="text-sky-400"
          delay={200}
          format="percent"
          sub="Net balance ÷ income (0% if no income)"
        />
      </div>

      {/* Income vs Expense — pie */}
      {(Number(data.total_income) > 0 || Number(data.total_expenses) > 0) && (
        <Card className="mb-6 animate-fade-up" style={{ animationDelay: "220ms", animationFillMode: "both", opacity: 0 }}>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-4">Income vs Expense</p>
          <div className="flex flex-col md:flex-row items-center gap-6">
            <ResponsiveContainer width="100%" height={240} className="max-w-xs mx-auto md:mx-0">
              <PieChart>
                <Pie
                  data={[
                    { name: "Income", value: Number(data.total_income) },
                    { name: "Expense", value: Number(data.total_expenses) },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={56}
                  outerRadius={88}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                >
                  <Cell fill="#10b981" />
                  <Cell fill="#f43f5e" />
                </Pie>
                <Tooltip
                  formatter={(value) => [`₹${Number(value).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`, ""]}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
            <p className="text-sm text-slate-500 max-w-md">
              Savings rate: <span className="text-sky-400 font-semibold">{Number(data.savings_rate ?? 0).toFixed(1)}%</span>
              {" — "}
              net balance divided by total income (0% if there is no income).
            </p>
          </div>
        </Card>
      )}

      {/* Trend Chart */}
      {trends.length > 0 && (
        <Card className="mb-6 animate-fade-up" style={{ animationDelay: "240ms", animationFillMode: "both", opacity: 0 }}>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-5">Monthly Trends</p>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={trends} margin={{ top: 5, right: 5, bottom: 5, left: 10 }}>
              <defs>
                <linearGradient id="gIncome" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="gExpense" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#f43f5e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="name" tick={{ fill: "#7a90b8", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#7a90b8", fontSize: 11 }} axisLine={false} tickLine={false}
                tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="income"  stroke="#10b981" fill="url(#gIncome)"  strokeWidth={2} name="Income" />
              <Area type="monotone" dataKey="expense" stroke="#f43f5e" fill="url(#gExpense)" strokeWidth={2} name="Expense" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Category Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Income by category */}
        <Card className="animate-fade-up" style={{ animationDelay: "320ms", animationFillMode: "both", opacity: 0 }}>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-4">Income by Category</p>
          {incomeCategories.length === 0
            ? <p className="text-slate-600 text-sm py-6 text-center">No data yet</p>
            : (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={incomeCategories} layout="vertical" margin={{ left: 10 }}>
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="category" tick={{ fill: "#7a90b8", fontSize: 11 }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="total" radius={[0, 4, 4, 0]} name="Income">
                    {incomeCategories.map((_, i) => <Cell key={i} fill={PIE_COLORS_INCOME[i % PIE_COLORS_INCOME.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
        </Card>

        {/* Expense by category */}
        <Card className="animate-fade-up" style={{ animationDelay: "380ms", animationFillMode: "both", opacity: 0 }}>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-4">Expense by Category</p>
          {expenseCategories.length === 0
            ? <p className="text-slate-600 text-sm py-6 text-center">No data yet</p>
            : (
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={expenseCategories} layout="vertical" margin={{ left: 10 }}>
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="category" tick={{ fill: "#7a90b8", fontSize: 11 }} axisLine={false} tickLine={false} width={80} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="total" radius={[0, 4, 4, 0]} name="Expense">
                    {expenseCategories.map((_, i) => <Cell key={i} fill={PIE_COLORS_EXPENSE[i % PIE_COLORS_EXPENSE.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card className="animate-fade-up" style={{ animationDelay: "440ms", animationFillMode: "both", opacity: 0 }}>
        <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-4">Recent Activity</p>
        {(!data.recent_transactions || data.recent_transactions.length === 0)
          ? <EmptyState icon="↕" title="No transactions yet" />
          : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left">
                  {["Date","Category","Type","Amount","Notes"].map(h => (
                    <th key={h} className="pb-3 text-xs font-medium text-slate-500 uppercase tracking-wider pr-4">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {data.recent_transactions.map(tx => (
                  <tr key={tx.id} className="tr-hover">
                    <td className="py-2.5 pr-4 text-slate-400 font-mono text-xs">{tx.date}</td>
                    <td className="py-2.5 pr-4 text-slate-200">{tx.category}</td>
                    <td className="py-2.5 pr-4"><Badge type={tx.type} /></td>
                    <td className={`py-2.5 pr-4 font-mono font-medium ${tx.type === "income" ? "text-emerald-400" : "text-rose-400"}`}>
                      {tx.type === "income" ? "+" : "−"}₹{Number(tx.amount).toLocaleString("en-IN")}
                    </td>
                    <td className="py-2.5 text-slate-500 text-xs truncate max-w-xs">{tx.description || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </Card>
    </div>
  );
}
