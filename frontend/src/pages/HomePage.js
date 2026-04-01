import { useState, useEffect } from 'react';
import axios from 'axios';
import { ArticleCardHero, ArticleCardSecondary } from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function SectionHeader({ title, href, testId }) {
  return (
    <div className="flex items-center justify-between mb-6">
      <h2 className="text-xl sm:text-2xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
        {title}
      </h2>
      {href && (
        <Link
          to={href}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-[#232B3E] text-[#9CA3AF] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors"
          data-testid={testId}
        >
          View All <ArrowRight className="w-3 h-3" />
        </Link>
      )}
    </div>
  );
}

export default function HomePage() {
  const [sections, setSections] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data } = await axios.get(`${API}/articles/homepage-sections`);
        setSections(data);
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

  if (!sections) return null;

  const heroArticle = sections.latest?.[0];
  const secondaryArticles = sections.latest?.slice(1, 3) || [];
  const moreLatest = sections.latest?.slice(3) || [];

  return (
    <div data-testid="homepage">
      {/* Hero Section - Latest News Bento Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-4">
        <SectionHeader title="Latest News" href="/latest" testId="view-all-latest-btn" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <ArticleCardHero article={heroArticle} />
          </div>
          <div className="space-y-6">
            {secondaryArticles.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 * (i + 1) }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        </div>
        {moreLatest.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
            {moreLatest.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        )}
      </section>

      {/* Crypto Section */}
      {sections.crypto?.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-[#1A202E]">
          <SectionHeader title="Crypto" href="/category/crypto" testId="view-all-crypto-btn" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {sections.crypto.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Press Releases Section */}
      {sections.press_releases?.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-[#1A202E]">
          <SectionHeader title="Press Releases" href="/category/press-releases" testId="view-all-press-btn" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {sections.press_releases.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Sponsored Section */}
      {sections.sponsored?.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-[#1A202E]">
          <SectionHeader title="Sponsored" href="/category/sponsored" testId="view-all-sponsored-btn" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {sections.sponsored.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Others + Sidebar */}
      {sections.others?.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-[#1A202E]">
          <SectionHeader title="More Stories" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {sections.others.map((article, i) => (
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
      )}

      {/* Show sidebar even if no others */}
      {(!sections.others || sections.others.length === 0) && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 border-t border-[#1A202E]">
          <div className="max-w-sm">
            <Sidebar />
          </div>
        </section>
      )}
    </div>
  );
}
