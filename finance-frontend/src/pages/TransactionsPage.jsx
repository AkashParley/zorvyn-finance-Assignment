import { useEffect, useState, useCallback } from "react";
import { txApi } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  Card, Badge, Button, Input, Select,
  Modal, Alert, Spinner, EmptyState
} from "../components/ui";

const EMPTY_FORM = { amount: "", type: "income", category: "", date: "", description: "" };

function TransactionForm({ initial, onSave, onClose }) {
  const [form, setForm] = useState(initial || EMPTY_FORM);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await onSave({ ...form, amount: parseFloat(form.amount) });
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Alert message={error} />
      <div className="grid grid-cols-2 gap-4">
        <Input label="Amount (₹)" type="number" step="0.01" min="0.01"
          value={form.amount} onChange={e => set("amount", e.target.value)} required />
        <Select label="Type" value={form.type} onChange={e => set("type", e.target.value)}>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </Select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input label="Category" placeholder="Salary, Rent…"
          value={form.category} onChange={e => set("category", e.target.value)} required />
        <Input label="Date" type="date"
          value={form.date} onChange={e => set("date", e.target.value)} required />
      </div>
      <Input label="Notes (optional)" placeholder="Brief description…"
        value={form.description} onChange={e => set("description", e.target.value)} />
      <div className="flex gap-3 pt-1 justify-end">
        <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
        <Button type="submit" loading={loading}>
          {initial ? "Save Changes" : "Add Transaction"}
        </Button>
      </div>
    </form>
  );
}

export default function TransactionsPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [txs, setTxs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 15;

  // Filters
  const [filters, setFilters] = useState({ type: "", category: "", date_from: "", date_to: "", search: "" });
  const setF = (k, v) => { setFilters(f => ({ ...f, [k]: v })); setPage(1); };

  // Modals
  const [addOpen, setAddOpen] = useState(false);
  const [editTx, setEditTx] = useState(null);
  const [deleteTx, setDeleteTx] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { ...filters, page, page_size: PAGE_SIZE };
      const res = await txApi.list(params);
      setTxs(res.transactions || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => { load(); }, [load]);

  const handleAdd = async (data) => {
    await txApi.create(data);
    load();
  };

  const handleEdit = async (data) => {
    await txApi.update(editTx.id, data);
    setEditTx(null);
    load();
  };

  const handleDelete = async () => {
    setDeleteLoading(true);
    try { await txApi.remove(deleteTx.id); setDeleteTx(null); load(); }
    catch (e) { console.error(e); }
    finally { setDeleteLoading(false); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-7 animate-fade-up">
        <div>
          <h1 className="font-display font-bold text-2xl tracking-tight">Transactions</h1>
          <p className="text-slate-400 text-sm mt-1">{total} records total</p>
        </div>
        {isAdmin && (
          <Button onClick={() => setAddOpen(true)}>
            <span className="text-base leading-none">+</span> Add Transaction
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card className="mb-5 animate-fade-up" style={{ animationDelay: "80ms", animationFillMode: "both", opacity: 0 }}>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <Input placeholder="🔍  Search…" value={filters.search}
            onChange={e => setF("search", e.target.value)} />
          <Select value={filters.type} onChange={e => setF("type", e.target.value)}>
            <option value="">All Types</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </Select>
          <Input placeholder="Category (exact match)" value={filters.category}
            onChange={e => setF("category", e.target.value)} />
          <Input type="date" value={filters.date_from}
            onChange={e => setF("date_from", e.target.value)} />
          <Input type="date" value={filters.date_to}
            onChange={e => setF("date_to", e.target.value)} />
        </div>
        {Object.values(filters).some(Boolean) && (
          <button className="text-xs text-slate-500 hover:text-emerald-400 transition-colors mt-3"
            onClick={() => { setFilters({ type: "", category: "", date_from: "", date_to: "", search: "" }); setPage(1); }}>
            Clear filters ×
          </button>
        )}
      </Card>

      {/* Table */}
      <Card className="animate-fade-up" style={{ animationDelay: "160ms", animationFillMode: "both", opacity: 0 }}>
        {loading ? (
          <div className="flex justify-center py-20"><Spinner size="lg" /></div>
        ) : txs.length === 0 ? (
          <EmptyState icon="↕" title="No transactions found" subtitle="Try adjusting your filters." />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/7">
                    {["#","Date","Category","Type","Amount","Notes", isAdmin ? "Actions" : ""].map(h => (
                      <th key={h} className="pb-3 pt-1 text-left text-xs font-medium text-slate-500 uppercase tracking-wider pr-4">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {txs.map(tx => (
                    <tr key={tx.id} className="tr-hover">
                      <td className="py-3 pr-4 text-slate-600 font-mono text-xs">{tx.id}</td>
                      <td className="py-3 pr-4 text-slate-400 font-mono text-xs whitespace-nowrap">{tx.date}</td>
                      <td className="py-3 pr-4 text-slate-200 font-medium">{tx.category}</td>
                      <td className="py-3 pr-4"><Badge type={tx.type} /></td>
                      <td className={`py-3 pr-4 font-mono font-semibold ${tx.type === "income" ? "text-emerald-400" : "text-rose-400"}`}>
                        {tx.type === "income" ? "+" : "−"}₹{Number(tx.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 pr-4 text-slate-500 text-xs max-w-[180px] truncate">{tx.description || "—"}</td>
                      {isAdmin && (
                        <td className="py-3 whitespace-nowrap">
                          <div className="flex gap-2">
                            <button onClick={() => setEditTx(tx)}
                              className="text-xs text-slate-400 hover:text-emerald-400 transition-colors px-2 py-1 rounded hover:bg-emerald-400/10">
                              Edit
                            </button>
                            <button onClick={() => setDeleteTx(tx)}
                              className="text-xs text-slate-400 hover:text-rose-400 transition-colors px-2 py-1 rounded hover:bg-rose-400/10">
                              Delete
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {total > 0 && (
              <div className="flex items-center justify-between mt-5 pt-4 border-t border-white/7">
                <p className="text-xs text-slate-500">
                  Page {page} of {Math.max(totalPages, 1)} · {total} records
                </p>
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" disabled={page <= 1}
                    onClick={() => setPage(p => p - 1)}>← Prev</Button>
                  <Button variant="secondary" size="sm" disabled={page >= totalPages}
                    onClick={() => setPage(p => p + 1)}>Next →</Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>

      {/* Add Modal */}
      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="New Transaction">
        <TransactionForm onSave={handleAdd} onClose={() => setAddOpen(false)} />
      </Modal>

      {/* Edit Modal */}
      <Modal open={!!editTx} onClose={() => setEditTx(null)} title="Edit Transaction">
        {editTx && (
          <TransactionForm
            initial={{ ...editTx, amount: String(editTx.amount), date: editTx.date }}
            onSave={handleEdit}
            onClose={() => setEditTx(null)}
          />
        )}
      </Modal>

      {/* Delete Confirm */}
      <Modal open={!!deleteTx} onClose={() => setDeleteTx(null)} title="Delete Transaction">
        <p className="text-slate-300 text-sm mb-6">
          Are you sure you want to delete transaction <span className="font-mono text-white">#{deleteTx?.id}</span>?
          This action performs a soft delete and can be recovered from the database.
        </p>
        <div className="flex gap-3 justify-end">
          <Button variant="secondary" onClick={() => setDeleteTx(null)}>Cancel</Button>
          <Button variant="danger" loading={deleteLoading} onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}
