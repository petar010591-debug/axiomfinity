import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, BookOpen, User } from 'lucide-react';
import { motion } from 'framer-motion';
import FaqAccordion from '../components/FaqAccordion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function EducationArticle() {
  const { slug } = useParams();
  const [page, setPage] = useState(null);
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [pageRes, authorRes] = await Promise.all([
          axios.get(`${API}/pages/${slug}`),
          axios.get(`${API}/authors/default`).catch(() => null),
        ]);
        setPage(pageRes.data);
        if (authorRes?.data) setAuthor(authorRes.data);
      } catch {} finally { setLoading(false); }
    };
    fetchData();
    window.scrollTo(0, 0);
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-4 w-32 bg-[#121620] rounded animate-pulse mb-6" />
        <div className="h-10 w-3/4 bg-[#121620] rounded animate-pulse mb-6" />
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
        <Link to="/education" className="inline-flex items-center gap-2 text-[#D4AF37] hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Education
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="education-article">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-[#6B7280] mb-6" data-testid="breadcrumb">
          <Link to="/" className="hover:text-[#D4AF37] transition-colors">Home</Link>
          <span>/</span>
          <Link to="/education" className="hover:text-[#D4AF37] transition-colors">Education</Link>
          <span>/</span>
          <span className="text-[#9CA3AF]">{page.title}</span>
        </nav>

        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-[#D4AF37]" />
          <span className="text-xs uppercase tracking-[0.15em] text-[#D4AF37] font-semibold">Education Guide</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-bold text-[#F3F4F6] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {page.title}
        </h1>

        {/* Author + Trust Block */}
        <Link to={author ? `/author/${author.slug}` : '#'} className="flex items-center gap-3 pb-4 mb-6 border-b border-[#232B3E] hover:opacity-90 transition-opacity" data-testid="author-trust-block">
          <div className="w-10 h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center overflow-hidden flex-shrink-0">
            {author?.avatar_url ? (
              <img src={author.avatar_url} alt={author.name || 'Author'} className="w-full h-full object-cover" />
            ) : (
              <User className="w-5 h-5 text-[#D4AF37]" />
            )}
          </div>
          <div>
            <p className="text-sm font-semibold text-[#F3F4F6]">Petar Jovanovic</p>
            <p className="text-xs text-[#9CA3AF]">
              Editor
              {page.updated_at && <> · Updated {new Date(page.updated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</>}
            </p>
          </div>
        </Link>

        {/* Featured Image */}
        {page.featured_image && (
          <div className="mb-8 rounded-lg overflow-hidden" data-testid="edu-featured-image">
            <img src={page.featured_image} alt={page.title} className="w-full h-auto object-cover rounded-lg" />
          </div>
        )}

        <div className="article-content" dangerouslySetInnerHTML={{ __html: page.content }} />

        {/* FAQs */}
        {page.faqs?.length > 0 && (
          <FaqAccordion faqs={page.faqs} />
        )}

        {/* Back to Education */}
        <div className="mt-12 pt-8 border-t border-[#232B3E]">
          <Link to="/education" className="inline-flex items-center gap-2 text-[#D4AF37] hover:underline text-sm" data-testid="back-to-education">
            <ArrowLeft className="w-4 h-4" /> Back to Education Hub
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
