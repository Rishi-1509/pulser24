import type { ReactNode } from 'react';
import type { DocumentAnalysis } from '../types/api';

export type NavSection =
  | 'dashboard'
  | 'upload'
  | 'analysis'
  | 'hyperlinks'
  | 'assets'
  | 'designer'
  | 'preview'
  | 'validation'
  | 'export'
  | 'settings';

interface MainLayoutProps {
  currentSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  activeDoc: DocumentAnalysis | null;
  children: ReactNode;
}

const NAV_ITEMS: Array<{ id: NavSection; label: string; icon: string; requiresDoc?: boolean }> = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'upload', label: 'New Conversion', icon: '📤' },
  { id: 'analysis', label: 'PDF Analysis', icon: '📑', requiresDoc: true },
  { id: 'hyperlinks', label: 'Hyperlink Manager', icon: '🔗', requiresDoc: true },
  { id: 'assets', label: 'Asset Library', icon: '🖼️', requiresDoc: true },
  { id: 'designer', label: 'Email Designer', icon: '🎨', requiresDoc: true },
  { id: 'preview', label: 'Preview Studio', icon: '👁️', requiresDoc: true },
  { id: 'validation', label: 'Validation Engine', icon: '✅', requiresDoc: true },
  { id: 'export', label: 'Export Centre', icon: '📦', requiresDoc: true },
  { id: 'settings', label: 'Settings', icon: '⚙️' },
];

export default function MainLayout({
  currentSection,
  onSelectSection,
  activeDoc,
  children,
}: MainLayoutProps) {
  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-800 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col shrink-0 border-r border-slate-800">
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-black text-white text-base shadow-md">
            P
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white leading-tight">
              PULSE R24
            </h1>
            <span className="text-[10px] text-blue-400 font-medium tracking-wide uppercase">
              Email Publishing Studio
            </span>
          </div>
        </div>

        {/* Active Document Badge */}
        {activeDoc ? (
          <div className="mx-3 mt-3 p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] uppercase font-bold text-slate-400">Active Document</span>
              <span className="px-1.5 py-0.2 bg-emerald-500/20 text-emerald-400 font-semibold rounded text-[10px]">
                {activeDoc.page_count} Pages
              </span>
            </div>
            <p className="font-medium text-slate-200 truncate" title={activeDoc.filename}>
              {activeDoc.filename}
            </p>
            <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-400">
              <span>🔗 {activeDoc.total_hyperlinks} Links</span>
              <span>•</span>
              <span>{activeDoc.qr_detected ? '📱 QR Detected' : 'No QR'}</span>
            </div>
          </div>
        ) : (
          <div className="mx-3 mt-3 p-2.5 rounded-lg bg-slate-800/40 border border-dashed border-slate-700 text-xs text-slate-400 text-center">
            No active document.
            <button
              onClick={() => onSelectSection('upload')}
              className="mt-1 block w-full text-center text-blue-400 font-semibold hover:underline"
            >
              Upload PDF &rarr;
            </button>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const isActive = currentSection === item.id;
            const disabled = item.requiresDoc && !activeDoc;
            return (
              <button
                key={item.id}
                disabled={disabled}
                onClick={() => onSelectSection(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-xs font-medium rounded-lg transition-colors text-left ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm font-semibold'
                    : disabled
                    ? 'text-slate-600 cursor-not-allowed'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer info */}
        <div className="p-3 border-t border-slate-800 text-[10px] text-slate-500 text-center">
          Pulse R24 Studio v1.0.0 &middot; Production Ready
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {currentSection.replace('-', ' ')}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {activeDoc && (
              <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span>Ref: <strong className="text-slate-700">{activeDoc.doc_id}</strong></span>
              </div>
            )}
            <button
              onClick={() => onSelectSection('upload')}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg shadow-sm transition"
            >
              + Upload PDF
            </button>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
}
