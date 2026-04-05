import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../contexts/AuthContext';
import { X, Search, Upload, Image as ImageIcon, Loader2, RefreshCw, Check } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function MediaLibrary({ onSelect, onClose }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [selected, setSelected] = useState(null);

  const fetchMedia = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, limit: 24 };
      if (search.trim()) params.q = search.trim();
      const { data } = await axios.get(`${API}/media`, { headers: getAuthHeader(), params });
      setItems(data.items || []);
      setTotal(data.total || 0);
      setPages(data.pages || 1);
    } catch {
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => { fetchMedia(); }, [fetchMedia]);

  // Debounced search
  useEffect(() => {
    setPage(1);
  }, [search]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await axios.post(`${API}/upload`, formData, { headers: getAuthHeader() });
      if (data.url) {
        setSelected(data.url);
        fetchMedia();
      }
    } catch {
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      const { data } = await axios.post(`${API}/media/sync-cloudinary`, {}, { headers: getAuthHeader() });
      if (data.imported > 0) fetchMedia();
    } catch {
    } finally {
      setSyncing(false);
    }
  };

  const handleConfirm = () => {
    if (selected) {
      onSelect(selected);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" data-testid="media-library-modal">
      <div className="bg-[#0F1219] border border-[#232B3E] rounded-xl w-[90vw] max-w-5xl max-h-[85vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#232B3E]">
          <div className="flex items-center gap-3">
            <ImageIcon className="w-5 h-5 text-[#D4AF37]" />
            <h2 className="text-lg font-bold text-[#F3F4F6]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>Media Library</h2>
            <span className="text-xs text-[#6B7280]">{total} images</span>
          </div>
          <button onClick={onClose} className="p-1.5 text-[#6B7280] hover:text-[#F3F4F6] transition-colors" data-testid="media-close-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-3 px-5 py-3 border-b border-[#1A202E]">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6B7280]" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search images..."
              className="w-full pl-8 pr-3 py-2 text-sm bg-[#121620] border border-[#232B3E] rounded-lg text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37]"
              data-testid="media-search-input"
            />
          </div>
          <label className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium cursor-pointer transition-colors ${uploading ? 'bg-[#232B3E] text-[#6B7280]' : 'bg-[#D4AF37] text-black hover:bg-[#C39F2F]'}`} data-testid="media-upload-btn">
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {uploading ? 'Uploading...' : 'Upload New'}
            <input type="file" accept="image/*" className="hidden" disabled={uploading} onChange={handleUpload} />
          </label>
          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-[#9CA3AF] bg-[#121620] border border-[#232B3E] rounded-lg hover:border-[#D4AF37] hover:text-[#D4AF37] transition-colors disabled:opacity-50"
            title="Import existing images from Cloudinary"
            data-testid="media-sync-btn"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            Sync
          </button>
        </div>

        {/* Grid */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {loading ? (
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="aspect-square bg-[#1C2230] rounded-lg animate-pulse" />
              ))}
            </div>
          ) : items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <ImageIcon className="w-12 h-12 text-[#232B3E] mb-3" />
              <p className="text-[#6B7280] text-sm">
                {search ? 'No images match your search.' : 'No images yet. Upload one or sync from Cloudinary.'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {items.map((item, idx) => {
                const isSelected = selected === item.url;
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setSelected(isSelected ? null : item.url)}
                    className={`group relative aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                      isSelected ? 'border-[#D4AF37] ring-2 ring-[#D4AF37]/30' : 'border-transparent hover:border-[#D4AF37]/50'
                    }`}
                    data-testid={`media-item-${idx}`}
                  >
                    <img src={item.url} alt={item.filename} className="w-full h-full object-cover" loading="lazy" />
                    {isSelected && (
                      <div className="absolute inset-0 bg-[#D4AF37]/20 flex items-center justify-center">
                        <div className="w-7 h-7 bg-[#D4AF37] rounded-full flex items-center justify-center">
                          <Check className="w-4 h-4 text-black" />
                        </div>
                      </div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 px-1.5 py-1 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                      <p className="text-[10px] text-white truncate">{item.filename}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Pagination */}
        {pages > 1 && (
          <div className="flex items-center justify-center gap-2 px-5 py-2 border-t border-[#1A202E]">
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 text-xs border border-[#232B3E] text-[#9CA3AF] rounded disabled:opacity-40 hover:border-[#D4AF37]">Prev</button>
            <span className="text-xs text-[#6B7280]">{page} / {pages}</span>
            <button onClick={() => setPage(p => Math.min(pages, p + 1))} disabled={page === pages} className="px-3 py-1 text-xs border border-[#232B3E] text-[#9CA3AF] rounded disabled:opacity-40 hover:border-[#D4AF37]">Next</button>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-[#232B3E]">
          <div className="text-xs text-[#6B7280]">
            {selected ? (
              <span className="text-[#D4AF37]">1 image selected</span>
            ) : (
              'Click an image to select it'
            )}
          </div>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 text-sm text-[#9CA3AF] hover:text-[#F3F4F6] transition-colors" data-testid="media-cancel-btn">
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={!selected}
              className="px-4 py-2 text-sm bg-[#D4AF37] text-black font-medium rounded-lg hover:bg-[#C39F2F] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              data-testid="media-select-btn"
            >
              Use Selected Image
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
