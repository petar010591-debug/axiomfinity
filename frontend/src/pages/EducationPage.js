import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { BookOpen, ArrowRight, Star, User } from 'lucide-react';
import { motion } from 'framer-motion';
import FaqAccordion from '../components/FaqAccordion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function EducationPage() {
  const [hub, setHub] = useState(null);
  const [pages, setPages] = useState([]);
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hubRes, pagesRes, authorRes] = await Promise.all([
          axios.get(`${API}/education-hub`).catch(() => ({ data: null })),
          axios.get(`${API}/education-hub/pages`).catch(() => ({ data: [] })),
          axios.get(`${API}/authors/default`).catch(() => null),
        ]);
        setHub(hubRes.data);
        setPages(pagesRes.data || []);
        if (authorRes?.data) setAuthor(authorRes.data);
      } catch {} finally { setLoading(false); }
    };
    fetchData();
  }, []);

  const getPageBySlug = (slug) => pages.find(p => p.slug === slug);

  const featuredPage = hub?.featured_slug ? getPageBySlug(hub.featured_slug) : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="education-page">
      {/* Hero */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <BookOpen className="w-5 h-5 text-[#D4AF37]" />
          <span className="text-xs uppercase tracking-[0.2em] text-[#D4AF37] font-semibold">Education Hub</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#F3F4F6] mb-4 max-w-4xl" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {hub?.hero_title || 'Crypto for Beginners: Learn Digital Finance with Clear, Practical Guides'}
        </h1>
        <p className="text-lg text-[#9CA3AF] max-w-2xl">
          {hub?.hero_subtitle || 'Learn the basics of cryptocurrency, blockchain, wallets, Bitcoin, Ethereum, and safe investing through beginner-friendly education guides.'}
        </p>

        {/* Author + Trust Block */}
        {author && (
          <Link to={`/author/${author.slug}`} className="inline-flex items-center gap-3 mt-5 hover:opacity-90 transition-opacity" data-testid="edu-hub-author">
            <div className="w-9 h-9 rounded-full bg-[#D4AF37]/20 flex items-center justify-center overflow-hidden flex-shrink-0">
              {author.avatar_url ? (
                <img src={author.avatar_url} alt={author.name} className="w-full h-full object-cover" />
              ) : (
                <User className="w-4 h-4 text-[#D4AF37]" />
              )}
            </div>
            <div>
              <p className="text-sm font-semibold text-[#F3F4F6]">{author.name}</p>
              <p className="text-xs text-[#9CA3AF]">Editor</p>
            </div>
          </Link>
        )}
      </motion.div>

      {/* SEO Intro Block */}
      {hub?.intro_content && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="article-content max-w-3xl mb-12 text-[#9CA3AF]"
          dangerouslySetInnerHTML={{ __html: hub.intro_content }}
          data-testid="edu-intro"
        />
      )}

      {/* Featured Guide */}
      {featuredPage && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-14">
          <Link to={`/education/${featuredPage.slug}`} data-testid="featured-guide">
            <div className="group relative bg-gradient-to-r from-[#D4AF37]/10 to-[#121620] border border-[#D4AF37]/30 rounded-xl p-6 sm:p-8 hover:border-[#D4AF37]/60 transition-all">
              <div className="flex items-center gap-2 mb-3">
                <Star className="w-4 h-4 text-[#D4AF37]" />
                <span className="text-xs uppercase tracking-[0.15em] text-[#D4AF37] font-semibold">Featured Guide</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#F3F4F6] mb-3 group-hover:text-[#D4AF37] transition-colors" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                {featuredPage.title}
              </h2>
              <p className="text-[#9CA3AF] mb-4 max-w-2xl">
                {featuredPage.meta_description || featuredPage.content?.replace(/<[^>]+>/g, '').slice(0, 200)}
              </p>
              <span className="inline-flex items-center gap-1.5 text-sm text-[#D4AF37] font-medium group-hover:gap-2.5 transition-all">
                Read the full guide <ArrowRight className="w-4 h-4" />
              </span>
            </div>
          </Link>
        </motion.div>
      )}

      {/* Topic Sections */}
      {hub?.sections?.map((section, si) => (
        <motion.section
          key={si}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 + si * 0.08 }}
          className="mb-12"
          data-testid={`edu-section-${si}`}
        >
          <h2 className="text-2xl font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            {section.title}
          </h2>
          <p className="text-sm text-[#9CA3AF] mb-6 max-w-2xl">{section.description}</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {section.slugs?.map((slug, ci) => {
              const pg = getPageBySlug(slug);
              if (!pg) return null;
              return (
                <Link to={`/education/${pg.slug}`} key={pg.slug} data-testid={`edu-card-${pg.slug}`}>
                  <div className="group bg-[#121620] border border-[#232B3E] rounded-lg p-5 hover:border-[#D4AF37]/50 transition-all duration-200 h-full flex flex-col">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-9 h-9 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center">
                        <BookOpen className="w-4 h-4 text-[#D4AF37]" />
                      </div>
                      <ArrowRight className="w-4 h-4 text-[#6B7280] group-hover:text-[#D4AF37] group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="text-base font-bold text-[#F3F4F6] mb-2 group-hover:text-[#D4AF37] transition-colors" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                      {pg.title}
                    </h3>
                    <p className="text-sm text-[#9CA3AF] line-clamp-3 flex-1">
                      {pg.meta_description || pg.content?.replace(/<[^>]+>/g, '').slice(0, 150)}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </motion.section>
      ))}

      {/* Fallback if no hub config: show all educational pages */}
      {(!hub?.sections || hub.sections.length === 0) && !loading && pages.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pages.map((pg, i) => (
            <motion.div key={pg.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
              <Link to={`/education/${pg.slug}`} data-testid={`edu-card-${pg.slug}`}>
                <div className="group bg-[#121620] border border-[#232B3E] rounded-lg p-5 hover:border-[#D4AF37]/50 transition-all h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-9 h-9 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center">
                      <BookOpen className="w-4 h-4 text-[#D4AF37]" />
                    </div>
                    <ArrowRight className="w-4 h-4 text-[#6B7280] group-hover:text-[#D4AF37] transition-all" />
                  </div>
                  <h3 className="text-base font-bold text-[#F3F4F6] mb-2 group-hover:text-[#D4AF37] transition-colors" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                    {pg.title}
                  </h3>
                  <p className="text-sm text-[#9CA3AF] line-clamp-3">{pg.content?.replace(/<[^>]+>/g, '').slice(0, 150)}</p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}

      {/* Hub FAQs */}
      {hub?.faqs?.length > 0 && (
        <div className="max-w-3xl mt-8">
          <FaqAccordion faqs={hub.faqs} />
        </div>
      )}
    </div>
  );
}
