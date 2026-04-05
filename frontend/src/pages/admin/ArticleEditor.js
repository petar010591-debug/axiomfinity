import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, ArrowLeft, Eye, Calendar, Upload, Loader2, Image as ImageIcon } from 'lucide-react';
import TipTapEditor from '../../components/TipTapEditor';
import MediaLibrary from '../../components/MediaLibrary';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ArticleEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = !!id;

  const [form, setForm] = useState({
    title: '', excerpt: '', content: '', featured_image: '', category_id: '', secondary_categories: [], tags: [], status: 'draft', is_sponsored: false, meta_title: '', meta_description: '', scheduled_at: '', og_image: ''
  });
  const [categories, setCategories] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [tagInput, setTagInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showMediaLibrary, setShowMediaLibrary] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [catsRes, tagsRes] = await Promise.all([
          axios.get(`${API}/categories`),
          axios.get(`${API}/tags`)
        ]);
        setCategories(catsRes.data || []);
        setAllTags(tagsRes.data || []);

        if (isEditing) {
          const { data } = await axios.get(`${API}/admin/articles/${id}`, { headers: getAuthHeader() });
          setForm({
            title: data.title || '',
            excerpt: data.excerpt || '',
            content: data.content || '',
            featured_image: data.featured_image || '',
            category_id: data.category_id || '',
            secondary_categories: data.categories?.filter(c => c !== data.category_slug) || [],
            tags: data.tags || [],
            status: data.status || 'draft',
            is_sponsored: data.is_sponsored || false,
            meta_title: data.meta_title || '',
            meta_description: data.meta_description || '',
            scheduled_at: data.scheduled_at || '',
            og_image: data.og_image || '',
          });
        }
      } catch {}
    };
    fetchData();
  }, [id, isEditing]);

  const updateField = (field, value) => setForm(prev => ({ ...prev, [field]: value }));

  const addTag = () => {
    const tag = tagInput.trim();
    if (tag && !form.tags.includes(tag)) {
      updateField('tags', [...form.tags, tag]);
    }
    setTagInput('');
  };

  const removeTag = (tag) => updateField('tags', form.tags.filter(t => t !== tag));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) { setError('Title is required'); return; }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      if (isEditing) {
        await axios.put(`${API}/admin/articles/${id}`, form, { headers: getAuthHeader() });
        setSuccess('Article updated successfully');
      } else {
        const { data } = await axios.post(`${API}/admin/articles`, form, { headers: getAuthHeader() });
        setSuccess('Article created successfully');
        setTimeout(() => navigate(`/admin/articles/edit/${data.id}`), 1000);
      }
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to save article');
    } finally { setSaving(false); }
  };

  return (
    <div className="p-6 lg:p-8 max-w-4xl" data-testid="article-editor-page">
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/admin/articles')} className="p-2 text-[#6B7280] hover:text-[#F3F4F6] transition-colors" data-testid="back-to-articles-btn">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {isEditing ? 'Edit Article' : 'New Article'}
        </h1>
      </div>

      {error && <div className="mb-4 p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg text-sm text-[#EF4444]" data-testid="editor-error">{error}</div>}
      {success && <div className="mb-4 p-3 bg-[#10B981]/10 border border-[#10B981]/30 rounded-lg text-sm text-[#10B981]" data-testid="editor-success">{success}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Title *</label>
          <input
            type="text" value={form.title} onChange={e => updateField('title', e.target.value)}
            className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
            placeholder="Article title"
            data-testid="article-title-input"
          />
        </div>

        {/* Excerpt */}
        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Excerpt</label>
          <textarea
            rows={2} value={form.excerpt} onChange={e => updateField('excerpt', e.target.value)}
            className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] resize-none"
            placeholder="Brief summary..."
            data-testid="article-excerpt-input"
          />
        </div>

        {/* Content - TipTap WYSIWYG */}
        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Content</label>
          <TipTapEditor content={form.content} onChange={(html) => updateField('content', html)} />
        </div>

        {/* Featured Image */}
        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Featured Image</label>
          <div className="flex gap-2">
            <input
              type="text" value={form.featured_image} onChange={e => updateField('featured_image', e.target.value)}
              className="flex-1 px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              placeholder="https://... or upload / choose from library"
              data-testid="article-image-input"
            />
            <button
              type="button"
              onClick={() => setShowMediaLibrary(true)}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium bg-[#1C2230] text-[#D4AF37] border border-[#D4AF37]/30 hover:bg-[#D4AF37]/10 transition-colors"
              data-testid="media-library-btn"
            >
              <ImageIcon className="w-4 h-4" /> Library
            </button>
            <label className={`flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium cursor-pointer transition-colors ${uploading ? 'bg-[#232B3E] text-[#6B7280]' : 'bg-[#D4AF37] text-black hover:bg-[#C39F2F]'}`} data-testid="image-upload-btn">
              {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              {uploading ? 'Uploading...' : 'Upload'}
              <input
                type="file" accept="image/*" className="hidden" disabled={uploading}
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  setUploading(true);
                  setError('');
                  try {
                    const formData = new FormData();
                    formData.append('file', file);
                    const { data } = await axios.post(`${API}/upload`, formData, {
                      headers: getAuthHeader()
                    });
                    updateField('featured_image', data.url);
                  } catch (err) {
                    setError('Image upload failed. Check Cloudinary configuration.');
                  } finally {
                    setUploading(false);
                    e.target.value = '';
                  }
                }}
              />
            </label>
          </div>
          {form.featured_image && (
            <div className="mt-2 rounded-lg overflow-hidden border border-[#232B3E] max-w-xs">
              <img src={form.featured_image} alt="Preview" className="w-full h-32 object-cover" />
            </div>
          )}
        </div>

        {/* Media Library Modal */}
        {showMediaLibrary && (
          <MediaLibrary
            onSelect={(url) => updateField('featured_image', url)}
            onClose={() => setShowMediaLibrary(false)}
          />
        )}

        {/* Category + Status row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Primary Category</label>
            <select
              value={form.category_id} onChange={e => updateField('category_id', e.target.value)}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="article-category-select"
            >
              <option value="">Select category</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Status</label>
            <select
              value={form.status} onChange={e => updateField('status', e.target.value)}
              className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="article-status-select"
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="scheduled">Scheduled</option>
              <option value="archived">Archived</option>
            </select>
          </div>
        </div>

        {/* Scheduling */}
        {form.status === 'scheduled' && (
          <div className="bg-[#1C2230] border border-[#232B3E] rounded-lg p-4">
            <label className="flex items-center gap-2 text-sm font-medium text-[#D4AF37] mb-2">
              <Calendar className="w-4 h-4" /> Schedule Publication (CET)
            </label>
            <input
              type="datetime-local"
              value={(() => {
                if (!form.scheduled_at) return '';
                // Convert stored UTC to CET for display
                const d = new Date(form.scheduled_at);
                const cet = new Date(d.toLocaleString('en-US', { timeZone: 'Europe/Berlin' }));
                const y = cet.getFullYear();
                const m = String(cet.getMonth() + 1).padStart(2, '0');
                const day = String(cet.getDate()).padStart(2, '0');
                const h = String(cet.getHours()).padStart(2, '0');
                const min = String(cet.getMinutes()).padStart(2, '0');
                return `${y}-${m}-${day}T${h}:${min}`;
              })()}
              onChange={e => {
                if (!e.target.value) { updateField('scheduled_at', ''); return; }
                // Input is in CET — convert to UTC for storage
                // CET is UTC+1 (or UTC+2 during CEST)
                const cetStr = e.target.value;
                // Create date assuming CET by appending the offset
                // Use Intl to determine current CET offset
                const tempDate = new Date(cetStr);
                const utcRef = new Date(tempDate.toLocaleString('en-US', { timeZone: 'UTC' }));
                const cetRef = new Date(tempDate.toLocaleString('en-US', { timeZone: 'Europe/Berlin' }));
                const offsetMs = cetRef - utcRef;
                const utcDate = new Date(tempDate.getTime() - offsetMs);
                updateField('scheduled_at', utcDate.toISOString());
              }}
              className="w-full max-w-xs px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="article-schedule-input"
            />
            <p className="text-xs text-[#6B7280] mt-2">All times in Central European Time (CET). Article will auto-publish at this time.</p>
          </div>
        )}

        {/* Secondary Categories */}
        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Additional Categories</label>
          <p className="text-xs text-[#6B7280] mb-2">Select extra categories this article should appear in (e.g., Sponsored, Educational)</p>
          <div className="flex flex-wrap gap-2">
            {categories.map(c => {
              const isSelected = form.secondary_categories.includes(c.slug);
              return (
                <button
                  key={c.id} type="button"
                  onClick={() => {
                    if (isSelected) updateField('secondary_categories', form.secondary_categories.filter(s => s !== c.slug));
                    else updateField('secondary_categories', [...form.secondary_categories, c.slug]);
                  }}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${isSelected ? 'bg-[#D4AF37] text-black' : 'bg-[#1C2230] text-[#9CA3AF] border border-[#232B3E] hover:border-[#D4AF37]'}`}
                  data-testid={`secondary-cat-${c.slug}`}
                >
                  {c.name}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Tags</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {form.tags.map(tag => (
              <span key={tag} className="flex items-center gap-1 px-2.5 py-1 text-xs bg-[#D4AF37]/10 text-[#D4AF37] rounded-full">
                {tag}
                <button type="button" onClick={() => removeTag(tag)} className="hover:text-[#EF4444]">&times;</button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text" value={tagInput} onChange={e => setTagInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addTag(); } }}
              className="flex-1 px-3 py-2 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              placeholder="Add tag..."
              data-testid="article-tag-input"
            />
            <button type="button" onClick={addTag} className="px-3 py-2 text-xs bg-[#1C2230] text-[#9CA3AF] rounded-lg hover:text-[#D4AF37] border border-[#232B3E]">Add</button>
          </div>
          {allTags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {allTags.filter(t => !form.tags.includes(t.name)).slice(0, 10).map(t => (
                <button key={t.id} type="button" onClick={() => updateField('tags', [...form.tags, t.name])} className="px-2 py-0.5 text-[10px] text-[#6B7280] bg-[#1C2230] rounded hover:text-[#D4AF37] transition-colors">
                  + {t.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Sponsored */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox" id="sponsored" checked={form.is_sponsored} onChange={e => updateField('is_sponsored', e.target.checked)}
            className="w-4 h-4 rounded border-[#232B3E] bg-[#121620] text-[#D4AF37] focus:ring-[#D4AF37]"
            data-testid="article-sponsored-checkbox"
          />
          <label htmlFor="sponsored" className="text-sm text-[#9CA3AF]">Sponsored content</label>
        </div>

        {/* SEO */}
        <details className="border border-[#232B3E] rounded-lg">
          <summary className="px-4 py-3 text-sm font-medium text-[#9CA3AF] cursor-pointer hover:text-[#F3F4F6]">SEO Settings</summary>
          <div className="px-4 pb-4 space-y-3">
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">Meta Title</label>
              <input type="text" value={form.meta_title} onChange={e => updateField('meta_title', e.target.value)} className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" />
            </div>
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">Meta Description</label>
              <textarea rows={2} value={form.meta_description} onChange={e => updateField('meta_description', e.target.value)} className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] resize-none" />
            </div>
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">OG Image URL (for social sharing)</label>
              <input type="text" value={form.og_image} onChange={e => updateField('og_image', e.target.value)} placeholder="Defaults to featured image" className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="og-image-input" />
            </div>
          </div>
        </details>

        {/* Submit */}
        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit" disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50 transition-colors"
            data-testid="article-save-btn"
          >
            <Save className="w-4 h-4" /> {saving ? 'Saving...' : (isEditing ? 'Update Article' : 'Create Article')}
          </button>
          <button type="button" onClick={() => navigate('/admin/articles')} className="px-4 py-2.5 text-sm text-[#9CA3AF] hover:text-[#F3F4F6] transition-colors">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
