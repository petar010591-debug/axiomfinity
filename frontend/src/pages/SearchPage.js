import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Search, ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
import { ArticleCardSecondary } from '../components/ArticleCard';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const initialPage = parseInt(searchParams.get('page') || '1', 10);
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(!!initialQuery);

  useEffect(() => {
    if (initialQuery) doSearch(initialQuery, initialPage);
  }, []); // eslint-disable-line

  const doSearch = async (q, page = 1) => {
    if (!q.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const { data } = await axios.get(`${API}/articles/search`, { params: { q: q.trim(), page, limit: 12 } });
      setResults(data.articles || []);
      setTotal(data.total || 0);
      setCurrentPage(data.page || 1);
      setTotalPages(data.pages || 0);
    } catch {} finally { setLoading(false); }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSearchParams({ q: query, page: '1' });
    doSearch(query, 1);
    window.scrollTo(0, 0);
  };

  const goToPage = (page) => {
    const q = searchParams.get('q') || query;
    setSearchParams({ q, page: String(page) });
    doSearch(q, page);
    window.scrollTo(0, 0);
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;
    const pages = [];
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    if (end - start + 1 < maxVisible) start = Math.max(1, end - maxVisible + 1);

    return (
      <div className="flex items-center justify-center gap-2 mt-10" data-testid="search-pagination">
        <button
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage <= 1}
          className="flex items-center gap-1 px-3 py-2 text-sm text-[#9CA3AF] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] disabled:opacity-30 disabled:hover:border-[#232B3E] disabled:hover:text-[#9CA3AF] transition-colors"
          data-testid="pagination-prev"
        >
          <ChevronLeft className="w-4 h-4" /> Prev
        </button>

        {start > 1 && (
          <>
            <button onClick={() => goToPage(1)} className="px-3 py-2 text-sm text-[#9CA3AF] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors">1</button>
            {start > 2 && <span className="text-[#6B7280] px-1">...</span>}
          </>
        )}

        {Array.from({ length: end - start + 1 }, (_, i) => start + i).map(p => (
          <button
            key={p}
            onClick={() => goToPage(p)}
            className={`px-3 py-2 text-sm rounded-lg border transition-colors ${p === currentPage ? 'bg-[#D4AF37] text-black border-[#D4AF37] font-semibold' : 'text-[#9CA3AF] border-[#232B3E] hover:border-[#D4AF37] hover:text-[#D4AF37]'}`}
            data-testid={`pagination-page-${p}`}
          >
            {p}
          </button>
        ))}

        {end < totalPages && (
          <>
            {end < totalPages - 1 && <span className="text-[#6B7280] px-1">...</span>}
            <button onClick={() => goToPage(totalPages)} className="px-3 py-2 text-sm text-[#9CA3AF] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors">{totalPages}</button>
          </>
        )}

        <button
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="flex items-center gap-1 px-3 py-2 text-sm text-[#9CA3AF] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] disabled:opacity-30 disabled:hover:border-[#232B3E] disabled:hover:text-[#9CA3AF] transition-colors"
          data-testid="pagination-next"
        >
          Next <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="search-page">
      <h1 className="text-3xl sm:text-4xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        Search
      </h1>

      <form onSubmit={handleSubmit} className="max-w-2xl mb-8" data-testid="search-form">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#6B7280]" />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search articles, topics, categories..."
            className="w-full pl-12 pr-4 py-3.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] placeholder-[#6B7280] focus:outline-none focus:border-[#D4AF37] transition-colors text-base"
            data-testid="search-input"
          />
        </div>
      </form>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => <div key={i} className="h-72 bg-[#121620] rounded-lg animate-pulse" />)}
        </div>
      ) : searched && results.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-[#6B7280] text-lg mb-2">No results found for "{searchParams.get('q')}"</p>
          <p className="text-sm text-[#6B7280]">Try different keywords or browse our categories.</p>
          <Link to="/latest" className="inline-flex items-center gap-2 mt-4 text-sm text-[#D4AF37] hover:underline">
            <ArrowLeft className="w-4 h-4" /> Browse Latest News
          </Link>
        </div>
      ) : (
        <>
          {searched && (
            <p className="text-sm text-[#6B7280] mb-6">
              {total} result{total !== 1 ? 's' : ''} for "{searchParams.get('q')}"
              {totalPages > 1 && <span> · Page {currentPage} of {totalPages}</span>}
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
          {renderPagination()}
        </>
      )}
    </div>
  );
}
