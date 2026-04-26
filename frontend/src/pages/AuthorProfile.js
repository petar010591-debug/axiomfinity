import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { User, Twitter, Linkedin, Globe, ArrowLeft } from 'lucide-react';
import { ArticleCardSecondary } from '../components/ArticleCard';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AuthorProfile() {
  const { authorSlug } = useParams();
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAuthor = async () => {
      try {
        const { data } = await axios.get(`${API}/authors/by-slug/${authorSlug}`);
        setAuthor(data);
      } catch {} finally { setLoading(false); }
    };
    fetchAuthor();
  }, [authorSlug]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center gap-6 mb-8">
          <div className="w-20 h-20 rounded-full bg-[#121620] animate-pulse" />
          <div className="space-y-2">
            <div className="h-6 w-48 bg-[#121620] rounded animate-pulse" />
            <div className="h-4 w-72 bg-[#121620] rounded animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  if (!author) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 className="text-2xl font-bold text-[#F3F4F6] mb-4">Author Not Found</h1>
        <Link to="/" className="inline-flex items-center gap-2 text-[#D4AF37] hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="author-profile-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Author Header */}
        <div className="flex items-start gap-6 mb-10 pb-8 border-b border-[#232B3E]">
          <div className="w-20 h-20 rounded-full bg-[#D4AF37]/10 flex items-center justify-center flex-shrink-0 overflow-hidden">
            {author.avatar_url ? (
              <img src={author.avatar_url} alt={author.name} className="w-full h-full object-cover" />
            ) : (
              <User className="w-8 h-8 text-[#D4AF37]" />
            )}
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-[#F3F4F6] mb-1" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              {author.name}
            </h1>
            {author.job_title ? (
              <p className="text-sm text-[#D4AF37] font-semibold mb-1" data-testid="author-job-title">{author.job_title}</p>
            ) : (
              <p className="text-sm text-[#D4AF37] capitalize mb-1">{author.role?.replace('_', ' ')}</p>
            )}
            {author.expertise && (
              <p className="text-xs text-[#9CA3AF] mb-3" data-testid="author-expertise">
                <span className="text-[#F3F4F6] font-medium">Areas of expertise:</span> {author.expertise}
              </p>
            )}
            {author.bio_html ? (
              <div
                className="text-sm text-[#9CA3AF] leading-relaxed max-w-2xl article-content"
                data-testid="author-bio-html"
                dangerouslySetInnerHTML={{ __html: author.bio_html }}
              />
            ) : (
              author.bio && <p className="text-sm text-[#9CA3AF] leading-relaxed max-w-2xl">{author.bio}</p>
            )}
            <div className="flex items-center gap-3 mt-3">
              {author.social_twitter && (
                <a href={author.social_twitter.startsWith('http') ? author.social_twitter : `https://twitter.com/${author.social_twitter.replace('@','')}`} target="_blank" rel="noopener noreferrer" className="text-[#6B7280] hover:text-[#D4AF37] transition-colors" data-testid="author-twitter">
                  <Twitter className="w-4 h-4" />
                </a>
              )}
              {author.social_linkedin && (
                <a href={author.social_linkedin} target="_blank" rel="noopener noreferrer" className="text-[#6B7280] hover:text-[#D4AF37] transition-colors">
                  <Linkedin className="w-4 h-4" />
                </a>
              )}
              {author.website && (
                <a href={author.website} target="_blank" rel="noopener noreferrer" className="text-[#6B7280] hover:text-[#D4AF37] transition-colors">
                  <Globe className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Author Articles */}
        <h2 className="text-xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Articles by {author.name}
        </h2>
        {author.articles?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {author.articles.map((article, i) => (
              <motion.div key={article.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                <ArticleCardSecondary article={article} />
              </motion.div>
            ))}
          </div>
        ) : (
          <p className="text-[#6B7280]">No published articles yet.</p>
        )}
      </motion.div>
    </div>
  );
}
