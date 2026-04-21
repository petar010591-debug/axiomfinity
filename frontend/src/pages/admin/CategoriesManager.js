import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Plus, Trash2, PenLine, X } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function CategoriesManager() {
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [showCatForm, setShowCatForm] = useState(false);
  const [editingCat, setEditingCat] = useState(null);
  const [catForm, setCatForm] = useState({ name: '', description: '' });
  const [tagInput, setTagInput] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchData = async () => {
    try {
      const [catsRes, tagsRes] = await Promise.all([
        axios.get(`${API}/categories`),
        axios.get(`${API}/tags`)
      ]);
      setCategories(catsRes.data || []);
      setTags(tagsRes.data || []);
    } catch {}
  };

  useEffect(() => { fetchData(); }, []);

  const handleSaveCategory = async (e) => {
    e.preventDefault();
    if (!catForm.name.trim()) return;
    setSaving(true);
    try {
      if (editingCat) {
        await axios.put(`${API}/admin/categories/${editingCat.id}`, catForm, { headers: getAuthHeader() });
      } else {
        await axios.post(`${API}/admin/categories`, catForm, { headers: getAuthHeader() });
      }
      setShowCatForm(false);
      setEditingCat(null);
      setCatForm({ name: '', description: '' });
      fetchData();
    } catch {} finally { setSaving(false); }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm('Delete this category?')) return;
    try {
      await axios.delete(`${API}/admin/categories/${id}`, { headers: getAuthHeader() });
      fetchData();
    } catch {}
  };

  const handleAddTag = async () => {
    if (!tagInput.trim()) return;
    try {
      await axios.post(`${API}/admin/tags`, { name: tagInput.trim() }, { headers: getAuthHeader() });
      setTagInput('');
      fetchData();
    } catch {}
  };

  const handleDeleteTag = async (id) => {
    try {
      await axios.delete(`${API}/admin/tags/${id}`, { headers: getAuthHeader() });
      fetchData();
    } catch {}
  };

  const startEdit = (cat) => {
    setEditingCat(cat);
    setCatForm({ name: cat.name, description: cat.description || '' });
    setShowCatForm(true);
  };

  return (
    <div className="p-6 lg:p-8" data-testid="categories-manager-page">
      <h1 className="text-xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Categories & Tags</h1>

      {/* Categories Section */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold uppercase tracking-[0.15em] text-[#9CA3AF]">Categories</h2>
          <button
            onClick={() => { setShowCatForm(true); setEditingCat(null); setCatForm({ name: '', description: '' }); }}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] transition-colors"
            data-testid="add-category-btn"
          >
            <Plus className="w-3.5 h-3.5" /> Add Category
          </button>
        </div>

        {/* Category Form */}
        {showCatForm && (
          <form onSubmit={handleSaveCategory} className="bg-[#121620] border border-[#232B3E] rounded-lg p-4 mb-4 space-y-3" data-testid="category-form">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-[#F3F4F6]">{editingCat ? 'Edit Category' : 'New Category'}</h3>
              <button type="button" onClick={() => { setShowCatForm(false); setEditingCat(null); }} className="text-[#6B7280] hover:text-[#F3F4F6]">
                <X className="w-4 h-4" />
              </button>
            </div>
            <input
              type="text" value={catForm.name} onChange={e => setCatForm({ ...catForm, name: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              placeholder="Category name"
              data-testid="category-name-input"
            />
            <textarea
              value={catForm.description} onChange={e => setCatForm({ ...catForm, description: e.target.value })}
              className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] resize-none"
              placeholder="SEO description (200-300 words recommended for category page intro)"
              rows={4}
              data-testid="category-description-input"
            />
            <button type="submit" disabled={saving} className="px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50" data-testid="category-save-btn">
              {saving ? 'Saving...' : (editingCat ? 'Update' : 'Create')}
            </button>
          </form>
        )}

        {/* Categories List */}
        <div className="space-y-2">
          {categories.map(cat => (
            <div key={cat.id} className="flex items-center justify-between px-4 py-3 bg-[#121620] border border-[#232B3E] rounded-lg">
              <div>
                <span className="text-sm font-medium text-[#F3F4F6]">{cat.name}</span>
                {cat.description && <span className="text-xs text-[#6B7280] ml-2">— {cat.description}</span>}
                <span className="text-xs text-[#6B7280] ml-2">/{cat.slug}</span>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => startEdit(cat)} className="p-1.5 text-[#6B7280] hover:text-[#D4AF37] transition-colors" data-testid={`edit-cat-${cat.id}`}>
                  <PenLine className="w-3.5 h-3.5" />
                </button>
                <button onClick={() => handleDeleteCategory(cat.id)} className="p-1.5 text-[#6B7280] hover:text-[#EF4444] transition-colors" data-testid={`delete-cat-${cat.id}`}>
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tags Section */}
      <div>
        <h2 className="text-sm font-bold uppercase tracking-[0.15em] text-[#9CA3AF] mb-4">Tags</h2>
        <div className="flex gap-2 mb-4">
          <input
            type="text" value={tagInput} onChange={e => setTagInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddTag(); } }}
            className="flex-1 max-w-xs px-3 py-2 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
            placeholder="New tag name..."
            data-testid="new-tag-input"
          />
          <button onClick={handleAddTag} className="px-3 py-2 text-xs bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F]" data-testid="add-tag-btn">
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {tags.map(tag => (
            <span key={tag.id} className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-[#121620] text-[#9CA3AF] border border-[#232B3E] rounded-full">
              {tag.name}
              <button onClick={() => handleDeleteTag(tag.id)} className="text-[#6B7280] hover:text-[#EF4444] transition-colors" data-testid={`delete-tag-${tag.id}`}>
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
