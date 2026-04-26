import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader, useAuth } from '../../contexts/AuthContext';
import { Save, User, Upload } from 'lucide-react';
import TipTapEditor from '../../components/TipTapEditor';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AdminProfile() {
  const { user } = useAuth();
  const [form, setForm] = useState({
    name: '',
    bio: '',
    bio_html: '',
    avatar_url: '',
    social_twitter: '',
    social_linkedin: '',
    website: '',
    job_title: '',
    expertise: '',
  });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await axios.get(`${API}/auth/me`, { headers: getAuthHeader() });
        setForm({
          name: data.name || '',
          bio: data.bio || '',
          bio_html: data.bio_html || '',
          avatar_url: data.avatar_url || '',
          social_twitter: data.social_twitter || '',
          social_linkedin: data.social_linkedin || '',
          website: data.website || '',
          job_title: data.job_title || '',
          expertise: data.expertise || '',
        });
      } catch {}
    };
    fetchProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    try {
      await axios.put(`${API}/admin/profile`, form, { headers: getAuthHeader() });
      setSuccess('Profile updated');
      setTimeout(() => setSuccess(''), 3000);
    } catch {} finally { setSaving(false); }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await axios.post(`${API}/upload`, formData, { headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' } });
      if (data.url) setForm(f => ({ ...f, avatar_url: data.url }));
    } catch {} finally { setUploading(false); }
  };

  return (
    <div className="p-6 lg:p-8 max-w-3xl" data-testid="admin-profile-page">
      <h1 className="text-xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>My Profile</h1>

      {success && <div className="mb-4 p-3 bg-[#10B981]/10 border border-[#10B981]/30 rounded-lg text-sm text-[#10B981]">{success}</div>}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Avatar */}
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-[#D4AF37]/10 flex items-center justify-center overflow-hidden flex-shrink-0">
            {form.avatar_url ? (
              <img src={form.avatar_url} alt="Avatar" className="w-full h-full object-cover" />
            ) : (
              <User className="w-6 h-6 text-[#D4AF37]" />
            )}
          </div>
          <div>
            <label className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-[#1C2230] text-[#9CA3AF] border border-[#232B3E] rounded-lg cursor-pointer hover:text-[#D4AF37] hover:border-[#D4AF37] transition-colors">
              <Upload className="w-3.5 h-3.5" /> {uploading ? 'Uploading...' : 'Upload Avatar'}
              <input type="file" accept="image/*" onChange={handleAvatarUpload} className="hidden" />
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Display Name</label>
            <input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="profile-name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Job Title</label>
            <input type="text" value={form.job_title} onChange={e => setForm({ ...form, job_title: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="e.g. Editor-in-Chief" data-testid="profile-job-title" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Areas of Expertise</label>
          <input type="text" value={form.expertise} onChange={e => setForm({ ...form, expertise: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="e.g. Cryptocurrency, DeFi, On-chain Analysis, Bitcoin" data-testid="profile-expertise" />
          <p className="text-xs text-[#6B7280] mt-1">Comma-separated. Used in author JSON-LD as <code className="text-[#D4AF37]">knowsAbout</code> for E-E-A-T signals.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Short Bio (Plain Text)</label>
          <textarea rows={2} value={form.bio} onChange={e => setForm({ ...form, bio: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] resize-none" placeholder="One-line summary used in meta descriptions and Person JSON-LD..." data-testid="profile-bio" />
          <p className="text-xs text-[#6B7280] mt-1">Used for meta descriptions and JSON-LD <code className="text-[#D4AF37]">description</code>. Keep it under 160 characters.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Long Bio (Rich Text)</label>
          <TipTapEditor
            content={form.bio_html}
            onChange={(html) => setForm(prev => ({ ...prev, bio_html: html }))}
          />
          <p className="text-xs text-[#6B7280] mt-1">Displayed on your public author page. Add credentials, experience, and links to build E-E-A-T trust signals.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Twitter/X Handle</label>
            <input type="text" value={form.social_twitter} onChange={e => setForm({ ...form, social_twitter: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="@username" data-testid="profile-twitter" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">LinkedIn URL</label>
            <input type="text" value={form.social_linkedin} onChange={e => setForm({ ...form, social_linkedin: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="https://linkedin.com/in/..." data-testid="profile-linkedin" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Website</label>
          <input type="text" value={form.website} onChange={e => setForm({ ...form, website: e.target.value })} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="https://..." data-testid="profile-website" />
        </div>

        <button type="submit" disabled={saving} className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50 transition-colors" data-testid="profile-save-btn">
          <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
}
