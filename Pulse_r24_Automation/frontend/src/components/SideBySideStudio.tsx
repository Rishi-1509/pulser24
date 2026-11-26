import { useState } from 'react';
import type { DocumentAnalysis } from '../types/api';

interface SideBySideStudioProps {
  activeDoc: DocumentAnalysis;
  htmlContent: string;
  mode: 'reconstructed' | 'faithful';
  onModeChange: (m: 'reconstructed' | 'faithful') => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export default function SideBySideStudio({
  activeDoc,
  htmlContent,
  mode,
  onModeChange,
  onRefresh,
  isRefreshing,
}: SideBySideStudioProps) {
  const [selectedPdfPage, setSelectedPdfPage] = useState<number>(1);
  const [deviceView, setDeviceView] = useState<'desktop' | 'mobile'>('desktop');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(htmlContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const pdfPageUrl = `/api/pages/${activeDoc.doc_id}/page_${selectedPdfPage}.png`;

  return (
    <div className="space-y-4">
      {/* Control Bar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        {/* Left: Mode Switcher */}
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-slate-200 overflow-hidden bg-slate-50 text-xs font-semibold">
            <button
              onClick={() => onModeChange('reconstructed')}
              className={`px-3 py-1.5 transition ${
                mode === 'reconstructed'
                  ? 'bg-blue-600 text-white shadow-xs font-bold'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              🧩 Reconstructed Native HTML
            </button>
            <button
              onClick={() => onModeChange('faithful')}
              className={`px-3 py-1.5 transition border-l border-slate-200 ${
                mode === 'faithful'
                  ? 'bg-blue-600 text-white shadow-xs font-bold'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              🖼️ Faithful Page Slices
            </button>
          </div>

          <span className="text-[11px] text-slate-500 hidden sm:inline">
            {mode === 'reconstructed'
              ? 'Native table layout with inline CSS & active hyperlinks'
              : 'High-res page renders with source index'}
          </span>
        </div>

        {/* Right: Device & Actions */}
        <div className="flex items-center gap-2">
          {/* Device Toggle */}
          <div className="flex items-center bg-slate-100 rounded-lg p-0.5 border border-slate-200 text-xs font-medium">
            <button
              onClick={() => setDeviceView('desktop')}
              className={`px-2.5 py-1 rounded transition ${
                deviceView === 'desktop' ? 'bg-white text-slate-800 shadow-xs font-bold' : 'text-slate-500'
              }`}
            >
              💻 Desktop (650px)
            </button>
            <button
              onClick={() => setDeviceView('mobile')}
              className={`px-2.5 py-1 rounded transition ${
                deviceView === 'mobile' ? 'bg-white text-slate-800 shadow-xs font-bold' : 'text-slate-500'
              }`}
            >
              📱 Mobile (375px)
            </button>
          </div>

          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg text-slate-600 text-xs"
            title="Refresh generated HTML"
          >
            {isRefreshing ? '⏳' : '🔄'}
          </button>

          <button
            onClick={handleCopy}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-xs transition"
          >
            {copied ? '✓ Copied!' : 'Copy HTML'}
          </button>
        </div>
      </div>

      {/* Side-by-Side Comparison Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* LEFT COLUMN: ORIGINAL PDF */}
        <div className="bg-slate-800 rounded-2xl p-4 text-white flex flex-col shadow-sm border border-slate-700">
          <div className="flex items-center justify-between pb-3 border-b border-slate-700 mb-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Original PDF Document
              </span>
              <span className="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded font-mono">
                {activeDoc.page_count} Pages
              </span>
            </div>

            {/* Page Selector Tabs */}
            <div className="flex rounded-lg overflow-hidden border border-slate-600 text-xs">
              {Array.from({ length: activeDoc.page_count }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setSelectedPdfPage(p)}
                  className={`px-3 py-1 font-semibold transition ${
                    selectedPdfPage === p
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  Page {p}
                </button>
              ))}
            </div>
          </div>

          {/* PDF Page Image Container */}
          <div className="flex-1 bg-slate-900 rounded-xl overflow-auto p-3 flex justify-center items-start min-h-[640px] max-h-[760px] border border-slate-700/60">
            <img
              src={pdfPageUrl}
              alt={`Original PDF Page ${selectedPdfPage}`}
              className="max-w-full h-auto rounded shadow-lg border border-slate-700"
            />
          </div>

          <div className="pt-2 text-center text-[11px] text-slate-400">
            Viewing High-Resolution Render of Original Bulletin Page {selectedPdfPage}
          </div>
        </div>

        {/* RIGHT COLUMN: GENERATED RESPONSIVE EMAIL */}
        <div className="bg-slate-100 rounded-2xl p-4 flex flex-col shadow-sm border border-slate-300">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-3 text-slate-800">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Live Generated Email
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">
                100% Inline CSS &middot; 41 Links
              </span>
            </div>

            <span className="text-[11px] text-slate-500 font-medium">
              Mode: <strong className="capitalize text-blue-700">{mode}</strong>
            </span>
          </div>

          {/* Email Preview Frame */}
          <div className="flex-1 bg-slate-200 rounded-xl p-3 flex justify-center items-start min-h-[640px] max-h-[760px] overflow-hidden border border-slate-300">
            <div
              className={`transition-all duration-300 bg-white rounded-lg shadow-xl overflow-hidden border border-slate-300 flex flex-col h-full ${
                deviceView === 'desktop' ? 'w-full max-w-[650px]' : 'w-[375px]'
              }`}
            >
              {/* Mock Webmail Header */}
              <div className="bg-slate-100 border-b border-slate-200 p-2 text-[10px] text-slate-600 flex justify-between items-center shrink-0">
                <span className="font-bold text-slate-800">Gmail Preview &middot; Pulse R24 Bulletin</span>
                <span className="text-slate-400">{deviceView === 'desktop' ? '650px width' : '375px width'}</span>
              </div>

              {/* Sandboxed Iframe */}
              <iframe
                title="Generated Email HTML"
                srcDoc={htmlContent}
                sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation"
                className="w-full flex-1 border-0 bg-slate-50 overflow-y-auto"
              />
            </div>
          </div>

          <div className="pt-2 text-center text-[11px] text-slate-500">
            Scrollable responsive HTML email with active hyperlinks &amp; table formatting
          </div>
        </div>
      </div>
    </div>
  );
}
