import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Search, Menu, X, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const NAV_LINKS = [
  { label: 'Latest', href: '/latest' },
  {
    label: 'Categories', href: '#', children: [
      { label: 'Crypto', href: '/category/crypto' },
      { label: 'Markets', href: '/category/markets' },
      { label: 'DeFi', href: '/category/defi' },
      { label: 'Analysis', href: '/category/analysis' },
      { label: 'Educational', href: '/category/educational' },
      { label: 'Sponsored', href: '/category/sponsored' },
      { label: 'Press Releases', href: '/category/press-releases' },
    ]
  },
  { label: 'Education', href: '/education' },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
];

export default function Header() {
  const { user } = useAuth();
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => { setMobileOpen(false); setDropdownOpen(false); }, [location]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchQuery.trim())}`;
    }
  };

  return (
    <header
      data-testid="main-header"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-[#0A0D14]/90 backdrop-blur-xl border-b border-[#232B3E]' : 'bg-[#0A0D14]/70 backdrop-blur-xl'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group" data-testid="header-logo">
            <img src="/logo.png" alt="AxiomFinity" className="w-8 h-8 rounded-sm object-contain" />
            <span className="text-lg font-bold text-[#F3F4F6] tracking-tight hidden sm:block" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              Axiom<span className="text-[#D4AF37]">Finity</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden lg:flex items-center gap-1" data-testid="desktop-nav">
            {NAV_LINKS.map((link) =>
              link.children ? (
                <div key={link.label} className="relative" onMouseEnter={() => setDropdownOpen(true)} onMouseLeave={() => setDropdownOpen(false)}>
                  <button className="flex items-center gap-1 px-3 py-2 text-sm text-[#9CA3AF] hover:text-[#F3F4F6] transition-colors" data-testid="categories-dropdown-btn">
                    {link.label} <ChevronDown className="w-3.5 h-3.5" />
                  </button>
                  <AnimatePresence>
                    {dropdownOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 8 }}
                        transition={{ duration: 0.15 }}
                        className="absolute top-full left-0 mt-1 w-48 bg-[#121620] border border-[#232B3E] rounded-lg shadow-xl overflow-hidden"
                      >
                        {link.children.map((child) => (
                          <Link
                            key={child.href}
                            to={child.href}
                            className="block px-4 py-2.5 text-sm text-[#9CA3AF] hover:text-[#F3F4F6] hover:bg-[#1C2230] transition-colors"
                            data-testid={`category-link-${child.label.toLowerCase()}`}
                          >
                            {child.label}
                          </Link>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <Link
                  key={link.href}
                  to={link.href}
                  className={`px-3 py-2 text-sm transition-colors ${
                    location.pathname === link.href ? 'text-[#D4AF37]' : 'text-[#9CA3AF] hover:text-[#F3F4F6]'
                  }`}
                  data-testid={`nav-link-${link.label.toLowerCase()}`}
                >
                  {link.label}
                </Link>
              )
            )}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            {/* Search */}
            <AnimatePresence>
              {searchOpen ? (
                <motion.form
                  initial={{ width: 0, opacity: 0 }}
                  animate={{ width: 200, opacity: 1 }}
                  exit={{ width: 0, opacity: 0 }}
                  onSubmit={handleSearch}
                  className="overflow-hidden"
                >
                  <input
                    autoFocus
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onBlur={() => { if (!searchQuery) setSearchOpen(false); }}
                    placeholder="Search..."
                    className="w-full px-3 py-1.5 text-sm bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] placeholder-[#6B7280] focus:outline-none focus:border-[#D4AF37]"
                    data-testid="header-search-input"
                  />
                </motion.form>
              ) : (
                <button
                  onClick={() => setSearchOpen(true)}
                  className="p-2 text-[#9CA3AF] hover:text-[#D4AF37] transition-colors"
                  data-testid="header-search-btn"
                >
                  <Search className="w-4.5 h-4.5" />
                </button>
              )}
            </AnimatePresence>

            {user && (
              <Link
                to="/admin"
                className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 text-sm font-medium bg-[#D4AF37] text-black rounded-lg hover:bg-[#C39F2F] transition-colors"
                data-testid="admin-panel-btn"
              >
                Dashboard
              </Link>
            )}

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden p-2 text-[#9CA3AF] hover:text-[#F3F4F6] transition-colors"
              data-testid="mobile-menu-btn"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="lg:hidden bg-[#121620] border-t border-[#232B3E] overflow-hidden"
            data-testid="mobile-menu"
          >
            <div className="px-4 py-4 space-y-1">
              {NAV_LINKS.map((link) =>
                link.children ? (
                  <div key={link.label}>
                    <div className="px-3 py-2 text-xs uppercase tracking-[0.2em] text-[#6B7280]">{link.label}</div>
                    {link.children.map((child) => (
                      <Link key={child.href} to={child.href} className="block px-3 py-2 text-sm text-[#9CA3AF] hover:text-[#D4AF37]">
                        {child.label}
                      </Link>
                    ))}
                  </div>
                ) : (
                  <Link key={link.href} to={link.href} className="block px-3 py-2 text-sm text-[#9CA3AF] hover:text-[#D4AF37]">
                    {link.label}
                  </Link>
                )
              )}
              <form onSubmit={handleSearch} className="pt-2">
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search articles..."
                  className="w-full px-3 py-2 text-sm bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] placeholder-[#6B7280] focus:outline-none focus:border-[#D4AF37]"
                />
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
