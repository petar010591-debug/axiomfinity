import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { BookOpen, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function EducationPage() {
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPages = async () => {
      try {
        const { data } = await axios.get(`${API}/pages?page_type=educational`);
        setPages(data || []);
      } catch {} finally { setLoading(false); }
    };
    fetchPages();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="education-page">
      {/* Hero */}
      <div className="relative rounded-xl overflow-hidden mb-12">
        <img
          src="https://static.prod-images.emergentagent.com/jobs/0356c6e3-d9fe-4e34-b671-3b8a5d7d214f/images/a93bc06ad761fa1cee1bcc03f9f82eb5ffb38dddbd06acdd028acf9e70b95a52.png"
          alt="Education"
          className="w-full h-64 sm:h-80 object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0A0D14] via-[#0A0D14]/60 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-8">
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-5 h-5 text-[#D4AF37]" />
            <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37] font-semibold">Education Hub</span>
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Learn About Digital Finance
          </h1>
          <p className="text-[#9CA3AF] mt-3 max-w-2xl">
            Build your knowledge with our comprehensive guides on blockchain, cryptocurrencies, DeFi, and traditional markets.
          </p>
        </div>
      </div>

      {/* Educational Articles */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1,2,3,4].map(i => <div key={i} className="h-48 bg-[#121620] rounded-lg animate-pulse" />)}
        </div>
      ) : pages.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-[#6B7280] text-lg">Educational content coming soon.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {pages.map((page, i) => (
            <motion.div key={page.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
              <Link to={`/page/${page.slug}`} data-testid={`edu-card-${page.slug}`}>
                <div className="group bg-[#121620] border border-[#232B3E] rounded-lg p-6 hover:border-[#D4AF37]/50 transition-all duration-200 h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-10 h-10 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center">
                      <BookOpen className="w-5 h-5 text-[#D4AF37]" />
                    </div>
                    <ArrowRight className="w-4 h-4 text-[#6B7280] group-hover:text-[#D4AF37] group-hover:translate-x-1 transition-all" />
                  </div>
                  <h3 className="text-lg font-bold text-[#F3F4F6] mb-2 group-hover:text-[#D4AF37] transition-colors" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                    {page.title}
                  </h3>
                  <p className="text-sm text-[#9CA3AF] line-clamp-3">{page.content?.replace(/<[^>]+>/g, '').slice(0, 150)}...</p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
