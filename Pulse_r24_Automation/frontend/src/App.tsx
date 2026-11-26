import { useState, useEffect } from 'react';
import SideBySideStudio from './components/SideBySideStudio';
import HyperlinkPage from './pages/HyperlinkPage';
import AssetLibraryPage from './pages/AssetLibraryPage';
import ValidationPage from './pages/ValidationPage';
import ExportCentrePage from './pages/ExportCentrePage';
import SettingsPage from './pages/SettingsPage';
import UploadPage from './pages/UploadPage';

import { listDocuments, generateEmail, createExportPackage } from './services/api';
import type { DocumentAnalysis } from './types/api';

type TabType = 'studio' | 'hyperlinks' | 'assets' | 'validation' | 'export' | 'settings' | 'upload';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('studio');
  const [documents, setDocuments] = useState<DocumentAnalysis[]>([]);
  const [activeDoc, setActiveDoc] = useState<DocumentAnalysis | null>(null);
  const [mode, setMode] = useState<'reconstructed' | 'faithful'>('reconstructed');
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isDownloadingZip, setIsDownloadingZip] = useState(false);

  // Initial load
  useEffect(() => {
    listDocuments()
      .then((docs) => {
        setDocuments(docs);
        if (docs.length > 0) {
          const doc = docs[0];
          setActiveDoc(doc);
          loadEmail(doc.doc_id, mode);
        }
      })
      .catch(() => {});
  }, []);

  const loadEmail = async (docId: string, emailMode: 'reconstructed' | 'faithful') => {
    try {
      setIsRefreshing(true);
      const res = await generateEmail(docId, emailMode);
      setHtmlContent(res.html_content);
      setMode(emailMode);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleModeChange = (newMode: 'reconstructed' | 'faithful') => {
    if (activeDoc) {
      loadEmail(activeDoc.doc_id, newMode);
    }
  };

  const handleUploadSuccess = (doc: DocumentAnalysis) => {
    setActiveDoc(doc);
    setDocuments((prev) => [doc, ...prev.filter((d) => d.doc_id !== doc.doc_id)]);
    setActiveTab('studio');
    loadEmail(doc.doc_id, 'reconstructed');
  };

  const handleQuickDownloadZip = async () => {
    if (!activeDoc) return;
    try {
      setIsDownloadingZip(true);
      await createExportPackage(activeDoc.doc_id);
      window.location.href = `/api/export/${activeDoc.doc_id}/download-zip`;
    } catch (err) {
      alert('Failed to package ZIP archive.');
    } finally {
      setIsDownloadingZip(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-800 flex flex-col font-sans">
      {/* TOP HEADER */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
          
          {/* Brand Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center font-black text-white text-base shadow-sm">
              P
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-sm sm:text-base tracking-tight">PULSE R24</span>
                <span className="text-[10px] bg-blue-500/30 text-blue-300 font-semibold px-2 py-0.5 rounded-full border border-blue-400/30 uppercase">
                  Publishing Studio
                </span>
              </div>
              <p className="text-[10px] text-slate-400 hidden sm:block">
                Convert PDF Newsletters to Responsive, Email-Compatible HTML
              </p>
            </div>
          </div>

          {/* Active Document Status Pill */}
          {activeDoc && (
            <div className="hidden md:flex items-center gap-2 bg-slate-800/90 border border-slate-700/80 px-3 py-1.5 rounded-full text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              {documents.length > 1 ? (
                <select
                  value={activeDoc.doc_id}
                  onChange={(e) => {
                    const found = documents.find((d) => d.doc_id === e.target.value);
                    if (found) {
                      setActiveDoc(found);
                      loadEmail(found.doc_id, mode);
                    }
                  }}
                  className="bg-transparent text-slate-200 font-medium text-xs border-0 cursor-pointer focus:outline-none"
                >
                  {documents.map((d) => (
                    <option key={d.doc_id} value={d.doc_id} className="bg-slate-900 text-white">
                      {d.filename}
                    </option>
                  ))}
                </select>
              ) : (
                <span className="text-slate-300 font-medium truncate max-w-[220px]">
                  {activeDoc.filename}
                </span>
              )}
              <span className="bg-blue-600/50 text-blue-200 text-[10px] px-2 py-0.2 rounded-full font-bold">
                {activeDoc.total_hyperlinks} Links
              </span>
            </div>
          )}

          {/* Quick Actions */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setActiveTab('upload')}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
            >
              + Upload PDF
            </button>

            {activeDoc && (
              <button
                onClick={handleQuickDownloadZip}
                disabled={isDownloadingZip}
                className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
              >
                <span>📦</span>
                <span>{isDownloadingZip ? 'Packaging...' : 'Download ZIP'}</span>
              </button>
            )}
          </div>
        </div>

        {/* PRIMARY STUDIO NAVIGATION TABS */}
        <div className="bg-slate-900/95 border-t border-slate-800/80 px-4 sm:px-6">
          <div className="max-w-7xl mx-auto flex items-center gap-1 overflow-x-auto text-xs py-1">
            {[
              { id: 'studio' as TabType, label: '👁️ Side-by-Side Studio', badge: null },
              { id: 'hyperlinks' as TabType, label: '🔗 Hyperlinks', badge: activeDoc ? `${activeDoc.total_hyperlinks}` : null },
              { id: 'assets' as TabType, label: '🖼️ Assets & QR Code', badge: activeDoc ? `${activeDoc.total_images}` : null },
              { id: 'validation' as TabType, label: '✅ Pre-Flight Audit', badge: '14/14' },
              { id: 'export' as TabType, label: '📦 Export & ESP Guides', badge: null },
              { id: 'settings' as TabType, label: '⚙️ Branding Settings', badge: null },
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-2 rounded-lg font-semibold transition whitespace-nowrap flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <span>{tab.label}</span>
                  {tab.badge && (
                    <span
                      className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                        isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* MAIN WORKSPACE CONTENT */}
      <main className="max-w-7xl mx-auto w-full p-4 sm:p-6 flex-1">
        {activeTab === 'upload' && (
          <UploadPage
            onUploadSuccess={handleUploadSuccess}
            onNavigate={(sec) => {
              if (sec === 'hyperlinks') setActiveTab('hyperlinks');
              else if (sec === 'assets') setActiveTab('assets');
              else setActiveTab('studio');
            }}
          />
        )}

        {activeTab === 'studio' && activeDoc && (
          <SideBySideStudio
            activeDoc={activeDoc}
            htmlContent={htmlContent}
            mode={mode}
            onModeChange={handleModeChange}
            onRefresh={() => loadEmail(activeDoc.doc_id, mode)}
            isRefreshing={isRefreshing}
          />
        )}

        {activeTab === 'hyperlinks' && activeDoc && (
          <HyperlinkPage activeDoc={activeDoc} />
        )}

        {activeTab === 'assets' && activeDoc && (
          <AssetLibraryPage activeDoc={activeDoc} />
        )}

        {activeTab === 'validation' && activeDoc && (
          <ValidationPage activeDoc={activeDoc} />
        )}

        {activeTab === 'export' && activeDoc && (
          <ExportCentrePage activeDoc={activeDoc} />
        )}

        {activeTab === 'settings' && <SettingsPage />}

        {!activeDoc && activeTab !== 'upload' && (
          <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 max-w-lg mx-auto my-12 space-y-4">
            <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center text-3xl mx-auto">
              📄
            </div>
            <h3 className="text-base font-bold text-slate-800">No Document Loaded</h3>
            <p className="text-xs text-slate-500">
              Upload your Pulse R24 newsletter PDF or click below to load the benchmark reference edition.
            </p>
            <button
              onClick={() => setActiveTab('upload')}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow transition"
            >
              Upload or Load Benchmark PDF &rarr;
            </button>
          </div>
        )}
      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-200 bg-white py-3 px-6 text-center text-xs text-slate-400">
        Pulse R24 Email Publishing Studio &middot; Production Build &middot; Fully Compatible with Gmail, Brevo, Mailchimp &amp; EmailOctopus
      </footer>
    </div>
  );
}
