import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { useAuth } from '../../contexts/AuthContext';
import { Plus, Trash2, Shield, X } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const ROLES = ['author', 'editor', 'admin', 'super_admin'];

export default function UsersManager() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: '', password: '', name: '', role: 'author', bio: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const fetchUsers = async () => {
    try {
      const { data } = await axios.get(`${API}/admin/users`, { headers: getAuthHeader() });
      setUsers(data || []);
    } catch {}
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password || !form.name) { setError('All fields required'); return; }
    setSaving(true);
    setError('');
    try {
      await axios.post(`${API}/admin/users`, form, { headers: getAuthHeader() });
      setShowForm(false);
      setForm({ email: '', password: '', name: '', role: 'author', bio: '' });
      fetchUsers();
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to create user');
    } finally { setSaving(false); }
  };

  const handleChangeRole = async (userId, role) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/role?role=${role}`, {}, { headers: getAuthHeader() });
      fetchUsers();
    } catch {}
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Delete this user?')) return;
    try {
      await axios.delete(`${API}/admin/users/${userId}`, { headers: getAuthHeader() });
      fetchUsers();
    } catch {}
  };

  const roleBadge = (role) => {
    const colors = {
      super_admin: 'bg-[#D4AF37]/10 text-[#D4AF37] border-[#D4AF37]/30',
      admin: 'bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30',
      editor: 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30',
      author: 'bg-[#9CA3AF]/10 text-[#9CA3AF] border-[#9CA3AF]/30',
    };
    return (
      <span className={`px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold border rounded ${colors[role] || colors.author}`}>
        {role.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="p-6 lg:p-8" data-testid="users-manager-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Team Members</h1>
          <p className="text-sm text-[#6B7280]">{users.length} users</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-1 px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] transition-colors"
          data-testid="add-user-btn"
        >
          <Plus className="w-4 h-4" /> Add User
        </button>
      </div>

      {/* Create User Form */}
      {showForm && (
        <form onSubmit={handleCreate} className="bg-[#121620] border border-[#232B3E] rounded-lg p-4 mb-6 space-y-3" data-testid="create-user-form">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-[#F3F4F6]">New Team Member</h3>
            <button type="button" onClick={() => setShowForm(false)} className="text-[#6B7280] hover:text-[#F3F4F6]"><X className="w-4 h-4" /></button>
          </div>
          {error && <div className="text-xs text-[#EF4444]">{error}</div>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Full name" className="px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="new-user-name" />
            <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="Email" className="px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="new-user-email" />
            <input type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} placeholder="Password" className="px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="new-user-password" />
            <select value={form.role} onChange={e => setForm({...form, role: e.target.value})} className="px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="new-user-role">
              {ROLES.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
            </select>
          </div>
          <button type="submit" disabled={saving} className="px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50" data-testid="save-user-btn">
            {saving ? 'Creating...' : 'Create User'}
          </button>
        </form>
      )}

      {/* Users Table */}
      <div className="bg-[#121620] border border-[#232B3E] rounded-lg overflow-hidden">
        <table className="w-full" data-testid="users-table">
          <thead>
            <tr className="border-b border-[#232B3E]">
              <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold text-left">User</th>
              <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold text-left hidden md:table-cell">Email</th>
              <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold text-left">Role</th>
              <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-b border-[#1A202E] hover:bg-[#1C2230]/50">
                <td className="px-4 py-3 text-sm font-medium text-[#F3F4F6]">{u.name}</td>
                <td className="px-4 py-3 text-sm text-[#9CA3AF] hidden md:table-cell">{u.email}</td>
                <td className="px-4 py-3">
                  {currentUser?.role === 'super_admin' && u.id !== currentUser.id ? (
                    <select
                      value={u.role}
                      onChange={e => handleChangeRole(u.id, e.target.value)}
                      className="px-2 py-1 text-xs bg-[#0A0D14] border border-[#232B3E] rounded text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37]"
                      data-testid={`role-select-${u.id}`}
                    >
                      {ROLES.map(r => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                    </select>
                  ) : (
                    roleBadge(u.role)
                  )}
                </td>
                <td className="px-4 py-3 text-right">
                  {currentUser?.role === 'super_admin' && u.id !== currentUser.id && (
                    <button onClick={() => handleDelete(u.id)} className="p-1.5 text-[#6B7280] hover:text-[#EF4444] transition-colors" data-testid={`delete-user-${u.id}`}>
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
