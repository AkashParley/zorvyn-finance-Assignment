import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const NAV = [
  { to: "/dashboard", icon: "⬡", label: "Dashboard" },
  { to: "/transactions", icon: "↕", label: "Transactions" },
  { to: "/users", icon: "◈", label: "Users", adminOnly: true },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <aside className="fixed left-0 top-0 h-screen w-56 flex flex-col z-30"
      style={{ background: "rgba(8,20,38,0.97)", borderRight: "1px solid rgba(255,255,255,0.06)" }}>

      {/* Logo */}
      <div className="px-5 pt-7 pb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center glow">
            <span className="text-navy-950 font-display font-black text-sm">F</span>
          </div>
          <span className="font-display font-bold text-base tracking-tight">FinanceOS</span>
        </div>
        <p className="text-xs text-slate-500 mt-1 font-mono">v1.0</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 flex flex-col gap-0.5">
        <p className="text-xs font-medium text-slate-600 uppercase tracking-widest px-2 mb-2">Menu</p>
        {NAV.map(({ to, icon, label, adminOnly }) => {
          if (adminOnly && user?.role !== "admin") return null;
          return (
            <NavLink key={to} to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-150 border-l-2
                 ${isActive
                   ? "nav-active font-medium"
                   : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/4"}`}>
              <span className="text-base w-5 text-center">{icon}</span>
              <span className="font-body">{label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User info */}
      <div className="px-3 pb-5">
        <div className="glass rounded-xl px-3.5 py-3">
          <div className="flex items-center gap-2.5 mb-2.5">
            <div className="w-7 h-7 rounded-full bg-navy-700 border border-white/10 flex items-center justify-center text-xs font-semibold text-emerald-400">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">{user?.username}</p>
              <p className="text-[10px] text-slate-500 capitalize">{user?.role}</p>
            </div>
          </div>
          <button onClick={handleLogout}
            className="w-full text-xs text-slate-500 hover:text-rose-400 transition-colors text-left py-0.5">
            Sign out →
          </button>
        </div>
      </div>
    </aside>
  );
}
