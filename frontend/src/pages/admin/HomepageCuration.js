import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, RefreshCw, ArrowUpDown } from 'lucide-react';
import { Link } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function HomepageCuration() {
  const [articles, setArticles] = useState([]);
  const [heroPrimary, setHeroPrimary] = useState('');
  const [heroSecondary, setHeroSecondary] = useState(['', '']);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesRes, homepageRes] = await Promise.all([
          axios.get(`${API}/admin/articles?limit=50&status=published`, { headers: getAuthHeader() }),
          axios.get(`${API}/admin/homepage`, { headers: getAuthHeader() })
        ]);
        setArticles(articlesRes.data.articles || []);
        if (homepageRes.data.hero_primary) setHeroPrimary(homepageRes.data.hero_primary);
        if (homepageRes.data.hero_secondary?.length) {
          const sec = [...homepageRes.data.hero_secondary];
          while (sec.length < 2) sec.push('');
          setHeroSecondary(sec.slice(0, 4));
        }
      } catch {} finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSuccess('');
    try {
      await axios.put(`${API}/admin/homepage`, {
        hero_primary: heroPrimary || null,
        hero_secondary: heroSecondary.filter(Boolean)
      }, { headers: getAuthHeader() });
      setSuccess('Homepage updated successfully');
      setTimeout(() => setSuccess(''), 3000);
    } catch {} finally { setSaving(false); }
  };

  const updateSecondary = (index, value) => {
    const updated = [...heroSecondary];
    updated[index] = value;
    setHeroSecondary(updated);
  };

  if (loading) {
    return <div className="p-6 lg:p-8"><div className="h-64 bg-[#121620] rounded-lg animate-pulse" /></div>;
  }

  return (
    <div className="p-6 lg:p-8 max-w-3xl" data-testid="homepage-curation-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Homepage Curation</h1>
          <p className="text-sm text-[#6B7280] mt-1">Control which articles appear in the hero section</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/admin/homepage/order" className="flex items-center gap-1.5 px-3 py-2 text-xs text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/10" data-testid="section-order-link">
            <ArrowUpDown className="w-3.5 h-3.5" /> Section Order
          </Link>
          <button onClick={handleSave} disabled={saving}
            className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50 transition-colors"
            data-testid="homepage-save-btn">
            <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {success && (
        <div className="mb-4 p-3 bg-[#10B981]/10 border border-[#10B981]/30 rounded-lg text-sm text-[#10B981]">{success}</div>
      )}

      <div className="space-y-6">
        {/* Hero Primary */}
        <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <label className="block text-sm font-medium text-[#D4AF37] mb-3">Hero Primary (Large Card)</label>
          <select
            value={heroPrimary} onChange={e => setHeroPrimary(e.target.value)}
            className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
            data-testid="hero-primary-select"
          >
            <option value="">Auto (latest article)</option>
            {articles.map(a => <option key={a.id} value={a.id}>{a.title}</option>)}
          </select>
        </div>

        {/* Hero Secondary */}
        <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
          <label className="block text-sm font-medium text-[#D4AF37] mb-3">Hero Secondary (Side Cards)</label>
          <div className="space-y-3">
            {heroSecondary.map((val, i) => (
              <div key={i}>
                <label className="block text-xs text-[#6B7280] mb-1">Card {i + 1}</label>
                <select
                  value={val} onChange={e => updateSecondary(i, e.target.value)}
                  className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
                  data-testid={`hero-secondary-select-${i}`}
                >
                  <option value="">Auto</option>
                  {articles.map(a => <option key={a.id} value={a.id}>{a.title}</option>)}
                </select>
              </div>
            ))}
            {heroSecondary.length < 4 && (
              <button
                type="button"
                onClick={() => setHeroSecondary([...heroSecondary, ''])}
                className="text-xs text-[#D4AF37] hover:underline"
              >
                + Add another card
              </button>
            )}
          </div>
        </div>

        <p className="text-xs text-[#6B7280] leading-relaxed">
          Leave selections empty to automatically show the latest published articles. Changes will be visible on the homepage immediately after saving.
        </p>
      </div>
    </div>
  );
}
