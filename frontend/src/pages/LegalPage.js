import { useState, useEffect } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import FaqAccordion from '../components/FaqAccordion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function LegalPage() {
  const params = useParams();
  const location = useLocation();
  // Support both `/page/:slug` and bare paths like `/privacy-policy` or `/editorial-standards`
  const slug = params.slug || location.pathname.replace(/^\/+/, '').split('/')[0];
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPage = async () => {
      setLoading(true);
      try {
        const { data } = await axios.get(`${API}/pages/${slug}`);
        setPage(data);
      } catch {} finally { setLoading(false); }
    };
    fetchPage();
    window.scrollTo(0, 0);
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-10 w-64 bg-[#121620] rounded animate-pulse mb-6" />
        <div className="space-y-4">
          {[1,2,3,4,5].map(i => <div key={i} className="h-4 bg-[#121620] rounded animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (!page) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 className="text-2xl font-bold text-[#F3F4F6] mb-4">Page Not Found</h1>
        <Link to="/" className="inline-flex items-center gap-2 text-[#D4AF37] hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="legal-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <nav className="flex items-center gap-2 text-sm text-[#6B7280] mb-6">
          <Link to="/" className="hover:text-[#D4AF37] transition-colors">Home</Link>
          <span>/</span>
          <span className="text-[#9CA3AF]">{page.title}</span>
        </nav>

        <h1 className="text-3xl sm:text-4xl font-bold text-[#F3F4F6] mb-8" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {page.title}
        </h1>

        <div className="article-content" dangerouslySetInnerHTML={{ __html: page.content }} />

        {page.faqs?.length > 0 && (
          <div className="mt-12">
            <FaqAccordion faqs={page.faqs} />
          </div>
        )}
      </motion.div>
    </div>
  );
}
