import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import FaqAccordion from '../components/FaqAccordion';
import DOMPurify from 'dompurify';
import { Helmet } from 'react-helmet-async';
import { Clock, User, ArrowLeft, Share2, Tag, RefreshCw } from 'lucide-react';
import { ArticleCardSecondary } from '../components/ArticleCard';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
}

function formatSlug(slug) {
  return slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export default function ArticlePage() {
  const { slug } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    const fetchArticle = async () => {
      setLoading(true);
      try {
        const { data } = await axios.get(`${API}/articles/by-slug/${slug}`);
        setArticle(data);
      } catch (e) {
        setNotFound(true);
      } finally { setLoading(false); }
    };
    fetchArticle();
    window.scrollTo(0, 0);
  }, [slug]);

  // Load Twitter widget for embeds (handles both data-twitter-embed and class="twitter-tweet")
  useEffect(() => {
    if (!article?.content) return;
    if (!article.content.includes('twitter-tweet') && !article.content.includes('data-twitter-embed') && !article.content.includes('twitter.com')) return;

    // Convert old-format twitter embeds to standard format for widgets.js
    const contentEl = document.querySelector('[data-testid="article-content"]');
    if (contentEl) {
      contentEl.querySelectorAll('[data-twitter-embed]').forEach(el => {
        const tweetId = el.getAttribute('data-twitter-embed');
        if (tweetId && !el.classList.contains('twitter-tweet')) {
          const blockquote = document.createElement('blockquote');
          blockquote.className = 'twitter-tweet';
          blockquote.setAttribute('data-twitter-embed', tweetId);
          const link = document.createElement('a');
          link.href = `https://twitter.com/i/status/${tweetId}`;
          link.textContent = 'Loading tweet...';
          blockquote.appendChild(link);
          el.replaceWith(blockquote);
        }
      });
    }

    const timer = setTimeout(() => {
      if (window.twttr?.widgets) {
        window.twttr.widgets.load();
      } else {
        const existing = document.querySelector('script[src*="platform.twitter.com/widgets.js"]');
        if (!existing) {
          const script = document.createElement('script');
          script.src = 'https://platform.twitter.com/widgets.js';
          script.async = true;
          script.charset = 'utf-8';
          document.body.appendChild(script);
        }
      }
    }, 200);
    return () => clearTimeout(timer);
  }, [article]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-8 w-48 bg-[#121620] rounded animate-pulse mb-4" />
        <div className="h-12 bg-[#121620] rounded animate-pulse mb-4" />
        <div className="h-[400px] bg-[#121620] rounded-lg animate-pulse mb-8" />
        <div className="space-y-4">
          {[1,2,3,4].map(i => <div key={i} className="h-4 bg-[#121620] rounded animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (notFound) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 className="text-4xl font-bold text-[#F3F4F6] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Article Not Found</h1>
        <p className="text-[#9CA3AF] mb-6">The article you're looking for doesn't exist or has been removed.</p>
        <Link to="/" className="inline-flex items-center gap-2 px-4 py-2 bg-[#D4AF37] text-black rounded-lg font-medium hover:bg-[#C39F2F] transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
      </div>
    );
  }

  if (!article) return null;

  const shareUrl = window.location.href;
  const ogImage = article.og_image || article.featured_image || '';
  const ogTitle = article.og_title || article.title || '';
  const ogDescription = article.og_description || article.excerpt || '';

  return (
    <div data-testid="article-page">
      <Helmet>
        <title>{`${ogTitle} | AxiomFinity`}</title>
        <meta name="description" content={ogDescription} />
        <meta property="og:title" content={ogTitle} />
        <meta property="og:description" content={ogDescription} />
        <meta property="og:image" content={ogImage} />
        <meta property="og:url" content={shareUrl} />
        <meta property="og:type" content="article" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={ogTitle} />
        <meta name="twitter:description" content={ogDescription} />
        <meta name="twitter:image" content={ogImage} />
      </Helmet>
      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-[#6B7280] mb-6" data-testid="article-breadcrumb">
          <Link to="/" className="hover:text-[#D4AF37] transition-colors">Home</Link>
          <span>/</span>
          {article.category_name && (
            <>
              <Link to={`/category/${article.category_slug}`} className="hover:text-[#D4AF37] transition-colors">{article.category_name}</Link>
              <span>/</span>
            </>
          )}
          <span className="text-[#9CA3AF] truncate">{article.title}</span>
        </nav>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4 flex-wrap">
            {article.category_name && (
              <Link to={`/category/${article.category_slug}`} className="px-2.5 py-1 text-[11px] uppercase tracking-[0.15em] font-semibold bg-[#D4AF37] text-black rounded hover:bg-[#C39F2F] transition-colors">
                {article.category_name}
              </Link>
            )}
            {(article.categories || []).filter(s => s !== article.category_slug && !(s === 'sponsored' && article.is_sponsored)).map(slug => (
              <Link key={slug} to={`/category/${slug}`} className="px-2.5 py-1 text-[11px] uppercase tracking-[0.15em] font-semibold bg-[#D4AF37]/15 text-[#D4AF37] border border-[#D4AF37]/30 rounded hover:bg-[#D4AF37]/25 transition-colors">
                {formatSlug(slug)}
              </Link>
            ))}
            {article.is_sponsored && (
              <span className="px-2.5 py-1 text-[11px] uppercase tracking-[0.15em] font-semibold bg-[#D4AF37]/20 text-[#D4AF37] rounded">Sponsored</span>
            )}
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#F3F4F6] leading-tight mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }} data-testid="article-title">
            {article.title}
          </h1>

          {article.excerpt && (
            <p className="text-lg text-[#9CA3AF] mb-6 leading-relaxed">{article.excerpt}</p>
          )}

          <div className="flex items-center justify-between flex-wrap gap-4 pb-6 mb-8 border-b border-[#232B3E]">
            <div className="flex items-center gap-4 text-sm text-[#6B7280]">
              {article.author_id && (
                <Link to={`/author/${article.author_id}`} className="flex items-center gap-1.5 hover:text-[#D4AF37] transition-colors" data-testid="article-author-link">
                  <div className="w-7 h-7 rounded-full bg-[#D4AF37]/20 flex items-center justify-center overflow-hidden">
                    {article.author?.avatar_url ? (
                      <img src={article.author.avatar_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <User className="w-3.5 h-3.5 text-[#D4AF37]" />
                    )}
                  </div>
                  <span className="text-[#F3F4F6] font-medium">{article.author_name}</span>
                </Link>
              )}
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {formatDate(article.published_at)}</span>
              {article.updated_at && article.published_at && new Date(article.updated_at).getTime() - new Date(article.published_at).getTime() > 60000 && (
                <span className="flex items-center gap-1 text-[#D4AF37]">
                  <RefreshCw className="w-3 h-3" /> Updated: {formatDate(article.updated_at)}
                </span>
              )}
            </div>
            <button
              onClick={() => navigator.clipboard?.writeText(shareUrl)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-[#232B3E] text-[#9CA3AF] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors"
              data-testid="share-btn"
            >
              <Share2 className="w-3.5 h-3.5" /> Share
            </button>
          </div>
        </motion.div>

        {/* Featured Image */}
        {article.featured_image && (
          <div className="relative rounded-lg overflow-hidden mb-8">
            <img src={article.featured_image} alt={article.title} className="w-full h-auto max-h-[500px] object-cover" data-testid="article-featured-image" />
          </div>
        )}

        {/* Content */}
        <div className="article-content max-w-none" data-testid="article-content" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(article.content, { ADD_TAGS: ['iframe', 'blockquote'], ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'scrolling', 'data-twitter-embed', 'target', 'rel', 'href', 'class'] }) }} />

        {/* JSON-LD Structured Data */}
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "NewsArticle",
          "headline": article.title,
          "description": article.excerpt,
          "image": article.featured_image ? [article.featured_image] : [],
          "datePublished": article.published_at,
          "dateModified": article.updated_at || article.published_at,
          "author": { "@type": "Person", "name": article.author_name || "AxiomFinity" },
          "publisher": { "@type": "Organization", "name": "AxiomFinity", "logo": { "@type": "ImageObject", "url": "https://www.axiomfinity.com/logo192.png" } },
          "mainEntityOfPage": { "@type": "WebPage", "@id": `https://www.axiomfinity.com/${article.category_slug}/${article.slug}` }
        }) }} />

        {/* FAQs */}
        <FaqAccordion faqs={article.faqs} />

        {/* Tags */}
        {article.tags?.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap mt-8 pt-6 border-t border-[#232B3E]">
            <Tag className="w-4 h-4 text-[#6B7280]" />
            {article.tags.map(tag => (
              <Link key={tag} to={`/search?q=${tag}`} className="px-3 py-1 text-xs font-medium text-[#9CA3AF] bg-[#1C2230] rounded-full hover:text-[#D4AF37] hover:bg-[#D4AF37]/10 transition-colors">
                {tag}
              </Link>
            ))}
          </div>
        )}
      </article>

      {/* Related Articles */}
      {article.related?.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h2 className="text-2xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Related Articles</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {article.related.map(a => (
              <ArticleCardSecondary key={a.id} article={a} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
