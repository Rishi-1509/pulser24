import { useState, useEffect } from 'react';
import { generateEmail } from '../services/api';
import type { DocumentAnalysis, EmailGenerationResponse, HyperlinkItem } from '../types/api';
import { getHyperlinks } from '../services/api';

interface PreviewStudioPageProps {
  activeDoc: DocumentAnalysis;
  lastGenerated: EmailGenerationResponse | null;
}

export default function PreviewStudioPage({
  activeDoc,
  lastGenerated: initialGenerated,
}: PreviewStudioPageProps) {
  const [deviceView, setDeviceView] = useState<'desktop' | 'mobile'>('desktop');
  const [mode, setMode] = useState<'reconstructed' | 'faithful'>(
    (initialGenerated?.mode as 'reconstructed' | 'faithful') || 'reconstructed'
  );
  const [htmlContent, setHtmlContent] = useState<string>(initialGenerated?.html_content || '');
  const [plainText, setPlainText] = useState<string>(initialGenerated?.plain_text_content || '');
  const [activeTab, setActiveTab] = useState<'preview' | 'html' | 'text' | 'links'>('preview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [links, setLinks] = useState<HyperlinkItem[]>([]);
  const [copied, setCopied] = useState(false);

  const fetchEmail = async (selectedMode: 'reconstructed' | 'faithful') => {
    try {
      setIsRefreshing(true);
      const res = await generateEmail(activeDoc.doc_id, selectedMode);
      setHtmlContent(res.html_content);
      setPlainText(res.plain_text_content);
      setMode(selectedMode);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Preview generation failed');
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    if (!htmlContent) {
      fetchEmail(mode);
    }
    getHyperlinks(activeDoc.doc_id)
      .then(setLinks)
      .catch(() => setLinks([]));
  }, [activeDoc.doc_id]);

  const handleCopyHtml = () => {
    navigator.clipboard.writeText(htmlContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      {/* Top Controls Toolbar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {/* Mode Switcher */}
          <div className="flex rounded-lg border border-slate-200 overflow-hidden bg-slate-50 text-xs font-semibold">
            <button
              onClick={() => fetchEmail('reconstructed')}
              className={`px-3 py-1.5 transition ${
                mode === 'reconstructed' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Reconstructed Native HTML
            </button>
            <button
              onClick={() => fetchEmail('faithful')}
              className={`px-3 py-1.5 transition border-l border-slate-200 ${
                mode === 'faithful' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Faithful Page Slices
            </button>
          </div>

          {/* View Tab Switcher */}
          <div className="flex rounded-lg border border-slate-200 overflow-hidden text-xs">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-3 py-1.5 font-medium ${
                activeTab === 'preview' ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              Live Render
            </button>
            <button
              onClick={() => setActiveTab('html')}
              className={`px-3 py-1.5 font-medium border-l border-slate-200 ${
                activeTab === 'html' ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              HTML Code
            </button>
            <button
              onClick={() => setActiveTab('text')}
              className={`px-3 py-1.5 font-medium border-l border-slate-200 ${
                activeTab === 'text' ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              Plain Text
            </button>
            <button
              onClick={() => setActiveTab('links')}
              className={`px-3 py-1.5 font-medium border-l border-slate-200 ${
                activeTab === 'links' ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              Link Inspector ({links.length})
            </button>
          </div>
        </div>

        {/* Device Switcher & Actions */}
        <div className="flex items-center gap-2">
          {activeTab === 'preview' && (
            <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200 text-xs">
              <button
                onClick={() => setDeviceView('desktop')}
                className={`px-2.5 py-1 rounded font-medium flex items-center gap-1.5 transition ${
                  deviceView === 'desktop' ? 'bg-white text-slate-800 shadow-xs' : 'text-slate-500'
                }`}
              >
                <span>💻</span> Desktop (650px)
              </button>
              <button
                onClick={() => setDeviceView('mobile')}
                className={`px-2.5 py-1 rounded font-medium flex items-center gap-1.5 transition ${
                  deviceView === 'mobile' ? 'bg-white text-slate-800 shadow-xs' : 'text-slate-500'
                }`}
              >
                <span>📱</span> Mobile (375px)
              </button>
            </div>
          )}

          <button
            onClick={() => fetchEmail(mode)}
            disabled={isRefreshing}
            className="p-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg text-slate-600 text-xs"
            title="Refresh preview"
          >
            {isRefreshing ? '⏳' : '🔄'}
          </button>

          <button
            onClick={handleCopyHtml}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-lg shadow-xs transition"
          >
            {copied ? '✓ Copied!' : 'Copy HTML'}
          </button>
        </div>
      </div>

      {/* Main Preview Surface */}
      <div className="bg-slate-200/70 rounded-2xl p-6 min-h-[680px] flex items-center justify-center border border-slate-300/60 overflow-hidden">
        {activeTab === 'preview' && (
          <div
            className={`transition-all duration-300 bg-white rounded-xl shadow-2xl overflow-hidden border border-slate-300 flex flex-col ${
              deviceView === 'desktop' ? 'w-[680px]' : 'w-[390px]'
            }`}
            style={{ height: '720px' }}
          >
            {/* Mock Email Client Header */}
            <div className="bg-slate-100 border-b border-slate-200 p-3 text-[11px] text-slate-600 space-y-1 shrink-0">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800">Pulse R24 Intelligence Bulletin</span>
                <span className="text-[10px] text-slate-400">Gmail / Webmail Preview</span>
              </div>
              <div className="text-slate-500 flex gap-4 text-[10px]">
                <span>From: editorial@pulser24.issp.in</span>
                <span>To: subscriber@corporate.com</span>
              </div>
            </div>

            {/* Sandboxed Live HTML Iframe */}
            <iframe
              title="Email HTML Preview"
              srcDoc={htmlContent}
              sandbox="allow-same-origin allow-popups"
              className="w-full flex-1 border-0 bg-slate-50"
            />
          </div>
        )}

        {activeTab === 'html' && (
          <div className="w-full max-w-4xl bg-slate-900 rounded-xl p-4 text-slate-100 shadow-xl overflow-hidden font-mono text-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3 text-[11px] text-slate-400">
              <span>email.html &middot; {(htmlContent.length / 1024).toFixed(1)} KB &middot; UTF-8</span>
              <button
                onClick={handleCopyHtml}
                className="text-blue-400 hover:underline font-semibold"
              >
                {copied ? '✓ Copied' : 'Copy All Code'}
              </button>
            </div>
            <pre className="overflow-auto max-h-[600px] text-[11px] text-slate-300 leading-relaxed whitespace-pre-wrap">
              {htmlContent}
            </pre>
          </div>
        )}

        {activeTab === 'text' && (
          <div className="w-full max-w-4xl bg-white rounded-xl p-5 text-slate-800 shadow-xl overflow-hidden font-mono text-xs border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-3 text-[11px] text-slate-500">
              <span>email.txt (Plain Text Alternative)</span>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(plainText);
                  alert('Plain text copied!');
                }}
                className="text-blue-600 hover:underline font-semibold"
              >
                Copy Plain Text
              </button>
            </div>
            <pre className="overflow-auto max-h-[600px] text-[11px] text-slate-700 leading-relaxed whitespace-pre-wrap font-mono">
              {plainText}
            </pre>
          </div>
        )}

        {activeTab === 'links' && (
          <div className="w-full max-w-4xl bg-white rounded-xl p-5 text-slate-800 shadow-xl overflow-hidden border border-slate-200">
            <h4 className="text-sm font-bold text-slate-800 mb-2">
              Hyperlink Destination Inspector ({links.length} Embedded Links)
            </h4>
            <p className="text-xs text-slate-500 mb-4">
              All clickable hyperlinks embedded into the email HTML. Click any URL to inspect its live destination.
            </p>
            <div className="divide-y divide-slate-100 max-h-[550px] overflow-y-auto text-xs">
              {links.map((l) => (
                <div key={l.id} className="py-2.5 flex items-start justify-between gap-4">
                  <div>
                    <span className="font-semibold text-blue-900 block">{l.visible_text}</span>
                    <a
                      href={l.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline font-mono text-[11px] break-all block mt-0.5"
                    >
                      {l.url}
                    </a>
                  </div>
                  <span className="px-2 py-0.5 bg-slate-100 text-slate-600 font-mono text-[10px] rounded shrink-0">
                    Page {l.page}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
