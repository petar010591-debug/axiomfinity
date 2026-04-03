import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { LogIn, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function AdminLogin() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (user) {
    navigate('/admin');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/admin');
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (typeof detail === 'string') setError(detail);
      else if (Array.isArray(detail)) setError(detail.map(d => d.msg || JSON.stringify(d)).join(' '));
      else setError('Login failed. Please check your credentials.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4" data-testid="admin-login-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
            <img src="/logo.png" alt="AxiomFinity" className="w-12 h-12 rounded-lg object-contain" />
          </div>
          <h1 className="text-2xl font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Admin Login</h1>
          <p className="text-sm text-[#6B7280] mt-1">Sign in to access the CMS dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-[#121620] border border-[#232B3E] rounded-lg p-6 space-y-4" data-testid="login-form">
          {error && (
            <div className="flex items-center gap-2 p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg text-sm text-[#EF4444]" data-testid="login-error">
              <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Email</label>
            <input
              type="email" required value={email} onChange={e => setEmail(e.target.value)}
              className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] transition-colors"
              placeholder="admin@example.com"
              data-testid="login-email-input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Password</label>
            <input
              type="password" required value={password} onChange={e => setPassword(e.target.value)}
              className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] transition-colors"
              placeholder="Enter your password"
              data-testid="login-password-input"
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50 transition-colors"
            data-testid="login-submit-btn"
          >
            <LogIn className="w-4 h-4" /> {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
