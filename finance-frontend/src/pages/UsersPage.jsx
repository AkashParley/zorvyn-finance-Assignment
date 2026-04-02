import { useEffect, useState, useCallback } from "react";
import { usersApi } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  Card, Button, Select, Modal,
  RoleBadge, StatusBadge, Spinner, EmptyState, Alert
} from "../components/ui";

function EditUserModal({ user, onSave, onClose }) {
  const [role, setRole] = useState(user.role);
  const [status, setStatus] = useState(user.status);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSave = async () => {
    setLoading(true);
    setError("");
    try {
      await onSave(user.id, { role, status });
      onClose();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Alert message={error} />
      <div className="glass rounded-lg px-4 py-3 mb-1">
        <p className="text-xs text-slate-500 mb-1">User</p>
        <p className="font-medium text-slate-200">{user.username}</p>
        <p className="text-xs text-slate-500">{user.email}</p>
      </div>
      <Select label="Role" value={role} onChange={e => setRole(e.target.value)}>
        <option value="viewer">Viewer — read-only access</option>
        <option value="analyst">Analyst — read + insights</option>
        <option value="admin">Admin — full access</option>
      </Select>
      <Select label="Status" value={status} onChange={e => setStatus(e.target.value)}>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </Select>
      <div className="flex gap-3 justify-end pt-1">
        <Button variant="secondary" onClick={onClose}>Cancel</Button>
        <Button loading={loading} onClick={handleSave}>Save Changes</Button>
      </div>
    </div>
  );
}

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [editUser, setEditUser] = useState(null);
  const [deactivateUser, setDeactivateUser] = useState(null);
  const [deactivateLoading, setDeactivateLoading] = useState(false);
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 15;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await usersApi.list(page, PAGE_SIZE);
      setUsers(res.users || []);
      setTotal(res.total || 0);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { load(); }, [load]);

  const handleSaveEdit = async (id, data) => {
    await usersApi.update(id, data);
    load();
  };

  const handleDeactivate = async () => {
    setDeactivateLoading(true);
    try {
      await usersApi.deactivate(deactivateUser.id);
      setDeactivateUser(null);
      load();
    } catch (e) {
      console.error(e);
    } finally {
      setDeactivateLoading(false);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  // Role distribution stats
  const counts = users.reduce((acc, u) => {
    acc[u.role] = (acc[u.role] || 0) + 1; return acc;
  }, {});

  return (
    <div>
      {/* Header */}
      <div className="mb-7 animate-fade-up">
        <h1 className="font-display font-bold text-2xl tracking-tight">User Management</h1>
        <p className="text-slate-400 text-sm mt-1">{total} registered users</p>
      </div>

      {/* Role Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6 animate-fade-up" style={{ animationDelay: "80ms", animationFillMode: "both", opacity: 0 }}>
        {[
          { role: "admin",   label: "Admins",   color: "text-violet-400", bg: "bg-violet-500/10 border-violet-500/20" },
          { role: "analyst", label: "Analysts", color: "text-sky-400",    bg: "bg-sky-500/10 border-sky-500/20" },
          { role: "viewer",  label: "Viewers",  color: "text-slate-300",  bg: "bg-slate-500/10 border-slate-500/20" },
        ].map(({ role, label, color, bg }) => (
          <div key={role} className={`glass rounded-xl px-5 py-4 border ${bg}`}>
            <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">{label}</p>
            <p className={`font-display font-bold text-3xl ${color}`}>{counts[role] || 0}</p>
          </div>
        ))}
      </div>

      {/* Table */}
      <Card className="animate-fade-up" style={{ animationDelay: "160ms", animationFillMode: "both", opacity: 0 }}>
        {loading ? (
          <div className="flex justify-center py-20"><Spinner size="lg" /></div>
        ) : users.length === 0 ? (
          <EmptyState icon="◈" title="No users found" />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/7">
                    {["#", "Username", "Email", "Role", "Status", "Joined", "Actions"].map(h => (
                      <th key={h} className="pb-3 pt-1 text-left text-xs font-medium text-slate-500 uppercase tracking-wider pr-4">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {users.map(u => (
                    <tr key={u.id} className="tr-hover">
                      <td className="py-3 pr-4 text-slate-600 font-mono text-xs">{u.id}</td>
                      <td className="py-3 pr-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-navy-700 border border-white/10 flex items-center justify-center text-xs font-semibold text-emerald-400 flex-shrink-0">
                            {u.username[0].toUpperCase()}
                          </div>
                          <span className="font-medium text-slate-200">
                            {u.username}
                            {u.id === currentUser?.id && (
                              <span className="ml-1.5 text-[10px] text-emerald-400 font-mono">(you)</span>
                            )}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 pr-4 text-slate-400 text-xs">{u.email}</td>
                      <td className="py-3 pr-4"><RoleBadge role={u.role} /></td>
                      <td className="py-3 pr-4"><StatusBadge status={u.status} /></td>
                      <td className="py-3 pr-4 text-slate-500 font-mono text-xs whitespace-nowrap">
                        {new Date(u.created_at).toLocaleDateString("en-IN")}
                      </td>
                      <td className="py-3 whitespace-nowrap">
                        {u.id !== currentUser?.id && (
                          <div className="flex gap-2">
                            <button onClick={() => setEditUser(u)}
                              className="text-xs text-slate-400 hover:text-emerald-400 transition-colors px-2 py-1 rounded hover:bg-emerald-400/10">
                              Edit
                            </button>
                            {u.status === "active" && (
                              <button onClick={() => setDeactivateUser(u)}
                                className="text-xs text-slate-400 hover:text-rose-400 transition-colors px-2 py-1 rounded hover:bg-rose-400/10">
                                Deactivate
                              </button>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-5 pt-4 border-t border-white/7">
                <p className="text-xs text-slate-500">Page {page} of {totalPages}</p>
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Prev</Button>
                  <Button variant="secondary" size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next →</Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>

      {/* Edit Modal */}
      <Modal open={!!editUser} onClose={() => setEditUser(null)} title="Edit User">
        {editUser && <EditUserModal user={editUser} onSave={handleSaveEdit} onClose={() => setEditUser(null)} />}
      </Modal>

      {/* Deactivate Confirm */}
      <Modal open={!!deactivateUser} onClose={() => setDeactivateUser(null)} title="Deactivate User">
        <p className="text-slate-300 text-sm mb-6">
          Deactivate <span className="font-medium text-white">{deactivateUser?.username}</span>?
          They will be unable to log in until reactivated.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeactivateUser(null)}>Cancel</Button>
          <Button variant="danger" loading={deactivateLoading} onClick={handleDeactivate}>Deactivate</Button>
        </div>
      </Modal>
    </div>
  );
}
