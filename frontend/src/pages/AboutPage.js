import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Mail, MapPin, Send } from 'lucide-react';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AboutPage() {
  const [aboutContent, setAboutContent] = useState(null);

  useEffect(() => {
    const fetchAbout = async () => {
      try {
        const { data } = await axios.get(`${API}/pages/about`);
        setAboutContent(data);
      } catch {}
    };
    fetchAbout();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="about-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#F3F4F6] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          About AxiomFinity
        </h1>
        <p className="text-lg text-[#9CA3AF] mb-12 max-w-2xl">
          Your trusted source for financial news, analysis, and educational content in the digital asset space.
        </p>
      </motion.div>

      {aboutContent && (
        <div className="article-content max-w-3xl mb-12" dangerouslySetInnerHTML={{ __html: aboutContent.content }} />
      )}

      {/* Values Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
        {[
          { title: 'Accuracy First', desc: 'We verify information through multiple sources before publishing. Trust and credibility are our foundation.' },
          { title: 'Independent Voice', desc: 'Our editorial content is independent of sponsors and advertisers. Sponsored content is always clearly labeled.' },
          { title: 'Accessible Finance', desc: 'We make complex financial topics understandable for everyone, from beginners to experienced investors.' },
        ].map((v, i) => (
          <motion.div
            key={v.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
            className="bg-[#121620] border border-[#232B3E] rounded-lg p-6"
          >
            <div className="w-8 h-8 rounded bg-[#D4AF37]/10 flex items-center justify-center mb-4">
              <span className="text-[#D4AF37] font-bold text-sm">{i + 1}</span>
            </div>
            <h3 className="text-lg font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{v.title}</h3>
            <p className="text-sm text-[#9CA3AF] leading-relaxed">{v.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await axios.post(`${API}/contact`, form);
      setSuccess(true);
      setForm({ name: '', email: '', subject: '', message: '' });
    } catch (e) {
      setError('Failed to send message. Please try again.');
    } finally { setSubmitting(false); }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="contact-page">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl sm:text-4xl font-bold text-[#F3F4F6] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Get in Touch
          </h1>
          <p className="text-[#9CA3AF] mb-8">
            Have questions, feedback, or business inquiries? We'd love to hear from you.
          </p>

          <div className="space-y-4 mb-8">
            <div className="flex items-center gap-3 text-sm text-[#9CA3AF]">
              <div className="w-10 h-10 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center">
                <Mail className="w-4 h-4 text-[#D4AF37]" />
              </div>
              <div>
                <p className="text-[#F3F4F6] font-medium">Email</p>
                <p>contact@finnews.com</p>
              </div>
            </div>
            <div className="flex items-center gap-3 text-sm text-[#9CA3AF]">
              <div className="w-10 h-10 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center">
                <MapPin className="w-4 h-4 text-[#D4AF37]" />
              </div>
              <div>
                <p className="text-[#F3F4F6] font-medium">Location</p>
                <p>Worldwide, Remote First</p>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <form onSubmit={handleSubmit} className="bg-[#121620] border border-[#232B3E] rounded-lg p-6 space-y-4" data-testid="contact-form">
            {success && (
              <div className="p-3 bg-[#10B981]/10 border border-[#10B981]/30 rounded-lg text-sm text-[#10B981]" data-testid="contact-success">
                Message sent successfully! We'll get back to you soon.
              </div>
            )}
            {error && (
              <div className="p-3 bg-[#EF4444]/10 border border-[#EF4444]/30 rounded-lg text-sm text-[#EF4444]">{error}</div>
            )}
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Name</label>
              <input
                type="text" required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] transition-colors"
                data-testid="contact-name-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Email</label>
              <input
                type="email" required value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] transition-colors"
                data-testid="contact-email-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Subject</label>
              <input
                type="text" value={form.subject} onChange={e => setForm({...form, subject: e.target.value})}
                className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] transition-colors"
                data-testid="contact-subject-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-1.5">Message</label>
              <textarea
                required rows={5} value={form.message} onChange={e => setForm({...form, message: e.target.value})}
                className="w-full px-3 py-2.5 bg-[#0A0D14] border border-[#232B3E] rounded-lg text-[#F3F4F6] text-sm focus:outline-none focus:border-[#D4AF37] transition-colors resize-none"
                data-testid="contact-message-input"
              />
            </div>
            <button
              type="submit" disabled={submitting}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-50 transition-colors"
              data-testid="contact-submit-btn"
            >
              <Send className="w-4 h-4" /> {submitting ? 'Sending...' : 'Send Message'}
            </button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
