import { useState, useEffect } from 'react';
import { useSearchParams, useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { ArticleCardSecondary } from '../components/ArticleCard';
import { motion } from 'framer-motion';
import FaqAccordion from '../components/FaqAccordion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function LatestNewsPage() {
  const [searchParams] = useSearchParams();
  const { slug: categoryFromUrl } = useParams();
  const navigate = useNavigate();
  const location = window.location.pathname;

  // Determine active category from URL: /category/:slug, /:slug, or query param
  const getCategoryFromPath = () => {
    if (categoryFromUrl) return categoryFromUrl;
    const param = searchParams.get('category');
    if (param) return param;
    // Check if path is a single-segment category slug like /crypto, /markets
    const pathSlug = location.replace(/^\//, '').split('/')[0];
    if (pathSlug && pathSlug !== 'latest') return pathSlug;
    return '';
  };

  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [latestConfig, setLatestConfig] = useState(null);
  const [activeCategory, setActiveCategory] = useState(getCategoryFromPath());
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setActiveCategory(getCategoryFromPath());
  }, [categoryFromUrl, location]); // eslint-disable-line

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const [catsRes, latestRes] = await Promise.all([
          axios.get(`${API}/categories`),
          axios.get(`${API}/latest-page-config`).catch(() => ({ data: null })),
        ]);
        setCategories(catsRes.data || []);
        setLatestConfig(latestRes.data);
      } catch {}
    };
    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchArticles = async () => {
      setLoading(true);
      try {
        const params = { page, limit: 12 };
        if (activeCategory) params.category = activeCategory;
        const { data } = await axios.get(`${API}/articles`, { params });
        setArticles(data.articles || []);
        setTotalPages(data.pages || 1);
      } catch {} finally { setLoading(false); }
    };
    fetchArticles();
  }, [page, activeCategory]);

  const switchCategory = (slug) => {
    setActiveCategory(slug);
    setPage(1);
    if (slug) {
      navigate(`/${slug}`);
    } else {
      navigate('/latest');
    }
  };

  const activeCat = categories.find(c => c.slug === activeCategory);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="latest-news-page">
      <h1 className="text-3xl sm:text-4xl font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        {activeCategory
          ? (activeCat?.display_title || activeCat?.name || 'Latest News')
          : (latestConfig?.display_title || 'Latest News')}
      </h1>
      {activeCategory && activeCat?.description ? (
        <div className="text-[#9CA3AF] mb-8 max-w-3xl text-sm leading-relaxed article-content"
          dangerouslySetInnerHTML={{ __html: activeCat.description }}
        />
      ) : !activeCategory && latestConfig?.description ? (
        <div className="text-[#9CA3AF] mb-8 max-w-3xl text-sm leading-relaxed article-content"
          dangerouslySetInnerHTML={{ __html: latestConfig.description }}
        />
      ) : (
        <p className="text-[#9CA3AF] mb-8">Stay updated with the latest in financial news and crypto markets.</p>
      )}

      {/* Category Filter */}
      <div className="flex items-center gap-2 flex-wrap mb-8" data-testid="category-filter">
        <button
          onClick={() => switchCategory('')}
          className={`px-4 py-2 text-sm rounded-lg font-medium transition-colors ${
            !activeCategory ? 'bg-[#D4AF37] text-black' : 'bg-[#121620] text-[#9CA3AF] border border-[#232B3E] hover:border-[#D4AF37] hover:text-[#D4AF37]'
          }`}
          data-testid="filter-all"
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => switchCategory(cat.slug)}
            className={`px-4 py-2 text-sm rounded-lg font-medium transition-colors ${
              activeCategory === cat.slug ? 'bg-[#D4AF37] text-black' : 'bg-[#121620] text-[#9CA3AF] border border-[#232B3E] hover:border-[#D4AF37] hover:text-[#D4AF37]'
            }`}
            data-testid={`filter-${cat.slug}`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="h-72 bg-[#121620] border border-[#232B3E] rounded-lg animate-pulse" />
          ))}
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-[#6B7280] text-lg">No articles found.</p>
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

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-10" data-testid="pagination">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm border border-[#232B3E] text-[#9CA3AF] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <span className="text-sm text-[#6B7280]">Page {page} of {totalPages}</span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 text-sm border border-[#232B3E] text-[#9CA3AF] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* FAQs */}
      {activeCategory && activeCat?.faqs?.length > 0 && (
        <div className="max-w-3xl mt-12">
          <FaqAccordion faqs={activeCat.faqs} />
        </div>
      )}
      {!activeCategory && latestConfig?.faqs?.length > 0 && (
        <div className="max-w-3xl mt-12">
          <FaqAccordion faqs={latestConfig.faqs} />
        </div>
      )}
    </div>
  );
}
