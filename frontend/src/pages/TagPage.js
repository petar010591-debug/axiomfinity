import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Tag, ChevronLeft, ChevronRight } from 'lucide-react';
import { ArticleCardSecondary } from '../components/ArticleCard';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function TagPage() {
  const { slug } = useParams();
  const [articles, setArticles] = useState([]);
  const [tagName, setTagName] = useState('');
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchArticles = async (page = 1) => {
    setLoading(true);
    try {
      const { data } = await axios.get(`${API}/tags/${slug}/articles`, { params: { page, limit: 12 } });
      setArticles(data.articles || []);
      setTotal(data.total || 0);
      setCurrentPage(data.page || 1);
      setTotalPages(data.pages || 0);
      setTagName(data.tag_name || slug);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchArticles(1); window.scrollTo(0, 0); }, [slug]); // eslint-disable-line

  const goToPage = (page) => { fetchArticles(page); window.scrollTo(0, 0); };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="tag-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-2">
          <Tag className="w-5 h-5 text-[#D4AF37]" />
          <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37] font-semibold">Tag</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {tagName}
        </h1>
        <p className="text-sm text-[#6B7280] mb-8">
          {total} article{total !== 1 ? 's' : ''} tagged with "{tagName}"
          {totalPages > 1 && <span> · Page {currentPage} of {totalPages}</span>}
        </p>
      </motion.div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => <div key={i} className="h-72 bg-[#121620] rounded-lg animate-pulse" />)}
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-[#6B7280] text-lg">No articles found with this tag.</p>
          <Link to="/latest" className="inline-block mt-4 text-sm text-[#D4AF37] hover:underline">Browse Latest News</Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-10" data-testid="tag-pagination">
              <button onClick={() => goToPage(currentPage - 1)} disabled={currentPage <= 1}
                className="flex items-center gap-1 px-3 py-2 text-sm text-[#9CA3AF] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] disabled:opacity-30 transition-colors">
                <ChevronLeft className="w-4 h-4" /> Prev
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).slice(0, 7).map(p => (
                <button key={p} onClick={() => goToPage(p)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${p === currentPage ? 'bg-[#D4AF37] text-black border-[#D4AF37] font-semibold' : 'text-[#9CA3AF] border-[#232B3E] hover:border-[#D4AF37] hover:text-[#D4AF37]'}`}>
                  {p}
                </button>
              ))}
              <button onClick={() => goToPage(currentPage + 1)} disabled={currentPage >= totalPages}
                className="flex items-center gap-1 px-3 py-2 text-sm text-[#9CA3AF] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] disabled:opacity-30 transition-colors">
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
