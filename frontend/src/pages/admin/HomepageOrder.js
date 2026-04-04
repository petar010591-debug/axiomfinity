import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, ArrowUp, ArrowDown, Loader2 } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SECTION_LABELS = {
  latest: 'Latest News (Hero)',
  crypto: 'Crypto',
  press_releases: 'Press Releases',
  sponsored: 'Sponsored',
  others: 'More Stories',
};

export default function HomepageOrder() {
  const [sections, setSections] = useState(['latest', 'crypto', 'press_releases', 'sponsored', 'others']);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      try {
        const { data } = await axios.get(`${API}/admin/homepage-order`, { headers: getAuthHeader() });
        if (data.sections?.length) setSections(data.sections);
      } catch {}
    };
    fetch();
  }, []);

  const move = (idx, dir) => {
    const newIdx = idx + dir;
    if (newIdx < 0 || newIdx >= sections.length) return;
    const updated = [...sections];
    [updated[idx], updated[newIdx]] = [updated[newIdx], updated[idx]];
    setSections(updated);
  };

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await axios.put(`${API}/admin/homepage-order`, { sections }, { headers: getAuthHeader() });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch { alert('Save failed'); }
    finally { setSaving(false); }
  };

  return (
    <div className="p-6 lg:p-8" data-testid="homepage-order">
      <h1 className="text-xl font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Homepage Section Order</h1>
      <p className="text-sm text-[#6B7280] mb-6">Drag sections up or down to change the order they appear on the homepage.</p>

      <div className="max-w-lg space-y-2">
        {sections.map((key, idx) => (
          <div key={key} className="flex items-center gap-3 p-4 bg-[#121620] border border-[#232B3E] rounded-lg" data-testid={`section-${key}`}>
            <span className="text-xs text-[#6B7280] w-5 text-center">{idx + 1}</span>
            <span className="flex-1 text-sm font-medium text-[#F3F4F6]">{SECTION_LABELS[key] || key}</span>
            <div className="flex items-center gap-1">
              <button onClick={() => move(idx, -1)} disabled={idx === 0}
                className="p-1.5 text-[#6B7280] hover:text-[#D4AF37] disabled:opacity-20 rounded" data-testid={`move-up-${key}`}>
                <ArrowUp className="w-4 h-4" />
              </button>
              <button onClick={() => move(idx, 1)} disabled={idx === sections.length - 1}
                className="p-1.5 text-[#6B7280] hover:text-[#D4AF37] disabled:opacity-20 rounded" data-testid={`move-down-${key}`}>
                <ArrowDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-3 mt-6">
        <button onClick={handleSave} disabled={saving}
          className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50"
          data-testid="save-order-btn">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />} Save Order
        </button>
        {saved && <span className="text-sm text-[#10B981]">Saved!</span>}
      </div>
    </div>
  );
}
