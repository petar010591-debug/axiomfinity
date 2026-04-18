import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArticleCardCompact } from './ArticleCard';
import { TrendingUp, BookOpen, Star } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Sidebar() {
  const [trending, setTrending] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesRes, catsRes] = await Promise.all([
          axios.get(`${API}/articles?limit=5`),
          axios.get(`${API}/categories`)
        ]);
        setTrending(articlesRes.data.articles || []);
        setCategories(catsRes.data || []);
      } catch {} finally { setLoading(false); }
    };
    fetchData();
  }, []);

  return (
    <aside className="space-y-6" data-testid="sidebar">
      {/* Trending Articles */}
      <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Trending</h3>
        </div>
        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => <div key={i} className="h-16 bg-[#1C2230] rounded animate-pulse" />)}
          </div>
        ) : (
          trending.slice(0, 4).map(article => (
            <ArticleCardCompact key={article.id} article={article} />
          ))
        )}
      </div>

      {/* Categories */}
      <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Categories</h3>
        </div>
        <div className="space-y-1">
          {categories.map(cat => (
            <a key={cat.id} href={`/category/${cat.slug}`} className="flex items-center justify-between px-3 py-2 text-sm text-[#9CA3AF] hover:text-[#D4AF37] hover:bg-[#1C2230] rounded transition-colors" data-testid={`sidebar-cat-${cat.slug}`}>
              <span>{cat.name}</span>
            </a>
          ))}
        </div>
      </div>

      {/* Education Hub - Beginner Guides */}
      <div className="bg-gradient-to-br from-[#D4AF37]/10 to-[#121620] border border-[#D4AF37]/20 rounded-lg p-5" data-testid="sidebar-education">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-[#D4AF37]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Learn Crypto</h3>
        </div>
        <p className="text-xs text-[#9CA3AF] leading-relaxed mb-3">
          New to crypto? Start with our beginner-friendly guides.
        </p>
        <div className="space-y-2 mb-3">
          <a href="/education/how-to-buy-bitcoin" className="block text-sm text-[#F3F4F6] hover:text-[#D4AF37] transition-colors" data-testid="sidebar-edu-link-1">
            How to Buy Bitcoin
          </a>
          <a href="/education/what-is-cryptocurrency" className="block text-sm text-[#F3F4F6] hover:text-[#D4AF37] transition-colors" data-testid="sidebar-edu-link-2">
            What Is Cryptocurrency?
          </a>
          <a href="/education/understanding-crypto-wallets" className="block text-sm text-[#F3F4F6] hover:text-[#D4AF37] transition-colors" data-testid="sidebar-edu-link-3">
            Understanding Crypto Wallets
          </a>
        </div>
        <a href="/education" className="inline-block text-xs font-semibold text-[#D4AF37] hover:underline">
          View all guides &rarr;
        </a>
      </div>

      {/* Editor's Pick */}
      <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-3">
          <Star className="w-4 h-4 text-[#D4AF37]" />
          <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Editor's Pick</h3>
        </div>
        <p className="text-xs text-[#9CA3AF] leading-relaxed">
          Stay informed with our curated selection of the most important stories in digital finance.
        </p>
      </div>
    </aside>
  );
}
