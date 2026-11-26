import { useState } from 'react';
import { generateEmail } from '../services/api';
import type { DocumentAnalysis, EmailGenerationResponse } from '../types/api';
import type { NavSection } from '../layouts/MainLayout';

interface EmailDesignerPageProps {
  activeDoc: DocumentAnalysis;
  onNavigate: (section: NavSection) => void;
  onEmailGenerated: (res: EmailGenerationResponse) => void;
}

export default function EmailDesignerPage({
  activeDoc,
  onNavigate,
  onEmailGenerated,
}: EmailDesignerPageProps) {
  const [mode, setMode] = useState<'reconstructed' | 'faithful'>('reconstructed');
  const [includeSourceDir, setIncludeSourceDir] = useState(true);
  const [maxWidth, setMaxWidth] = useState(650);
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastGenerated, setLastGenerated] = useState<EmailGenerationResponse | null>(null);

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      const res = await generateEmail(activeDoc.doc_id, mode, includeSourceDir);
      setLastGenerated(res);
      onEmailGenerated(res);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-800">Email Designer & Template Engine</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Choose between Faithful Page Slice mode and Reconstructed Native HTML mode for Gmail & ESP compatibility.
        </p>
      </div>

      {/* Mode Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Mode B: Reconstructed Native HTML */}
        <div
          onClick={() => setMode('reconstructed')}
          className={`p-5 rounded-2xl border-2 cursor-pointer transition relative flex flex-col justify-between ${
            mode === 'reconstructed'
              ? 'border-blue-600 bg-blue-50/30 shadow-md'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          {mode === 'reconstructed' && (
            <span className="absolute top-4 right-4 px-2 py-0.5 bg-blue-600 text-white text-[10px] font-bold rounded-full">
              SELECTED
            </span>
          )}
          <div>
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center text-lg mb-3">
              🧩
            </div>
            <h3 className="text-sm font-bold text-slate-800">MODE B: Reconstructed Native HTML</h3>
            <span className="text-[11px] font-medium text-blue-600 block mt-0.5">
              Recommended for Email Clients (Gmail, Outlook, Apple Mail)
            </span>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Rebuilds the entire newsletter into responsive, table-based HTML with inline CSS. Headlines,
              paragraphs, and tables are native text. All 41 hyperlinks are mapped directly to visible anchor
              text with interactive hover states.
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-600 space-y-1">
            <div className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Fast loading & 100% responsive
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Direct inline clickable hyperlinks
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Embedded QR Code section & social bar
            </div>
          </div>
        </div>

        {/* Mode A: Faithful Mode */}
        <div
          onClick={() => setMode('faithful')}
          className={`p-5 rounded-2xl border-2 cursor-pointer transition relative flex flex-col justify-between ${
            mode === 'faithful'
              ? 'border-blue-600 bg-blue-50/30 shadow-md'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          {mode === 'faithful' && (
            <span className="absolute top-4 right-4 px-2 py-0.5 bg-blue-600 text-white text-[10px] font-bold rounded-full">
              SELECTED
            </span>
          )}
          <div>
            <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center text-lg mb-3">
              🖼️
            </div>
            <h3 className="text-sm font-bold text-slate-800">MODE A: Faithful Page Mode</h3>
            <span className="text-[11px] font-medium text-indigo-600 block mt-0.5">
              Preserves Exact Visual Layout & Vector Artwork
            </span>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              High-resolution sequential page renders preserve 100% of the graphic designer&apos;s layout.
              Because email clients inconsistently support image map coordinates, a structured, clickable
              source directory is appended at the bottom.
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-600 space-y-1">
            <div className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> 100% visual layout preservation
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Structured clickable source index
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-emerald-500 font-bold">✓</span> Original PDF available as attachment
            </div>
          </div>
        </div>
      </div>

      {/* Formatting & Layout Controls */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
          Layout & Email Options
        </h4>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">
              Container Max Width (px)
            </label>
            <input
              type="number"
              min={550}
              max={700}
              value={maxWidth}
              onChange={(e) => setMaxWidth(Number(e.target.value))}
              className="text-xs p-2 rounded-lg border border-slate-300 w-full"
            />
            <span className="text-[10px] text-slate-400 mt-1 block">
              Standard email client width is 600 - 650px.
            </span>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
            <div>
              <span className="text-xs font-semibold text-slate-800 block">
                Include Source Directory
              </span>
              <span className="text-[10px] text-slate-500">
                Lists all {activeDoc.total_hyperlinks} sources grouped by page
              </span>
            </div>
            <input
              type="checkbox"
              checked={includeSourceDir}
              onChange={(e) => setIncludeSourceDir(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded"
            />
          </div>
        </div>
      </div>

      {/* Generate Action Card */}
      <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl text-white">
        <div>
          <span className="text-xs font-medium text-slate-400 block">Ready to compile:</span>
          <span className="text-sm font-bold text-white capitalize">
            {mode} Mode &middot; {maxWidth}px container width
          </span>
        </div>
        <div className="flex gap-2">
          <button
            disabled={isGenerating}
            onClick={handleGenerate}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow transition"
          >
            {isGenerating ? 'Compiling HTML...' : 'Generate Email HTML'}
          </button>
          {lastGenerated && (
            <button
              onClick={() => onNavigate('preview')}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium rounded-xl border border-slate-700 transition"
            >
              Open in Preview Studio &rarr;
            </button>
          )}
        </div>
      </div>

      {/* Last Generated Summary */}
      {lastGenerated && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-emerald-800">
              ✓ Successfully generated {lastGenerated.mode.toUpperCase()} email
            </span>
            <span className="text-[10px] text-emerald-600 font-mono">
              {new Date(lastGenerated.generated_at).toLocaleTimeString()}
            </span>
          </div>
          <div className="flex gap-4 text-emerald-900">
            <span>Size: {(lastGenerated.character_count / 1024).toFixed(1)} KB</span>
            <span>Hyperlinks included: {lastGenerated.total_links_included}</span>
            <span>Table layout: 100% Inline CSS</span>
          </div>
        </div>
      )}
    </div>
  );
}
