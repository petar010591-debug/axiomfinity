import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-[#0A0D14] border-t border-[#232B3E] mt-16" data-testid="footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-sm bg-[#D4AF37] flex items-center justify-center">
                <span className="text-black font-bold text-sm" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>FN</span>
              </div>
              <span className="text-lg font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                Fin<span className="text-[#D4AF37]">News</span>
              </span>
            </Link>
            <p className="text-sm text-[#6B7280] leading-relaxed">
              Your trusted source for financial news, crypto analysis, and market insights.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-[0.2em] text-[#9CA3AF] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Quick Links</h4>
            <div className="space-y-2">
              <Link to="/latest" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Latest News</Link>
              <Link to="/category/crypto" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Crypto</Link>
              <Link to="/category/markets" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Markets</Link>
              <Link to="/category/defi" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">DeFi</Link>
              <Link to="/category/analysis" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Analysis</Link>
            </div>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-[0.2em] text-[#9CA3AF] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Resources</h4>
            <div className="space-y-2">
              <Link to="/education" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Education Hub</Link>
              <Link to="/about" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">About Us</Link>
              <Link to="/contact" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Contact</Link>
            </div>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-[0.2em] text-[#9CA3AF] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Legal</h4>
            <div className="space-y-2">
              <Link to="/page/privacy-policy" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Privacy Policy</Link>
              <Link to="/page/terms-and-conditions" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Terms & Conditions</Link>
              <Link to="/page/financial-disclaimer" className="block text-sm text-[#6B7280] hover:text-[#D4AF37] transition-colors">Financial Disclaimer</Link>
            </div>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-[#1A202E] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-[#6B7280]">&copy; {new Date().getFullYear()} FinNews. All rights reserved.</p>
          <p className="text-xs text-[#6B7280]">
            Content is for informational purposes only. Not financial advice.
          </p>
        </div>
      </div>
    </footer>
  );
}
