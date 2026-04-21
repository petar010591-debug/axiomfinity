import { useState, useEffect } from 'react';
import { Link, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { getAuthHeader } from '../../contexts/AuthContext';
import {
  LayoutDashboard, FileText, FolderOpen, Tag, Home, LogOut, ChevronRight, Plus, Eye, PenLine, Archive, Menu, X, Users, UserCircle, Clock, FileEdit, Globe, ArrowUpDown, UsersRound, BookOpen
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SIDEBAR_ITEMS = [
  { label: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { label: 'Articles', href: '/admin/articles', icon: FileText },
  { label: 'Categories', href: '/admin/categories', icon: FolderOpen },
  { label: 'Pages', href: '/admin/pages', icon: FileEdit },
  { label: 'Education Hub', href: '/admin/education', icon: BookOpen },
  { label: 'Trending', href: '/admin/trending', icon: ArrowUpDown },
  { label: 'Homepage', href: '/admin/homepage', icon: Home },
  { label: 'Team Members', href: '/admin/team', icon: UsersRound },
  { label: 'Users & Roles', href: '/admin/users', icon: Users },
  { label: 'SEO / Nofollow', href: '/admin/seo', icon: Globe },
  { label: 'My Profile', href: '/admin/profile', icon: UserCircle },
];

export default function AdminDashboard() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [stats, setStats] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) navigate('/admin/login');
  }, [user, loading, navigate]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { data } = await axios.get(`${API}/admin/stats`, { headers: getAuthHeader() });
        setStats(data);
      } catch {}
    };
    if (user) fetchStats();
  }, [user, location.pathname]);

  useEffect(() => { setSidebarOpen(false); }, [location.pathname]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin" /></div>;
  if (!user) return null;

  const isActive = (href) => location.pathname === href;
  const isDashboardRoot = location.pathname === '/admin';

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0A0D14]" data-testid="admin-dashboard">
      {/* Mobile Header */}
      <div className="lg:hidden flex items-center justify-between px-4 py-3 bg-[#121620] border-b border-[#232B3E]">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-[#9CA3AF]">
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <span className="text-sm font-bold text-[#D4AF37]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>AxiomFinity CMS</span>
        <Link to="/" className="text-xs text-[#6B7280]">View Site</Link>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`fixed lg:sticky top-0 left-0 z-40 h-screen w-60 bg-[#121620] border-r border-[#232B3E] flex flex-col transition-transform lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`} data-testid="admin-sidebar">
          <div className="p-4 border-b border-[#232B3E]">
            <Link to="/admin" className="flex items-center gap-2">
              <img src="/logo.png" alt="AxiomFinity" className="w-7 h-7 rounded-sm object-contain" />
              <span className="text-sm font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>CMS Dashboard</span>
            </Link>
          </div>

          <nav className="flex-1 p-3 space-y-1">
            {SIDEBAR_ITEMS.map(item => (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center gap-2.5 px-3 py-2.5 text-sm rounded-lg transition-colors ${
                  isActive(item.href) ? 'bg-[#D4AF37]/10 text-[#D4AF37]' : 'text-[#9CA3AF] hover:text-[#F3F4F6] hover:bg-[#1C2230]'
                }`}
                data-testid={`admin-nav-${item.label.toLowerCase()}`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="p-3 border-t border-[#232B3E] space-y-1">
            <Link to="/" className="flex items-center gap-2.5 px-3 py-2.5 text-sm text-[#9CA3AF] hover:text-[#F3F4F6] hover:bg-[#1C2230] rounded-lg transition-colors">
              <Eye className="w-4 h-4" /> View Site
            </Link>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2.5 px-3 py-2.5 text-sm text-[#9CA3AF] hover:text-[#EF4444] hover:bg-[#EF4444]/10 rounded-lg transition-colors w-full"
              data-testid="admin-logout-btn"
            >
              <LogOut className="w-4 h-4" /> Logout
            </button>
          </div>
        </aside>

        {/* Mobile overlay */}
        {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-30 lg:hidden" onClick={() => setSidebarOpen(false)} />}

        {/* Main Content */}
        <main className="flex-1 min-h-screen">
          {isDashboardRoot ? (
            <div className="p-6 lg:p-8">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Dashboard</h1>
                  <p className="text-sm text-[#6B7280] mt-1">Welcome back, {user.name}</p>
                </div>
                <Link
                  to="/admin/articles/new"
                  className="flex items-center gap-1.5 px-4 py-2 bg-[#D4AF37] text-black text-sm font-medium rounded-lg hover:bg-[#C39F2F] transition-colors"
                  data-testid="new-article-btn"
                >
                  <Plus className="w-4 h-4" /> New Article
                </Link>
              </div>

              {/* Stats Grid */}
              {stats && (
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8" data-testid="admin-stats">
                  {[
                    { label: 'Total Articles', value: stats.total_articles, icon: FileText, color: '#D4AF37' },
                    { label: 'Published', value: stats.published, icon: Eye, color: '#10B981' },
                    { label: 'Drafts', value: stats.drafts, icon: PenLine, color: '#F59E0B' },
                    { label: 'Scheduled', value: stats.scheduled, icon: Clock, color: '#8B5CF6' },
                    { label: 'Categories', value: stats.categories, icon: FolderOpen, color: '#3B82F6' },
                    { label: 'Team', value: stats.users, icon: Users, color: '#EC4899' },
                  ].map(s => (
                    <div key={s.label} className="bg-[#121620] border border-[#232B3E] rounded-lg p-5">
                      <div className="flex items-center justify-between mb-3">
                        <s.icon className="w-5 h-5" style={{ color: s.color }} />
                      </div>
                      <p className="text-2xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{s.value}</p>
                      <p className="text-xs text-[#6B7280] mt-1">{s.label}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Quick Actions */}
              <h3 className="text-sm font-bold uppercase tracking-[0.15em] text-[#9CA3AF] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Quick Actions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { label: 'New Article', href: '/admin/articles/new', icon: Plus },
                  { label: 'Manage Articles', href: '/admin/articles', icon: FileText },
                  { label: 'Categories', href: '/admin/categories', icon: FolderOpen },
                  { label: 'Homepage', href: '/admin/homepage', icon: Home },
                ].map(action => (
                  <Link
                    key={action.href}
                    to={action.href}
                    className="flex items-center justify-between p-4 bg-[#121620] border border-[#232B3E] rounded-lg hover:border-[#D4AF37]/50 transition-colors group"
                  >
                    <span className="flex items-center gap-2 text-sm text-[#9CA3AF] group-hover:text-[#F3F4F6]">
                      <action.icon className="w-4 h-4" /> {action.label}
                    </span>
                    <ChevronRight className="w-4 h-4 text-[#6B7280] group-hover:text-[#D4AF37]" />
                  </Link>
                ))}
              </div>
            </div>
          ) : (
            <Outlet />
          )}
        </main>
      </div>
    </div>
  );
}
