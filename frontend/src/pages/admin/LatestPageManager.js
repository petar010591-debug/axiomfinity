import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, Loader2, HelpCircle, Plus, X, Newspaper } from 'lucide-react';
import TipTapEditor from '../../components/TipTapEditor';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function LatestPageManager() {
  const [config, setConfig] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      try {
        const { data } = await axios.get(`${API}/latest-page-config`, { headers: getAuthHeader() });
        setConfig(data);
      } catch {}
    };
    fetch();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await axios.put(`${API}/admin/latest-page-config`, config, { headers: getAuthHeader() });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch { alert('Save failed'); } finally { setSaving(false); }
  };

  const updateFaq = (i, field, value) => {
    const faqs = [...(config.faqs || [])];
    faqs[i] = { ...faqs[i], [field]: value };
    setConfig({ ...config, faqs });
  };

  if (!config) return <div className="p-6"><div className="h-8 w-48 bg-[#121620] rounded animate-pulse" /></div>;

  return (
    <div className="p-6 lg:p-8 max-w-4xl" data-testid="latest-page-manager">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Newspaper className="w-5 h-5 text-[#D4AF37]" />
          <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Latest Page Settings</h1>
        </div>
        <button onClick={handleSave} disabled={saving}
          className={`flex items-center gap-1.5 px-5 py-2.5 text-sm font-medium rounded-lg transition-colors ${saved ? 'bg-[#10B981] text-white' : 'bg-[#D4AF37] text-black hover:bg-[#C39F2F]'} disabled:opacity-50`}
          data-testid="latest-save-btn">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saved ? 'Saved!' : 'Save'}
        </button>
      </div>

      <div className="space-y-6">
        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <h2 className="text-sm font-bold text-[#F3F4F6] mb-3 uppercase tracking-wider">Page Title (H1)</h2>
          <input value={config.display_title || ''} onChange={e => setConfig({ ...config, display_title: e.target.value })}
            placeholder="Latest News"
            className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
            data-testid="latest-title" />
        </section>

        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <h2 className="text-sm font-bold text-[#F3F4F6] mb-3 uppercase tracking-wider">Intro Description</h2>
          <TipTapEditor content={config.description || ''} onChange={html => setConfig(prev => ({ ...prev, description: html }))} />
        </section>

        <section className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-[#D4AF37]" />
              <h2 className="text-sm font-bold text-[#F3F4F6] uppercase tracking-wider">FAQs</h2>
              <span className="text-[10px] text-[#6B7280]">({(config.faqs || []).length})</span>
            </div>
            <button onClick={() => setConfig({ ...config, faqs: [...(config.faqs || []), { question: '', answer: '' }] })}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#D4AF37]/10 text-[#D4AF37] rounded-lg hover:bg-[#D4AF37]/20">
              <Plus className="w-3.5 h-3.5" /> Add FAQ
            </button>
          </div>
          <div className="space-y-3">
            {(config.faqs || []).map((faq, i) => (
              <div key={i} className="bg-[#0A0D14] border border-[#1A202E] rounded-lg p-3">
                <div className="flex items-start gap-2 mb-2">
                  <input value={faq.question || ''} onChange={e => updateFaq(i, 'question', e.target.value)}
                    placeholder={`Question ${i + 1}`}
                    className="flex-1 px-2.5 py-2 bg-[#121620] border border-[#232B3E] rounded text-sm text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37]" />
                  <button onClick={() => setConfig({ ...config, faqs: config.faqs.filter((_, j) => j !== i) })}
                    className="p-1.5 text-[#6B7280] hover:text-[#EF4444]"><X className="w-3.5 h-3.5" /></button>
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
