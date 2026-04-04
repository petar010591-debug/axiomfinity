import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Plus, Trash2, Save, Upload, Loader2, GripVertical, ArrowUp, ArrowDown } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function TeamManager() {
  const [members, setMembers] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', role_title: '', bio: '', avatar_url: '' });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const fetchMembers = async () => {
    try {
      const { data } = await axios.get(`${API}/admin/team`, { headers: getAuthHeader() });
      setMembers(data);
    } catch {}
  };

  useEffect(() => { fetchMembers(); }, []);

  const startEdit = (m) => {
    setEditing(m.id);
    setForm({ name: m.name, role_title: m.role_title, bio: m.bio, avatar_url: m.avatar_url || '' });
  };

  const startNew = () => {
    setEditing('new');
    setForm({ name: '', role_title: '', bio: '', avatar_url: '' });
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await axios.post(`${API}/upload`, formData, { headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' } });
      setForm(prev => ({ ...prev, avatar_url: data.url }));
    } catch { alert('Upload failed'); }
    finally { setUploading(false); e.target.value = ''; }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editing === 'new') {
        await axios.post(`${API}/admin/team`, form, { headers: getAuthHeader() });
      } else {
        await axios.put(`${API}/admin/team/${editing}`, form, { headers: getAuthHeader() });
      }
      setEditing(null);
      fetchMembers();
    } catch { alert('Save failed'); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this team member?')) return;
    await axios.delete(`${API}/admin/team/${id}`, { headers: getAuthHeader() });
    fetchMembers();
  };

  const moveUp = async (idx) => {
    if (idx === 0) return;
    const updated = [...members];
    [updated[idx - 1], updated[idx]] = [updated[idx], updated[idx - 1]];
    for (let i = 0; i < updated.length; i++) {
      await axios.put(`${API}/admin/team/${updated[i].id}`, { order: i }, { headers: getAuthHeader() });
    }
    fetchMembers();
  };

  const moveDown = async (idx) => {
    if (idx >= members.length - 1) return;
    const updated = [...members];
    [updated[idx + 1], updated[idx]] = [updated[idx], updated[idx + 1]];
    for (let i = 0; i < updated.length; i++) {
      await axios.put(`${API}/admin/team/${updated[i].id}`, { order: i }, { headers: getAuthHeader() });
    }
    fetchMembers();
  };

  if (editing) {
    return (
      <div className="p-6 lg:p-8" data-testid="team-editor">
        <button onClick={() => setEditing(null)} className="text-sm text-[#9CA3AF] hover:text-[#F3F4F6] mb-6">&larr; Back</button>
        <h1 className="text-xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {editing === 'new' ? 'Add Team Member' : `Edit: ${form.name}`}
        </h1>
        <div className="space-y-4 max-w-lg">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-full bg-[#1C2230] border-2 border-[#D4AF37]/30 overflow-hidden flex-shrink-0">
              {form.avatar_url ? <img src={form.avatar_url} alt="" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-[#6B7280] text-2xl font-bold">{form.name?.[0] || '?'}</div>}
            </div>
            <label className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm cursor-pointer ${uploading ? 'bg-[#232B3E] text-[#6B7280]' : 'bg-[#D4AF37] text-black hover:bg-[#C39F2F]'}`}>
              {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              {uploading ? 'Uploading...' : 'Upload Photo'}
              <input type="file" accept="image/*" className="hidden" disabled={uploading} onChange={handleUpload} />
            </label>
          </div>
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Full Name</label>
            <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="team-name-input" />
          </div>
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Role / Title</label>
            <input value={form.role_title} onChange={e => setForm({ ...form, role_title: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              placeholder="e.g. Senior Editor, Managing Director" data-testid="team-role-input" />
          </div>
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Bio / Description</label>
            <textarea value={form.bio} onChange={e => setForm({ ...form, bio: e.target.value })} rows={4}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="team-bio-input" />
          </div>
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50"
            data-testid="team-save-btn">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Save
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8" data-testid="team-manager">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Team Members</h1>
        <button onClick={startNew} className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F]" data-testid="add-team-btn">
          <Plus className="w-4 h-4" /> Add Member
        </button>
      </div>
      <p className="text-xs text-[#6B7280] mb-4">These appear on the About page. Use arrows to reorder.</p>
      <div className="space-y-2">
        {members.map((m, idx) => (
          <div key={m.id} className="flex items-center gap-4 p-4 bg-[#121620] border border-[#232B3E] rounded-lg" data-testid={`team-member-${m.id}`}>
            <div className="flex flex-col gap-1">
              <button onClick={() => moveUp(idx)} disabled={idx === 0} className="text-[#6B7280] hover:text-[#D4AF37] disabled:opacity-20"><ArrowUp className="w-3.5 h-3.5" /></button>
              <button onClick={() => moveDown(idx)} disabled={idx === members.length - 1} className="text-[#6B7280] hover:text-[#D4AF37] disabled:opacity-20"><ArrowDown className="w-3.5 h-3.5" /></button>
            </div>
            <div className="w-12 h-12 rounded-full bg-[#1C2230] overflow-hidden flex-shrink-0">
              {m.avatar_url ? <img src={m.avatar_url} alt="" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-[#6B7280] font-bold">{m.name?.[0]}</div>}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[#F3F4F6]">{m.name}</p>
              <p className="text-xs text-[#D4AF37]">{m.role_title}</p>
              <p className="text-xs text-[#6B7280] truncate">{m.bio}</p>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => startEdit(m)} className="px-3 py-1.5 text-xs text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/10">Edit</button>
              <button onClick={() => handleDelete(m.id)} className="px-3 py-1.5 text-xs text-[#EF4444] border border-[#EF4444]/30 rounded-lg hover:bg-[#EF4444]/10"><Trash2 className="w-3.5 h-3.5" /></button>
            </div>
          </div>
        ))}
        {members.length === 0 && <p className="text-sm text-[#6B7280] text-center py-8">No team members yet. Click "Add Member" to start.</p>}
      </div>
    </div>
  );
}
