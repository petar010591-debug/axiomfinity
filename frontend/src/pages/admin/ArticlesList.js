import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import { Plus, PenLine, Trash2, Eye, Search } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function ArticlesList() {
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const params = { page, limit: 15 };
      if (statusFilter) params.status = statusFilter;
      const { data } = await axios.get(`${API}/admin/articles`, { headers: getAuthHeader(), params });
      setArticles(data.articles || []);
      setTotal(data.total || 0);
      setTotalPages(data.pages || 1);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchArticles(); }, [page, statusFilter]); // eslint-disable-line

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this article?')) return;
    try {
      await axios.delete(`${API}/admin/articles/${id}`, { headers: getAuthHeader() });
      fetchArticles();
    } catch {}
  };

  const statusBadge = (status) => {
    const styles = {
      published: 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30',
      draft: 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30',
      scheduled: 'bg-[#8B5CF6]/10 text-[#8B5CF6] border-[#8B5CF6]/30',
      archived: 'bg-[#6B7280]/10 text-[#6B7280] border-[#6B7280]/30',
    };
    return (
      <span className={`px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold border rounded ${styles[status] || styles.draft}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="p-6 lg:p-8" data-testid="articles-list-page">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Articles</h1>
          <p className="text-sm text-[#6B7280]">{total} total articles</p>
        </div>
        <Link
          to="/admin/articles/new"
          className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] transition-colors"
          data-testid="new-article-link"
        >
          <Plus className="w-4 h-4" /> New Article
        </Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-6" data-testid="article-status-filter">
        {['', 'published', 'draft', 'scheduled', 'archived'].map(s => (
          <button
            key={s}
            onClick={() => { setStatusFilter(s); setPage(1); }}
            className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
              statusFilter === s ? 'bg-[#D4AF37] text-black' : 'bg-[#121620] text-[#9CA3AF] border border-[#232B3E] hover:border-[#D4AF37]'
            }`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-[#121620] border border-[#232B3E] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full" data-testid="articles-table">
            <thead>
              <tr className="border-b border-[#232B3E] text-left">
                <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold">Title</th>
                <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold hidden md:table-cell">Category</th>
                <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold">Status</th>
                <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold hidden md:table-cell">Date</th>
                <th className="px-4 py-3 text-xs uppercase tracking-wider text-[#6B7280] font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [1,2,3,4,5].map(i => (
                  <tr key={i} className="border-b border-[#1A202E]">
                    <td colSpan={5} className="px-4 py-4"><div className="h-4 bg-[#1C2230] rounded animate-pulse" /></td>
                  </tr>
                ))
              ) : articles.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-10 text-center text-[#6B7280]">No articles found.</td></tr>
              ) : (
                articles.map(article => (
                  <tr key={article.id} className="border-b border-[#1A202E] hover:bg-[#1C2230]/50 transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm font-medium text-[#F3F4F6] line-clamp-1">{article.title}</p>
                        <p className="text-xs text-[#6B7280] mt-0.5 line-clamp-1">{article.slug}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-xs text-[#9CA3AF]">{article.category_name || '—'}</span>
                    </td>
                    <td className="px-4 py-3">{statusBadge(article.status)}</td>
                    <td className="px-4 py-3 hidden md:table-cell">
                      <span className="text-xs text-[#6B7280]">{formatDate(article.published_at || article.created_at)}</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {article.status === 'published' && (
                          <Link to={`/${article.category_slug || 'news'}/${article.slug}`} target="_blank" className="p-1.5 text-[#6B7280] hover:text-[#D4AF37] transition-colors" title="View">
                            <Eye className="w-3.5 h-3.5" />
                          </Link>
                        )}
                        <button onClick={() => navigate(`/admin/articles/edit/${article.id}`)} className="p-1.5 text-[#6B7280] hover:text-[#D4AF37] transition-colors" title="Edit" data-testid={`edit-article-${article.id}`}>
                          <PenLine className="w-3.5 h-3.5" />
                        </button>
                        <button onClick={() => handleDelete(article.id)} className="p-1.5 text-[#6B7280] hover:text-[#EF4444] transition-colors" title="Delete" data-testid={`delete-article-${article.id}`}>
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <span className="text-xs text-[#6B7280]">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1.5 text-xs border border-[#232B3E] text-[#9CA3AF] rounded-lg disabled:opacity-40 hover:border-[#D4AF37]">Prev</button>
            <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-3 py-1.5 text-xs border border-[#232B3E] text-[#9CA3AF] rounded-lg disabled:opacity-40 hover:border-[#D4AF37]">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
