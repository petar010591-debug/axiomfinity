import { useEditor, EditorContent, BubbleMenu } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Youtube from '@tiptap/extension-youtube';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableHeader } from '@tiptap/extension-table-header';
import { TableCell } from '@tiptap/extension-table-cell';
import Link from '@tiptap/extension-link';
import Placeholder from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import { useCallback, useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { getAuthHeader } from '../contexts/AuthContext';
import {
  Bold, Italic, Underline as UnderlineIcon, Strikethrough, Code, List, ListOrdered,
  Heading1, Heading2, Heading3, Quote, Minus, Undo, Redo, Link as LinkIcon,
  Image as ImageIcon, Youtube as YoutubeIcon, Table as TableIcon, Twitter,
  AlignLeft, AlignCenter, AlignRight, Upload, X, Plus, Trash2
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function ToolbarButton({ onClick, active, disabled, children, title }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`p-1.5 rounded transition-colors ${
        active ? 'bg-[#D4AF37]/20 text-[#D4AF37]' : 'text-[#9CA3AF] hover:text-[#F3F4F6] hover:bg-[#1C2230]'
      } ${disabled ? 'opacity-30 cursor-not-allowed' : ''}`}
    >
      {children}
    </button>
  );
}

function ToolbarDivider() {
  return <div className="w-px h-5 bg-[#232B3E] mx-1" />;
}

export default function TipTapEditor({ content, onChange }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [showEmbedModal, setShowEmbedModal] = useState(null); // 'youtube' | 'twitter' | 'image-url' | null
  const [embedUrl, setEmbedUrl] = useState('');

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [2, 3, 4] },
      }),
      Image.configure({ inline: false, allowBase64: false }),
      Youtube.configure({ width: 640, height: 360, nocookie: true }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Link.configure({ openOnClick: false, autolink: true }),
      Placeholder.configure({ placeholder: 'Start writing your article...' }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Underline,
    ],
    content: content || '',
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-invert max-w-none focus:outline-none min-h-[300px] px-4 py-3',
      },
    },
  });

  // Sync content from parent when it loads asynchronously (e.g. editing existing article)
  useEffect(() => {
    if (editor && content && editor.isEmpty) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  const handleImageUpload = useCallback(async (file) => {
    if (!file || !file.type.startsWith('image/')) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const { data } = await axios.post(`${API}/upload`, formData, {
        headers: { ...getAuthHeader(), 'Content-Type': 'multipart/form-data' },
      });
      if (data.url && editor) {
        editor.chain().focus().setImage({ src: data.url }).run();
      }
    } catch (e) {
      console.error('Upload failed:', e);
    } finally {
      setUploading(false);
    }
  }, [editor]);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) handleImageUpload(file);
    e.target.value = '';
  };

  const insertEmbed = () => {
    if (!embedUrl.trim() || !editor) return;
    if (showEmbedModal === 'youtube') {
      editor.chain().focus().setYoutubeVideo({ src: embedUrl.trim() }).run();
    } else if (showEmbedModal === 'twitter') {
      // Insert Twitter embed as custom HTML
      const tweetId = embedUrl.match(/status\/(\d+)/)?.[1] || embedUrl.trim();
      const html = `<div data-twitter-embed="${tweetId}" class="twitter-embed"><blockquote><p>Loading tweet...</p><a href="https://twitter.com/i/status/${tweetId}" target="_blank">View tweet</a></blockquote></div>`;
      editor.chain().focus().insertContent(html).run();
    } else if (showEmbedModal === 'image-url') {
      editor.chain().focus().setImage({ src: embedUrl.trim() }).run();
    }
    setEmbedUrl('');
    setShowEmbedModal(null);
  };

  if (!editor) return null;

  return (
    <div className="border border-[#232B3E] rounded-lg overflow-hidden bg-[#121620]" data-testid="tiptap-editor">
      {/* Toolbar */}
      <div className="flex items-center flex-wrap gap-0.5 px-2 py-1.5 bg-[#0A0D14] border-b border-[#232B3E]" data-testid="editor-toolbar">
        <ToolbarButton onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive('bold')} title="Bold">
          <Bold className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive('italic')} title="Italic">
          <Italic className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive('underline')} title="Underline">
          <UnderlineIcon className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleStrike().run()} active={editor.isActive('strike')} title="Strikethrough">
          <Strikethrough className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleCode().run()} active={editor.isActive('code')} title="Inline Code">
          <Code className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} active={editor.isActive('heading', { level: 2 })} title="Heading 2">
          <Heading2 className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()} active={editor.isActive('heading', { level: 3 })} title="Heading 3">
          <Heading3 className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => editor.chain().focus().toggleBulletList().run()} active={editor.isActive('bulletList')} title="Bullet List">
          <List className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive('orderedList')} title="Ordered List">
          <ListOrdered className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().toggleBlockquote().run()} active={editor.isActive('blockquote')} title="Quote">
          <Quote className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().setHorizontalRule().run()} title="Divider">
          <Minus className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('left').run()} active={editor.isActive({ textAlign: 'left' })} title="Align Left">
          <AlignLeft className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('center').run()} active={editor.isActive({ textAlign: 'center' })} title="Align Center">
          <AlignCenter className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().setTextAlign('right').run()} active={editor.isActive({ textAlign: 'right' })} title="Align Right">
          <AlignRight className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        {/* Link */}
        <ToolbarButton
          onClick={() => {
            const url = window.prompt('Enter URL');
            if (url) editor.chain().focus().setLink({ href: url }).run();
          }}
          active={editor.isActive('link')}
          title="Insert Link"
        >
          <LinkIcon className="w-4 h-4" />
        </ToolbarButton>

        {/* Image Upload */}
        <ToolbarButton onClick={() => fileInputRef.current?.click()} title="Upload Image" disabled={uploading}>
          <Upload className="w-4 h-4" />
        </ToolbarButton>
        <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />

        {/* Image URL */}
        <ToolbarButton onClick={() => setShowEmbedModal('image-url')} title="Image from URL">
          <ImageIcon className="w-4 h-4" />
        </ToolbarButton>

        {/* YouTube */}
        <ToolbarButton onClick={() => setShowEmbedModal('youtube')} title="Embed YouTube">
          <YoutubeIcon className="w-4 h-4" />
        </ToolbarButton>

        {/* Twitter */}
        <ToolbarButton onClick={() => setShowEmbedModal('twitter')} title="Embed Tweet">
          <Twitter className="w-4 h-4" />
        </ToolbarButton>

        {/* Table */}
        <ToolbarButton
          onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
          title="Insert Table"
        >
          <TableIcon className="w-4 h-4" />
        </ToolbarButton>

        <ToolbarDivider />

        <ToolbarButton onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()} title="Undo">
          <Undo className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()} title="Redo">
          <Redo className="w-4 h-4" />
        </ToolbarButton>

        {uploading && <span className="text-xs text-[#D4AF37] ml-2">Uploading...</span>}
      </div>

      {/* Table controls (shown when inside table) */}
      {editor.isActive('table') && (
        <div className="flex items-center gap-1 px-2 py-1 bg-[#1C2230] border-b border-[#232B3E]">
          <span className="text-[10px] uppercase tracking-wider text-[#6B7280] mr-2">Table:</span>
          <button type="button" onClick={() => editor.chain().focus().addColumnAfter().run()} className="px-2 py-0.5 text-[10px] text-[#9CA3AF] bg-[#0A0D14] rounded hover:text-[#D4AF37]">+ Col</button>
          <button type="button" onClick={() => editor.chain().focus().addRowAfter().run()} className="px-2 py-0.5 text-[10px] text-[#9CA3AF] bg-[#0A0D14] rounded hover:text-[#D4AF37]">+ Row</button>
          <button type="button" onClick={() => editor.chain().focus().deleteColumn().run()} className="px-2 py-0.5 text-[10px] text-[#9CA3AF] bg-[#0A0D14] rounded hover:text-[#EF4444]">- Col</button>
          <button type="button" onClick={() => editor.chain().focus().deleteRow().run()} className="px-2 py-0.5 text-[10px] text-[#9CA3AF] bg-[#0A0D14] rounded hover:text-[#EF4444]">- Row</button>
          <button type="button" onClick={() => editor.chain().focus().deleteTable().run()} className="px-2 py-0.5 text-[10px] text-[#EF4444] bg-[#0A0D14] rounded hover:text-[#EF4444]">
            <Trash2 className="w-3 h-3 inline" /> Table
          </button>
        </div>
      )}

      {/* Embed Modal */}
      {showEmbedModal && (
        <div className="flex items-center gap-2 px-3 py-2 bg-[#1C2230] border-b border-[#232B3E]">
          <span className="text-xs text-[#D4AF37] font-medium capitalize">{showEmbedModal.replace('-', ' ')}:</span>
          <input
            autoFocus
            type="text"
            value={embedUrl}
            onChange={e => setEmbedUrl(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); insertEmbed(); } }}
            placeholder={
              showEmbedModal === 'youtube' ? 'https://youtube.com/watch?v=...' :
              showEmbedModal === 'twitter' ? 'https://twitter.com/.../status/...' :
              'https://example.com/image.jpg'
            }
            className="flex-1 px-2 py-1 text-sm bg-[#0A0D14] border border-[#232B3E] rounded text-[#F3F4F6] focus:outline-none focus:border-[#D4AF37]"
            data-testid="embed-url-input"
          />
          <button type="button" onClick={insertEmbed} className="px-3 py-1 text-xs bg-[#D4AF37] text-black rounded font-medium hover:bg-[#C39F2F]">Insert</button>
          <button type="button" onClick={() => { setShowEmbedModal(null); setEmbedUrl(''); }} className="p-1 text-[#6B7280] hover:text-[#F3F4F6]">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Editor Content */}
      <EditorContent editor={editor} className="tiptap-content" />
    </div>
  );
}
