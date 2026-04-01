import { useState, useEffect } from 'react';
import axios from 'axios';
import { getAuthHeader, useAuth } from '../../contexts/AuthContext';
import { Save, User, Upload } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AdminProfile() {
  const { user } = useAuth();
  const [form, setForm] = useState({ name: '', bio: '', avatar_url: '', social_twitter: '', social_linkedin: '', website: '' });
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
          avatar_url: data.avatar_url || '',
          social_twitter: data.social_twitter || '',
          social_linkedin: data.social_linkedin || '',
          website: data.website || '',
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
    <div className="p-6 lg:p-8 max-w-2xl" data-testid="admin-profile-page">
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

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Display Name</label>
          <input type="text" value={form.name} onChange={e => setForm({...form, name: e.target.value})} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" data-testid="profile-name" />
        </div>

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Bio</label>
          <textarea rows={3} value={form.bio} onChange={e => setForm({...form, bio: e.target.value})} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] resize-none" placeholder="Tell readers about yourself..." data-testid="profile-bio" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Twitter/X Handle</label>
            <input type="text" value={form.social_twitter} onChange={e => setForm({...form, social_twitter: e.target.value})} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="@username" data-testid="profile-twitter" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">LinkedIn URL</label>
            <input type="text" value={form.social_linkedin} onChange={e => setForm({...form, social_linkedin: e.target.value})} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="https://linkedin.com/in/..." data-testid="profile-linkedin" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Website</label>
          <input type="text" value={form.website} onChange={e => setForm({...form, website: e.target.value})} className="w-full px-3 py-2.5 bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37]" placeholder="https://..." data-testid="profile-website" />
        </div>

        <button type="submit" disabled={saving} className="flex items-center gap-1.5 px-5 py-2.5 bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50 transition-colors" data-testid="profile-save-btn">
          <Save className="w-4 h-4" /> {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
}
