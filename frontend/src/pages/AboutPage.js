import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Mail } from 'lucide-react';
import { motion } from 'framer-motion';
import FaqAccordion from '../components/FaqAccordion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AboutPage() {
  const [aboutContent, setAboutContent] = useState(null);
  const [team, setTeam] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [aboutRes, teamRes] = await Promise.all([
          axios.get(`${API}/pages/about`).catch(() => null),
          axios.get(`${API}/team`).catch(() => ({ data: [] })),
        ]);
        if (aboutRes) setAboutContent(aboutRes.data);
        setTeam(teamRes.data);
      } catch {}
    };
    fetchData();
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

      {/* Team Section */}
      {team.length > 0 && (
        <section className="mb-16" data-testid="team-section">
          <h2 className="text-2xl font-bold text-[#F3F4F6] mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Our Team</h2>
          <p className="text-sm text-[#6B7280] mb-8">Meet the people behind AxiomFinity.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {team.map((m, i) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * i }}
                className="bg-[#121620] border border-[#232B3E] rounded-lg p-6 text-center"
                data-testid={`team-card-${m.id}`}
              >
                <div className="w-24 h-24 rounded-full mx-auto mb-4 bg-[#1C2230] border-2 border-[#D4AF37]/20 overflow-hidden">
                  {m.avatar_url ? (
                    <img src={m.avatar_url} alt={m.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-[#6B7280] text-3xl font-bold">{m.name?.[0]}</div>
                  )}
                </div>
                <h3 className="text-base font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>{m.name}</h3>
                <p className="text-sm text-[#D4AF37] mt-0.5">{m.role_title}</p>
                {m.bio && <p className="text-xs text-[#9CA3AF] mt-3 leading-relaxed">{m.bio}</p>}
              </motion.div>
            ))}
          </div>
        </section>
      )}
      {/* FAQs */}
      {aboutContent?.faqs?.length > 0 && (
        <div className="max-w-3xl">
          <FaqAccordion faqs={aboutContent.faqs} />
        </div>
      )}
    </div>
  );
}

export function ContactPage() {
  const [pageContent, setPageContent] = useState(null);

  useEffect(() => {
    axios.get(`${API}/pages/contact`).then(res => setPageContent(res.data)).catch(() => {});
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8" data-testid="contact-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[#F3F4F6] mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Contact
        </h1>
        <p className="text-lg text-[#9CA3AF] mb-8 max-w-2xl">
          Have questions, feedback, or business inquiries? We'd love to hear from you.
        </p>
      </motion.div>

      {/* CMS Editable Content */}
      {pageContent && pageContent.content && (
        <div className="article-content max-w-3xl mb-12" dangerouslySetInnerHTML={{ __html: pageContent.content }} />
      )}

      {/* Contact Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="max-w-3xl"
      >
        <div className="bg-[#121620] border border-[#232B3E] rounded-lg p-6" data-testid="contact-info-card">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center flex-shrink-0">
              <Mail className="w-5 h-5 text-[#D4AF37]" />
            </div>
            <div>
              <p className="text-sm text-[#9CA3AF] mb-0.5">Email Us</p>
              <a
                href="mailto:petar@axiomfinity.com"
                className="text-lg font-medium text-[#D4AF37] hover:text-[#C39F2F] transition-colors"
                data-testid="contact-email-link"
              >
                petar@axiomfinity.com
              </a>
            </div>
          </div>
        </div>
      </motion.div>

      {/* FAQs */}
      {pageContent?.faqs?.length > 0 && (
        <div className="max-w-3xl mt-12">
          <FaqAccordion faqs={pageContent.faqs} />
        </div>
      )}
    </div>
  );
}
