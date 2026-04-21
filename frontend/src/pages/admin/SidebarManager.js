import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Save, Loader2, TrendingUp, Plus, X, Search } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function SidebarManager() {
  const [articles, setArticles] = useState([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const { data } = await axios.get(`${API}/sidebar-config`, { headers: getAuthHeader() });
        setArticles(data.articles || []);
      } catch {}
    };
    fetchConfig();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await axios.put(`${API}/admin/sidebar-config`, { articles }, { headers: getAuthHeader() });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      alert('Save failed');
    } finally { setSaving(false); }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const { data } = await axios.get(`${API}/articles/search`, { params: { q: searchQuery, limit: 5 } });
      setSearchResults(data.articles || []);
    } catch {} finally { setSearching(false); }
  };

  const addArticle = (article) => {
    if (articles.some(a => a.slug === article.slug)) return;
    setArticles([...articles, { slug: article.slug, title: article.title }]);
    setSearchResults([]);
    setSearchQuery('');
  };

  const removeArticle = (index) => {
    setArticles(articles.filter((_, i) => i !== index));
  };

  return (
    <div className="p-6 lg:p-8 max-w-3xl" data-testid="sidebar-manager">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-5 h-5 text-[#D4AF37]" />
          <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Trending Articles</h1>
        </div>
        <button onClick={handleSave} disabled={saving}
          className={`flex items-center gap-1.5 px-5 py-2.5 text-sm font-medium rounded-lg transition-colors ${saved ? 'bg-[#10B981] text-white' : 'bg-[#D4AF37] text-black hover:bg-[#C39F2F]'} disabled:opacity-50`}
          data-testid="sidebar-save-btn">
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {saved ? 'Saved!' : 'Save'}
        </button>
      </div>

      <p className="text-sm text-[#6B7280] mb-6">
        Select articles to display in the "Trending" sidebar section. Leave empty to auto-show latest articles.
      </p>

      {/* Search to add articles */}
      <div className="mb-6">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
            <input
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') handleSearch(); }}
              placeholder="Search articles to add..."
              className="w-full pl-10 pr-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]"
              data-testid="sidebar-search-input"
            />
          </div>
          <button onClick={handleSearch} disabled={searching}
            className="px-4 py-2.5 bg-[#232B3E] text-[#F3F4F6] text-sm rounded-lg hover:bg-[#2A3348] transition-colors">
            {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
          </button>
        </div>

        {/* Search results dropdown */}
        {searchResults.length > 0 && (
          <div className="mt-2 bg-[#121620] border border-[#232B3E] rounded-lg overflow-hidden">
            {searchResults.map(article => (
              <button
                key={article.id}
                onClick={() => addArticle(article)}
                className="w-full text-left px-4 py-3 text-sm text-[#F3F4F6] hover:bg-[#1C2230] border-b border-[#1A202E] last:border-0 transition-colors"
                data-testid={`sidebar-search-result-${article.slug}`}
              >
                <span className="font-medium">{article.title}</span>
                <span className="text-xs text-[#6B7280] ml-2">/{article.category_slug || 'news'}/{article.slug}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Current trending articles */}
      <div className="space-y-2">
        {articles.length === 0 ? (
          <div className="text-center py-8 text-[#6B7280] text-sm border border-dashed border-[#232B3E] rounded-lg">
            No curated trending articles. The sidebar will show the latest articles automatically.
          </div>
        ) : (
          articles.map((article, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-3 bg-[#121620] border border-[#232B3E] rounded-lg" data-testid={`sidebar-trending-${i}`}>
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-[#D4AF37] w-5">{i + 1}</span>
                <span className="text-sm text-[#F3F4F6]">{article.title}</span>
              </div>
              <button onClick={() => removeArticle(i)} className="p-1.5 text-[#6B7280] hover:text-[#EF4444] transition-colors">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
