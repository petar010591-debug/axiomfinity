import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, Globe, Loader2 } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function SeoSettings() {
  const [nofollowEnabled, setNofollowEnabled] = useState(true);
  const [excludedDomains, setExcludedDomains] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      try {
        const { data } = await axios.get(`${API}/admin/seo-settings`, { headers: getAuthHeader() });
        setNofollowEnabled(data.nofollow_enabled);
        setExcludedDomains(data.excluded_domains);
      } catch {}
    };
    fetch();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await axios.put(`${API}/admin/seo-settings`, { nofollow_enabled: nofollowEnabled, excluded_domains: excludedDomains }, { headers: getAuthHeader() });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch { alert('Save failed'); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-6 lg:p-8" data-testid="seo-settings">
      <h1 className="text-xl font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>SEO / Nofollow Settings</h1>
      <p className="text-sm text-[#6B7280] mb-8">Control how external links behave across your site.</p>

      <div className="max-w-2xl space-y-6">
        {/* Nofollow toggle */}
        <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-[#F3F4F6]">Apply nofollow to external links</p>
              <p className="text-xs text-[#6B7280] mt-1">
                When enabled, <code className="text-[#D4AF37] bg-[#1C2230] px-1 rounded">rel="nofollow"</code> and <code className="text-[#D4AF37] bg-[#1C2230] px-1 rounded">target="_blank"</code> will be added to all external links in articles.
              </p>
            </div>
            <button
              onClick={() => setNofollowEnabled(!nofollowEnabled)}
              className={`w-12 h-6 rounded-full transition-colors relative ${nofollowEnabled ? 'bg-[#D4AF37]' : 'bg-[#232B3E]'}`}
              data-testid="nofollow-toggle"
            >
              <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-transform ${nofollowEnabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>
        </div>

        {/* Excluded domains */}
        <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <label className="block text-sm font-medium text-[#F3F4F6] mb-1">Exclude Domains (dofollow)</label>
          <p className="text-xs text-[#6B7280] mb-3">
            Links to these domains will NOT get <code className="text-[#D4AF37] bg-[#1C2230] px-1 rounded">rel="nofollow"</code>. Comma-separated. Don't include http:// or https://
          </p>
          <textarea
            value={excludedDomains}
            onChange={e => setExcludedDomains(e.target.value)}
            rows={8}
            placeholder="example.com, trusted-site.org, partner-brand.io"
            className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm font-mono focus:outline-none focus:border-[#D4AF37]"
            data-testid="excluded-domains-input"
          />
          <p className="text-xs text-[#6B7280] mt-2">
            Domains must be comma-separated. Example: <span className="text-[#9CA3AF]">cointelegraph.com, reuters.com, bloomberg.com</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50"
            data-testid="seo-save-btn">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Save Changes
          </button>
          {saved && <span className="text-sm text-[#10B981]">Saved!</span>}
        </div>
      </div>
    </div>
  );
}
