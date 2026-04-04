import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { FileEdit, Plus, Trash2, Save, ArrowLeft, Loader2 } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PagesManager() {
  const [pages, setPages] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: '', slug: '', content: '', page_type: 'legal' });
  const [saving, setSaving] = useState(false);

  const fetchPages = async () => {
    try {
      const { data } = await axios.get(`${API}/pages`, { headers: getAuthHeader() });
      setPages(data);
    } catch {}
  };

  useEffect(() => { fetchPages(); }, []);

  const startEdit = (page) => {
    setEditing(page.id);
    setForm({ title: page.title, slug: page.slug, content: page.content || '', page_type: page.page_type || 'legal' });
  };

  const startNew = () => {
    setEditing('new');
    setForm({ title: '', slug: '', content: '', page_type: 'legal' });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editing === 'new') {
        await axios.post(`${API}/admin/pages`, form, { headers: getAuthHeader() });
      } else {
        await axios.put(`${API}/admin/pages/${editing}`, form, { headers: getAuthHeader() });
      }
      setEditing(null);
      fetchPages();
    } catch (e) {
      alert('Save failed');
    } finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this page?')) return;
    await axios.delete(`${API}/admin/pages/${id}`, { headers: getAuthHeader() });
    fetchPages();
  };

  if (editing) {
    return (
      <div className="p-6 lg:p-8" data-testid="page-editor">
        <button onClick={() => setEditing(null)} className="flex items-center gap-1.5 text-sm text-[#9CA3AF] hover:text-[#F3F4F6] mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to Pages
        </button>
        <h1 className="text-xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {editing === 'new' ? 'New Page' : `Edit: ${form.title}`}
        </h1>
        <div className="space-y-4 max-w-3xl">
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Title</label>
            <input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="page-title-input" />
          </div>
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Slug</label>
            <input value={form.slug} onChange={e => setForm({ ...form, slug: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              placeholder="privacy-policy" data-testid="page-slug-input" />
          </div>
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Type</label>
            <select value={form.page_type} onChange={e => setForm({ ...form, page_type: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]">
              <option value="legal">Legal</option>
              <option value="educational">Educational</option>
              <option value="about">About</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Content (HTML)</label>
            <textarea value={form.content} onChange={e => setForm({ ...form, content: e.target.value })}
              rows={16}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm font-mono focus:outline-none focus:border-[#D4AF37]"
              data-testid="page-content-input" />
          </div>
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50"
            data-testid="page-save-btn">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Save Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8" data-testid="pages-manager">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Pages</h1>
        <button onClick={startNew} className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F]" data-testid="new-page-btn">
          <Plus className="w-4 h-4" /> New Page
        </button>
      </div>
      <div className="space-y-2">
        {pages.map(page => (
          <div key={page.id} className="flex items-center justify-between p-4 bg-[#121620] border border-[#232B3E] rounded-lg" data-testid={`page-item-${page.slug}`}>
            <div>
              <p className="text-sm font-medium text-[#F3F4F6]">{page.title}</p>
              <p className="text-xs text-[#6B7280]">/{page.slug} &middot; {page.page_type}</p>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={() => startEdit(page)} className="px-3 py-1.5 text-xs text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/10" data-testid={`edit-page-${page.slug}`}>
                <FileEdit className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => handleDelete(page.id)} className="px-3 py-1.5 text-xs text-[#EF4444] border border-[#EF4444]/30 rounded-lg hover:bg-[#EF4444]/10">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
