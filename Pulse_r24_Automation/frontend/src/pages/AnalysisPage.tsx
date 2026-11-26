import { useState, useEffect } from 'react';
import { getTextBlocks } from '../services/api';
import type { DocumentAnalysis, TextBlock } from '../types/api';
import type { NavSection } from '../layouts/MainLayout';

interface AnalysisPageProps {
  activeDoc: DocumentAnalysis;
  onNavigate: (section: NavSection) => void;
}

export default function AnalysisPage({ activeDoc, onNavigate }: AnalysisPageProps) {
  const [blocks, setBlocks] = useState<TextBlock[]>([]);
  const [selectedPage, setSelectedPage] = useState<number>(1);
  const [loading, setLoading] = useState(true);
  const [searchFilter, setSearchFilter] = useState('');

  useEffect(() => {
    setLoading(true);
    getTextBlocks(activeDoc.doc_id)
      .then(setBlocks)
      .catch(() => setBlocks([]))
      .finally(() => setLoading(false));
  }, [activeDoc.doc_id]);

  const filteredBlocks = blocks.filter((b) => {
    const pageMatch = selectedPage === 0 || b.page === selectedPage;
    const textMatch = !searchFilter || b.text.toLowerCase().includes(searchFilter.toLowerCase());
    return pageMatch && textMatch;
  });

  return (
    <div className="space-y-6">
      {/* Header and Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-800">PDF Document Analysis</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Document metadata, page dimensions, text blocks, and font metrics.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onNavigate('hyperlinks')}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg shadow-xs transition"
          >
            Review Hyperlinks ({activeDoc.total_hyperlinks}) &rarr;
          </button>
          <button
            onClick={() => onNavigate('assets')}
            className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium rounded-lg shadow-xs transition"
          >
            Asset Library ({activeDoc.total_images})
          </button>
        </div>
      </div>

      {/* Metadata Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Document Title</span>
          <div className="text-sm font-bold text-slate-800 mt-1 truncate" title={activeDoc.title || activeDoc.filename}>
            {activeDoc.title || activeDoc.filename}
          </div>
          <span className="text-[11px] text-slate-400 mt-0.5 block font-mono">ID: {activeDoc.doc_id}</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pages & Dimensions</span>
          <div className="text-sm font-bold text-slate-800 mt-1">
            {activeDoc.page_count} Pages
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">
            {activeDoc.page_dimensions[0]
              ? `${activeDoc.page_dimensions[0].width} × ${activeDoc.page_dimensions[0].height} pt`
              : 'Standard A4'}
          </span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Text Hierarchy</span>
          <div className="text-sm font-bold text-slate-800 mt-1">
            {blocks.length} Blocks
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">
            {blocks.filter((b) => b.is_headline).length} headlines & subheadings
          </span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Embedded QR Code</span>
          <div className="text-sm font-bold text-slate-800 mt-1 flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${activeDoc.qr_detected ? 'bg-emerald-500' : 'bg-slate-300'}`}></span>
            {activeDoc.qr_detected ? 'Decoded (OpenCV)' : 'None'}
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block truncate" title={activeDoc.qr_content || ''}>
            {activeDoc.qr_content || 'No QR detected'}
          </span>
        </div>
      </div>

      {/* Text Blocks Inspector */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {/* Filter Bar */}
        <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-50/50">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-600">Filter Page:</span>
            <div className="flex rounded-lg border border-slate-200 overflow-hidden bg-white">
              <button
                onClick={() => setSelectedPage(0)}
                className={`px-2.5 py-1 text-xs font-medium ${
                  selectedPage === 0 ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                All
              </button>
              {Array.from({ length: activeDoc.page_count }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setSelectedPage(p)}
                  className={`px-2.5 py-1 text-xs font-medium border-l border-slate-200 ${
                    selectedPage === p ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  Page {p}
                </button>
              ))}
            </div>
          </div>

          <input
            type="text"
            placeholder="Search extracted text..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 w-full sm:w-64 bg-white"
          />
        </div>

        {/* Blocks List */}
        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading extracted blocks...</div>
        ) : filteredBlocks.length > 0 ? (
          <div className="divide-y divide-slate-100 max-h-[550px] overflow-y-auto">
            {filteredBlocks.map((blk) => (
              <div key={blk.id} className="p-4 hover:bg-slate-50/80 transition text-xs">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="px-1.5 py-0.5 rounded bg-slate-100 font-mono text-slate-600">
                      P{blk.page}
                    </span>
                    <span
                      className={`px-1.5 py-0.5 rounded font-semibold uppercase text-[10px] ${
                        blk.block_type === 'headline'
                          ? 'bg-blue-100 text-blue-700'
                          : blk.block_type === 'subheading'
                          ? 'bg-indigo-100 text-indigo-700'
                          : blk.block_type === 'citation'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {blk.block_type}
                    </span>
                    <span className="text-slate-400">
                      Font: {blk.font_name} ({blk.font_size}pt) {blk.is_bold && '• Bold'}
                    </span>
                  </div>
                  <span className="font-mono text-[10px] text-slate-400">
                    [{blk.bbox.x0}, {blk.bbox.y0}] &rarr; [{blk.bbox.x1}, {blk.bbox.y1}]
                  </span>
                </div>
                <p className="text-slate-700 font-normal leading-relaxed whitespace-pre-line mt-1">
                  {blk.text}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-400">
            No text blocks match the active filter.
          </div>
        )}
      </div>
    </div>
  );
}
