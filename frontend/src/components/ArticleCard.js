import { Link } from 'react-router-dom';
import { Clock, User } from 'lucide-react';
import { motion } from 'framer-motion';

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatSlug(slug) {
  return slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function CategoryBadges({ article, variant = 'default' }) {
  const primary = article.category_name;
  const primarySlug = article.category_slug;
  const extras = (article.categories || []).filter(s => s !== primarySlug && !(s === 'sponsored' && article.is_sponsored));

  const badgeClass = variant === 'overlay'
    ? 'px-2 py-0.5 text-[10px] uppercase tracking-[0.15em] font-semibold rounded'
    : 'px-2.5 py-1 text-[11px] uppercase tracking-[0.15em] font-semibold rounded';

  return (
    <div className="flex items-center gap-1.5 flex-wrap">
      {primary && (
        <span className={`${badgeClass} bg-[#D4AF37] text-black`}>{primary}</span>
      )}
      {extras.map(slug => (
        <span key={slug} className={`${badgeClass} bg-[#D4AF37]/15 text-[#D4AF37] border border-[#D4AF37]/30`}>{formatSlug(slug)}</span>
      ))}
    </div>
  );
}

export function ArticleCardHero({ article }) {
  if (!article) return null;
  return (
    <Link to={`/${article.category_slug || 'news'}/${article.slug}`} data-testid="hero-primary-card">
      <motion.div
        whileHover={{ scale: 1.01 }}
        transition={{ duration: 0.2 }}
        className="relative h-full min-h-[400px] md:min-h-[500px] rounded-lg overflow-hidden group cursor-pointer"
      >
        <img src={article.featured_image} alt={article.title} className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0A0D14] via-[#0A0D14]/60 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-8">
          {article.is_sponsored && <span className="inline-block px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] bg-[#D4AF37]/20 text-[#D4AF37] rounded mb-3">Sponsored</span>}
          <div className="mb-3">
            <CategoryBadges article={article} variant="overlay" />
          </div>
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-[#F3F4F6] leading-tight mb-3" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            {article.title}
          </h2>
          <p className="text-[#9CA3AF] text-sm md:text-base line-clamp-2 mb-3 max-w-2xl">{article.excerpt}</p>
          <div className="flex items-center gap-4 text-xs text-[#6B7280]">
            {article.author_name && <span className="flex items-center gap-1"><User className="w-3 h-3" /> {article.author_name}</span>}
            <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {formatDate(article.published_at)}</span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}

export function ArticleCardSecondary({ article }) {
  if (!article) return null;
  return (
    <Link to={`/${article.category_slug || 'news'}/${article.slug}`} data-testid={`article-card-${article.slug}`}>
      <motion.div
        whileHover={{ y: -4, borderColor: 'rgba(212,175,55,0.5)' }}
        transition={{ duration: 0.2 }}
        className="group h-full bg-[#121620] border border-[#232B3E] rounded-lg overflow-hidden cursor-pointer"
      >
        <div className="relative h-48 overflow-hidden">
          <img src={article.featured_image} alt={article.title} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#121620] to-transparent opacity-60" />
          {article.category_name && (
            <div className="absolute top-3 left-3">
              <CategoryBadges article={article} variant="overlay" />
            </div>
          )}
        </div>
        <div className="p-4">
          <h3 className="text-base font-bold text-[#F3F4F6] leading-snug mb-2 line-clamp-2 group-hover:text-[#D4AF37] transition-colors" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            {article.title}
          </h3>
          <p className="text-sm text-[#9CA3AF] line-clamp-2 mb-3">{article.excerpt}</p>
          <div className="flex items-center gap-3 text-xs text-[#6B7280]">
            {article.author_name && <span className="flex items-center gap-1"><User className="w-3 h-3" /> {article.author_name}</span>}
            <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {formatDate(article.published_at)}</span>
          </div>
        </div>
      </motion.div>
    </Link>
  );
}

export function ArticleCardCompact({ article }) {
  if (!article) return null;
  return (
    <Link to={`/${article.category_slug || 'news'}/${article.slug}`} data-testid={`article-compact-${article.slug}`}>
      <motion.div
        whileHover={{ x: 4 }}
        transition={{ duration: 0.15 }}
        className="flex gap-3 group cursor-pointer py-3 border-b border-[#1A202E] last:border-0"
      >
        <div className="w-16 h-16 rounded overflow-hidden flex-shrink-0">
          <img src={article.featured_image} alt={article.title || 'Article image'} className="w-full h-full object-cover" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-[#F3F4F6] line-clamp-2 group-hover:text-[#D4AF37] transition-colors leading-snug" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            {article.title}
          </h4>
          <span className="text-xs text-[#6B7280] mt-1 block">{formatDate(article.published_at)}</span>
        </div>
      </motion.div>
    </Link>
  );
}
