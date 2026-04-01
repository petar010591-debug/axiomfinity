import { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import Marquee from 'react-fast-marquee';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function TickerStrip() {
  const [tickers, setTickers] = useState([]);

  useEffect(() => {
    const fetchTickers = async () => {
      try {
        const { data } = await axios.get(`${API}/market/ticker`);
        if (data.tickers?.length) setTickers(data.tickers);
      } catch {}
    };
    fetchTickers();
    const interval = setInterval(fetchTickers, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!tickers.length) return null;

  const formatPrice = (price) => {
    if (price >= 1000) return `$${price.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
    if (price >= 1) return `$${price.toFixed(2)}`;
    return `$${price.toFixed(4)}`;
  };

  return (
    <div className="bg-[#121620] border-b border-[#232B3E] py-2" data-testid="ticker-strip">
      <Marquee speed={30} gradient={false} pauseOnHover>
        {[...tickers, ...tickers].map((t, i) => (
          <div key={`${t.symbol}-${i}`} className="flex items-center gap-2 mx-6 text-sm">
            <span className="font-semibold text-[#F3F4F6]">{t.symbol}</span>
            <span className="text-[#9CA3AF]">{formatPrice(t.price)}</span>
            <span className={`flex items-center gap-0.5 text-xs font-medium ${
              t.change_24h > 0 ? 'text-[#10B981]' : t.change_24h < 0 ? 'text-[#EF4444]' : 'text-[#6B7280]'
            }`}>
              {t.change_24h > 0 ? <TrendingUp className="w-3 h-3" /> : t.change_24h < 0 ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
              {t.change_24h > 0 ? '+' : ''}{t.change_24h}%
            </span>
          </div>
        ))}
      </Marquee>
    </div>
  );
}
