import { useState } from 'react';
import { Plus, Minus } from 'lucide-react';

export default function FaqAccordion({ faqs = [] }) {
  const [openIndex, setOpenIndex] = useState(null);

  if (!faqs || faqs.length === 0) return null;

  const toggle = (i) => setOpenIndex(openIndex === i ? null : i);

  return (
    <section className="mt-12 mb-8" data-testid="faq-section">
      <div className="bg-[#111827] border border-[#232B3E] rounded-xl p-6 sm:p-8">
        <h2 className="text-xl sm:text-2xl font-bold text-[#F3F4F6] mb-6" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Frequently Asked Questions
        </h2>
        <div className="space-y-0 divide-y divide-[#232B3E]">
          {faqs.map((faq, i) => (
            <div key={i} data-testid={`faq-item-${i}`}>
              <button
                type="button"
                onClick={() => toggle(i)}
                className="flex items-center justify-between w-full py-5 text-left gap-4 group"
                data-testid={`faq-toggle-${i}`}
              >
                <span className="text-sm sm:text-base font-semibold text-[#E5E7EB] group-hover:text-[#D4AF37] transition-colors">
                  {i + 1}. {faq.question}
                </span>
                <span className="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full border border-[#D4AF37]/40 text-[#D4AF37]">
                  {openIndex === i ? <Minus className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
                </span>
              </button>
              <div
                className={`overflow-hidden transition-all duration-300 ${
                  openIndex === i ? 'max-h-96 opacity-100 pb-5' : 'max-h-0 opacity-0'
                }`}
              >
                <p className="text-sm text-[#9CA3AF] leading-relaxed pl-0.5">{faq.answer}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </section>
  );
}
