import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { FileEdit, Plus, Trash2, Save, ArrowLeft, Loader2, HelpCircle, X, Upload, Image as ImageIcon } from 'lucide-react';
import TipTapEditor from '../../components/TipTapEditor';
import MediaLibrary from '../../components/MediaLibrary';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function PagesManager() {
  const [pages, setPages] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: '', slug: '', content: '', page_type: 'legal', faqs: [], meta_title: '', meta_description: '', featured_image: '' });
  const [saving, setSaving] = useState(false);
  const [showMediaLibrary, setShowMediaLibrary] = useState(false);

  const fetchPages = async () => {
    try {
      const { data } = await axios.get(`${API}/pages`, { headers: getAuthHeader() });
      setPages(data);
    } catch {}
  };

  useEffect(() => { fetchPages(); }, []);

  const startEdit = (page) => {
    setEditing(page.id);
    setForm({
      title: page.title,
      slug: page.slug,
      content: page.content || '',
      page_type: page.page_type || 'legal',
      faqs: page.faqs || [],
      meta_title: page.meta_title || '',
      meta_description: page.meta_description || '',
      featured_image: page.featured_image || '',
    });
  };

  const startNew = () => {
    setEditing('new');
    setForm({ title: '', slug: '', content: '', page_type: 'legal', faqs: [], meta_title: '', meta_description: '', featured_image: '' });
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

  const updateFaq = (index, field, value) => {
    const updated = [...form.faqs];
    updated[index] = { ...updated[index], [field]: value };
    setForm({ ...form, faqs: updated });
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
        <div className="space-y-5 max-w-4xl">
          {/* Title */}
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Title</label>
            <input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="page-title-input" />
          </div>

          {/* Slug */}
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Slug</label>
            <input value={form.slug} onChange={e => setForm({ ...form, slug: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              placeholder="privacy-policy" data-testid="page-slug-input" />
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Type</label>
            <select value={form.page_type} onChange={e => setForm({ ...form, page_type: e.target.value })}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]">
              <option value="legal">Legal</option>
              <option value="educational">Educational</option>
              <option value="about">About</option>
            </select>
          </div>

          {/* Featured Image */}
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Featured Image</label>
            {form.featured_image ? (
              <div className="relative rounded-lg overflow-hidden mb-2">
                <img src={form.featured_image} alt="" className="w-full h-48 object-cover rounded-lg" />
                <button type="button" onClick={() => setForm({ ...form, featured_image: '' })}
                  className="absolute top-2 right-2 p-1.5 bg-[#0A0D14]/80 rounded-lg text-[#EF4444] hover:bg-[#EF4444]/20">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button type="button" onClick={() => setShowMediaLibrary(true)}
                className="w-full flex items-center justify-center gap-2 px-4 py-8 border-2 border-dashed border-[#232B3E] rounded-lg text-sm text-[#6B7280] hover:border-[#D4AF37]/50 hover:text-[#D4AF37] transition-colors"
                data-testid="page-featured-image-btn">
                <ImageIcon className="w-5 h-5" /> Upload Featured Image
              </button>
            )}
          </div>

          {/* TipTap WYSIWYG Content Editor */}
          <div>
            <label className="block text-sm text-[#9CA3AF] mb-1">Content</label>
            <TipTapEditor
              content={form.content}
              onChange={(html) => setForm(prev => ({ ...prev, content: html }))}
            />
          </div>

          {/* SEO Meta Fields */}
          <div className="border border-[#232B3E] rounded-lg p-4 space-y-3">
            <p className="text-sm font-medium text-[#F3F4F6]">SEO Settings</p>
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">Meta Title</label>
              <input value={form.meta_title} onChange={e => setForm({ ...form, meta_title: e.target.value })}
                placeholder={form.title ? `${form.title} | AxiomFinity` : 'Auto-generated from title'}
                className="w-full px-3 py-2 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
                data-testid="page-meta-title" />
            </div>
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">Meta Description</label>
              <textarea value={form.meta_description} onChange={e => setForm({ ...form, meta_description: e.target.value })}
                rows={2} placeholder="Brief description for search engines (150-160 characters)"
                className="w-full px-3 py-2 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] resize-none"
                data-testid="page-meta-description" />
            </div>
          </div>

          {/* FAQ Section */}
          <div className="border border-[#232B3E] rounded-lg p-4" data-testid="page-faq-section">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-sm font-medium text-[#F3F4F6]">
                <HelpCircle className="w-4 h-4 text-[#D4AF37]" /> FAQs <span className="text-[10px] text-[#6B7280]">({form.faqs.length} items)</span>
              </div>
              <button
                type="button"
                onClick={() => setForm({ ...form, faqs: [...form.faqs, { question: '', answer: '' }] })}
                className="px-3 py-1 text-xs bg-[#D4AF37]/10 text-[#D4AF37] rounded-lg hover:bg-[#D4AF37]/20 transition-colors"
                data-testid="page-faq-add-btn"
              >
                + Add FAQ
              </button>
            </div>
            {form.faqs.length === 0 && (
              <p className="text-xs text-[#6B7280] py-2">No FAQs yet. Add one to improve SEO with structured data.</p>
            )}
            <div className="space-y-3">
              {form.faqs.map((faq, i) => (
                <div key={i} className="bg-[#0A0D14] border border-[#1A202E] rounded-lg p-3" data-testid={`page-faq-item-${i}`}>
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <div className="flex-1">
                        <input
                          placeholder={`Question ${i + 1}`}
                          value={faq.question}
                          onChange={e => updateFaq(i, 'question', e.target.value)}
                          className="w-full px-2.5 py-2 bg-[#121620] border border-[#232B3E] rounded text-sm text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37]"
                          data-testid={`page-faq-question-${i}`}
                        />
                      </div>
                      <button
                        onClick={() => setForm({ ...form, faqs: form.faqs.filter((_, j) => j !== i) })}
                        className="p-1.5 text-[#6B7280] hover:text-[#EF4444] transition-colors flex-shrink-0"
                        data-testid={`page-faq-remove-${i}`}
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <textarea
                      placeholder="Answer..."
                      value={faq.answer}
                      onChange={e => updateFaq(i, 'answer', e.target.value)}
                      rows={2}
                      className="w-full px-2.5 py-2 bg-[#121620] border border-[#232B3E] rounded text-sm text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37] resize-none"
                      data-testid={`page-faq-answer-${i}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Save Button */}
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50"
            data-testid="page-save-btn">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Save Page
          </button>
        </div>

        {/* Media Library Modal */}
        {showMediaLibrary && (
          <MediaLibrary
            onSelect={(url) => { setForm(prev => ({ ...prev, featured_image: url })); setShowMediaLibrary(false); }}
            onClose={() => setShowMediaLibrary(false)}
          />
        )}
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
              <p className="text-xs text-[#6B7280]">/{page.slug} &middot; {page.page_type}{page.faqs?.length > 0 ? ` &middot; ${page.faqs.length} FAQs` : ''}</p>
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
