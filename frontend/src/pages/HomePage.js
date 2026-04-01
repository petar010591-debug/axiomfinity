import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArticleCardHero, ArticleCardSecondary } from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function HomePage() {
  const [featured, setFeatured] = useState({ hero_primary: null, hero_secondary: [] });
  const [latest, setLatest] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [featuredRes, latestRes] = await Promise.all([
          axios.get(`${API}/articles/featured`),
          axios.get(`${API}/articles?limit=6&page=1`)
        ]);
        setFeatured(featuredRes.data);
        setLatest(latestRes.data.articles || []);
      } catch (e) { console.error(e); } finally { setLoading(false); }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="md:col-span-2 h-[500px] bg-[#121620] rounded-lg animate-pulse" />
          <div className="space-y-6">
            <div className="h-[240px] bg-[#121620] rounded-lg animate-pulse" />
            <div className="h-[240px] bg-[#121620] rounded-lg animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div data-testid="homepage">
      {/* Hero Section - Bento Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <ArticleCardHero article={featured.hero_primary} />
          </div>
          <div className="space-y-6">
            {featured.hero_secondary.slice(0, 2).map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 * (i + 1) }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Latest News + Sidebar */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Latest News
          </h2>
          <Link
            to="/latest"
            className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border border-[#232B3E] text-[#9CA3AF] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors"
            data-testid="view-all-articles-btn"
          >
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {latest.map((article, i) => (
                <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                  <ArticleCardSecondary article={article} />
                </motion.div>
              ))}
            </div>
          </div>
          <div className="lg:col-span-1">
            <Sidebar />
          </div>
        </div>
      </section>
    </div>
  );
}
