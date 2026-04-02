// ── Button ───────────────────────────────────────────────────────────────────
export function Button({ children, variant = "primary", size = "md", className = "", loading, ...props }) {
  const base = "inline-flex items-center justify-center gap-2 font-body font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-emerald-500 hover:bg-emerald-400 text-navy-950 glow",
    secondary: "bg-navy-700 hover:bg-navy-600 text-slate-200 border border-white/10",
    danger: "bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 border border-rose-500/30",
    ghost: "hover:bg-white/5 text-slate-300",
  };
  const sizes = { sm: "px-3 py-1.5 text-sm", md: "px-4 py-2 text-sm", lg: "px-6 py-3 text-base" };
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} disabled={loading || props.disabled} {...props}>
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}

// ── Input ────────────────────────────────────────────────────────────────────
export function Input({ label, error, className = "", ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</label>}
      <input
        className={`input-field w-full px-3.5 py-2.5 rounded-lg text-sm ${error ? "border-rose-500/60" : ""} ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-rose-400">{error}</p>}
    </div>
  );
}

// ── Select ───────────────────────────────────────────────────────────────────
export function Select({ label, error, className = "", children, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</label>}
      <select
        className={`input-field w-full px-3.5 py-2.5 rounded-lg text-sm cursor-pointer ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <p className="text-xs text-rose-400">{error}</p>}
    </div>
  );
}

// ── Badge ────────────────────────────────────────────────────────────────────
export function Badge({ type }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium font-mono
      ${type === "income" ? "badge-income" : "badge-expense"}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${type === "income" ? "bg-emerald-400" : "bg-rose-400"}`} />
      {type}
    </span>
  );
}

// ── Role Badge ───────────────────────────────────────────────────────────────
export function RoleBadge({ role }) {
  const styles = {
    admin: "bg-violet-500/15 text-violet-300 border border-violet-500/25",
    analyst: "bg-sky-500/15 text-sky-300 border border-sky-500/25",
    viewer: "bg-slate-500/15 text-slate-300 border border-slate-500/25",
  };
  return (
    <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[role] || styles.viewer}`}>
      {role}
    </span>
  );
}

// ── Status Badge ─────────────────────────────────────────────────────────────
export function StatusBadge({ status }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
      ${status === "active"
        ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/25"
        : "bg-rose-500/15 text-rose-300 border border-rose-500/25"}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${status === "active" ? "bg-emerald-400" : "bg-rose-400"}`} />
      {status}
    </span>
  );
}

// ── Card ─────────────────────────────────────────────────────────────────────
export function Card({ children, className = "" }) {
  return (
    <div className={`glass rounded-xl p-5 ${className}`}>
      {children}
    </div>
  );
}

// ── Spinner ──────────────────────────────────────────────────────────────────
export function Spinner({ size = "md" }) {
  const s = size === "sm" ? "w-4 h-4" : size === "lg" ? "w-8 h-8" : "w-6 h-6";
  return (
    <svg className={`animate-spin ${s} text-emerald-400`} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

// ── Modal ────────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(5,13,26,0.85)", backdropFilter: "blur(4px)" }}>
      <div className="glass rounded-2xl w-full max-w-lg animate-fade-up">
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/7">
          <h2 className="font-display font-semibold text-base">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors text-xl leading-none">×</button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
}

// ── Alert ────────────────────────────────────────────────────────────────────
export function Alert({ type = "error", message }) {
  if (!message) return null;
  const styles = {
    error: "bg-rose-500/10 border-rose-500/30 text-rose-300",
    success: "bg-emerald-500/10 border-emerald-500/30 text-emerald-300",
  };
  return (
    <div className={`px-4 py-3 rounded-lg border text-sm ${styles[type]}`}>
      {message}
    </div>
  );
}

// ── Empty State ───────────────────────────────────────────────────────────────
export function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <div className="text-5xl opacity-20">{icon}</div>
      <p className="font-display font-semibold text-slate-300">{title}</p>
      {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
    </div>
  );
}
