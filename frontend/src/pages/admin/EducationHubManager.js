import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, Loader2, BookOpen, Star, Plus, X, HelpCircle, GripVertical } from 'lucide-react';
import TipTapEditor from '../../components/TipTapEditor';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function EducationHubManager() {
  const [config, setConfig] = useState(null);
  const [eduPages, setEduPages] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [hubRes, pagesRes] = await Promise.all([
        axios.get(`${API}/education-hub`, { headers: getAuthHeader() }),
        axios.get(`${API}/education-hub/pages`, { headers: getAuthHeader() }),
      ]);
      setConfig(hubRes.data);
      setEduPages(pagesRes.data || []);
    } catch {}
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await axios.put(`${API}/admin/education-hub`, config, { headers: getAuthHeader() });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      alert('Save failed');
    } finally { setSaving(false); }
  };

  const updateSection = (si, field, value) => {
    const sections = [...(config.sections || [])];
    sections[si] = { ...sections[si], [field]: value };
    setConfig({ ...config, sections });
  };

  const addSlugToSection = (si, slug) => {
    const sections = [...(config.sections || [])];
    const current = sections[si].slugs || [];
    if (!current.includes(slug)) {
      sections[si] = { ...sections[si], slugs: [...current, slug] };
      setConfig({ ...config, sections });
    }
  };

  const removeSlugFromSection = (si, slug) => {
    const sections = [...(config.sections || [])];
    sections[si] = { ...sections[si], slugs: (sections[si].slugs || []).filter(s => s !== slug) };
    setConfig({ ...config, sections });
  };

  const addSection = () => {
    setConfig({
      ...config,
      sections: [...(config.sections || []), { title: 'New Section', description: '', slugs: [] }]
    });
  };

  const removeSection = (si) => {
    if (!window.confirm('Remove this section?')) return;
    setConfig({ ...config, sections: config.sections.filter((_, i) => i !== si) });
  };

  const updateFaq = (i, field, value) => {
    const faqs = [...(config.faqs || [])];
    faqs[i] = { ...faqs[i], [field]: value };
    setConfig({ ...config, faqs });
  };

  if (!config) {
    return (
      <div className="p-6 lg:p-8">
        <div className="h-8 w-48 bg-[#121620] rounded animate-pulse mb-6" />
        <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="h-24 bg-[#121620] rounded-lg animate-pulse" />)}</div>
      </div>
    );
  }

  const getPageTitle = (slug) => {
    const p = eduPages.find(pg => pg.slug === slug);
    return p ? p.title : slug;
  };

  const usedSlugs = new Set((config.sections || []).flatMap(s => s.slugs || []));

  return (
    <div className="p-6 lg:p-8 max-w-4xl" data-testid="education-hub-manager">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <BookOpen className="w-5 h-5 text-[#D4AF37]" />
          <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Education Hub</h1>
        </div>
        <button onClick={handleSave} disabled={saving}
          className={`flex items-center gap-1.5 px-5 py-2.5 text-sm font-medium rounded-lg transition-colors ${saved ? 'bg-[#10B981] text-white' : 'bg-[#D4AF37] text-black hover:bg-[#C39F2F]'} disabled:opacity-50`}
          data-testid="edu-hub-save-btn">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saved ? 'Saved!' : 'Save Changes'}
        </button>
      </div>

      <div className="space-y-6">
        {/* Hero Settings */}
        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <h2 className="text-sm font-bold text-[#F3F4F6] mb-4 uppercase tracking-wider">Hero Section</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">H1 Title</label>
              <input value={config.hero_title || ''} onChange={e => setConfig({ ...config, hero_title: e.target.value })}
                className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
                data-testid="edu-hero-title" />
            </div>
            <div>
              <label className="block text-xs text-[#6B7280] mb-1">Subtitle</label>
              <input value={config.hero_subtitle || ''} onChange={e => setConfig({ ...config, hero_subtitle: e.target.value })}
                className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
                data-testid="edu-hero-subtitle" />
            </div>
          </div>
        </section>

        {/* Intro Content */}
        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <h2 className="text-sm font-bold text-[#F3F4F6] mb-4 uppercase tracking-wider">SEO Intro Block</h2>
          <TipTapEditor
            content={config.intro_content || ''}
            onChange={(html) => setConfig(prev => ({ ...prev, intro_content: html }))}
          />
        </section>

        {/* Featured Guide */}
        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-4 h-4 text-[#D4AF37]" />
            <h2 className="text-sm font-bold text-[#F3F4F6] uppercase tracking-wider">Featured Guide</h2>
          </div>
          <select value={config.featured_slug || ''} onChange={e => setConfig({ ...config, featured_slug: e.target.value })}
            className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
            data-testid="edu-featured-select">
            <option value="">None</option>
            {eduPages.map(p => <option key={p.slug} value={p.slug}>{p.title}</option>)}
          </select>
        </section>

        {/* Sections */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-[#F3F4F6] uppercase tracking-wider">Topic Sections</h2>
            <button onClick={addSection} className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#D4AF37]/10 text-[#D4AF37] rounded-lg hover:bg-[#D4AF37]/20"
              data-testid="edu-add-section">
              <Plus className="w-3.5 h-3.5" /> Add Section
            </button>
          </div>

          <div className="space-y-4">
            {(config.sections || []).map((section, si) => (
              <div key={si} className="bg-[#121620] border border-[#232B3E] rounded-lg p-5" data-testid={`edu-section-${si}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <GripVertical className="w-4 h-4 text-[#6B7280]" />
                    <span className="text-xs text-[#6B7280]">Section {si + 1}</span>
                  </div>
                  <button onClick={() => removeSection(si)} className="p-1 text-[#6B7280] hover:text-[#EF4444]">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="space-y-3">
                  <input value={section.title || ''} onChange={e => updateSection(si, 'title', e.target.value)}
                    placeholder="Section Title"
                    className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" />
                  <input value={section.description || ''} onChange={e => updateSection(si, 'description', e.target.value)}
                    placeholder="Short description for this section"
                    className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" />

                  {/* Linked articles */}
                  <div>
                    <label className="block text-xs text-[#6B7280] mb-2">Linked Articles</label>
                    <div className="space-y-1.5 mb-2">
                      {(section.slugs || []).map(slug => (
                        <div key={slug} className="flex items-center justify-between px-3 py-2 bg-[#0A0D14] border border-[#1A202E] rounded text-sm">
                          <span className="text-[#F3F4F6]">{getPageTitle(slug)}</span>
                          <button onClick={() => removeSlugFromSection(si, slug)} className="text-[#6B7280] hover:text-[#EF4444]">
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                    <select onChange={e => { if (e.target.value) { addSlugToSection(si, e.target.value); e.target.value = ''; } }}
                      className="w-full px-3 py-2 bg-[#0A0D14] border border-[#232B3E] rounded text-[#9CA3AF] text-sm focus:outline-none focus:border-[#D4AF37]">
                      <option value="">+ Add article...</option>
                      {eduPages.filter(p => !usedSlugs.has(p.slug) || (section.slugs || []).includes(p.slug)).filter(p => !(section.slugs || []).includes(p.slug)).map(p => (
                        <option key={p.slug} value={p.slug}>{p.title}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Hub FAQs */}
        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-[#D4AF37]" />
              <h2 className="text-sm font-bold text-[#F3F4F6] uppercase tracking-wider">Hub FAQs</h2>
              <span className="text-[10px] text-[#6B7280]">({(config.faqs || []).length})</span>
            </div>
            <button onClick={() => setConfig({ ...config, faqs: [...(config.faqs || []), { question: '', answer: '' }] })}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#D4AF37]/10 text-[#D4AF37] rounded-lg hover:bg-[#D4AF37]/20"
              data-testid="edu-add-faq">
              <Plus className="w-3.5 h-3.5" /> Add FAQ
            </button>
          </div>
          <div className="space-y-3">
            {(config.faqs || []).map((faq, i) => (
              <div key={i} className="bg-[#0A0D14] border border-[#1A202E] rounded-lg p-3" data-testid={`edu-faq-${i}`}>
                <div className="flex items-start gap-2 mb-2">
                  <input value={faq.question || ''} onChange={e => updateFaq(i, 'question', e.target.value)}
                    placeholder={`Question ${i + 1}`}
                    className="flex-1 px-2.5 py-2 bg-[#121620] border border-[#232B3E] rounded text-sm text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37]" />
                  <button onClick={() => setConfig({ ...config, faqs: config.faqs.filter((_, j) => j !== i) })}
                    className="p-1.5 text-[#6B7280] hover:text-[#EF4444] flex-shrink-0">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <textarea value={faq.answer || ''} onChange={e => updateFaq(i, 'answer', e.target.value)}
                  placeholder="Answer..." rows={2}
                  className="w-full px-2.5 py-2 bg-[#121620] border border-[#232B3E] rounded text-sm text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37] resize-none" />
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
