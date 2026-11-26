import type { DocumentAnalysis } from '../types/api';
import type { NavSection } from '../layouts/MainLayout';

interface DashboardProps {
  activeDoc: DocumentAnalysis | null;
  documents: DocumentAnalysis[];
  onSelectDoc: (doc: DocumentAnalysis) => void;
  onNavigate: (section: NavSection) => void;
}

export default function DashboardPage({
  activeDoc,
  documents,
  onSelectDoc,
  onNavigate,
}: DashboardProps) {
  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-2xl p-6 text-white shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-semibold text-xs border border-blue-400/30">
            Professional Email Publishing Studio
          </span>
          <h2 className="text-2xl font-bold mt-2 tracking-tight">
            Pulse R24 Publishing Workspace
          </h2>
          <p className="text-slate-300 text-sm mt-1 max-w-2xl">
            Convert corporate intelligence bulletin PDFs into responsive, email-compatible HTML
            while preserving all embedded sources, tables, logos, and QR codes.
          </p>
        </div>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => onNavigate('upload')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs rounded-xl shadow transition"
          >
            Upload New PDF
          </button>
          {activeDoc && (
            <button
              onClick={() => onNavigate('preview')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs rounded-xl border border-slate-700 transition"
            >
              Open Preview
            </button>
          )}
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Documents Analyzed</span>
          <div className="text-2xl font-bold text-slate-800 mt-1">{documents.length || (activeDoc ? 1 : 0)}</div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Stored in local session</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Total Hyperlinks</span>
          <div className="text-2xl font-bold text-blue-600 mt-1">
            {activeDoc ? activeDoc.total_hyperlinks : 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">
            {activeDoc ? `${activeDoc.mapped_hyperlinks} mapped to anchor text` : 'No active document'}
          </span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Visual Assets</span>
          <div className="text-2xl font-bold text-emerald-600 mt-1">
            {activeDoc ? activeDoc.total_images : 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">
            {activeDoc?.qr_detected ? 'QR Code decoded' : 'Logos and graphics'}
          </span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <span className="text-xs font-semibold text-slate-400 uppercase">Conversion Status</span>
          <div className="text-base font-bold text-slate-800 mt-1.5 flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${activeDoc ? 'bg-emerald-500' : 'bg-slate-300'}`}></span>
            {activeDoc ? 'Ready to Export' : 'Idle'}
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">14-point audit available</span>
        </div>
      </div>

      {/* Workflow Steps Overview */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <h3 className="text-sm font-bold text-slate-800 mb-3">Publishing Workflow</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3 text-center">
          {[
            { step: '1', title: 'Upload', desc: 'Secure PDF parsing', sec: 'upload' as NavSection },
            { step: '2', title: 'Analyze', desc: 'Text & bounding boxes', sec: 'analysis' as NavSection },
            { step: '3', title: 'Map Links', desc: '41 benchmark sources', sec: 'hyperlinks' as NavSection },
            { step: '4', title: 'Assets', desc: 'Logos & QR decode', sec: 'assets' as NavSection },
            { step: '5', title: 'Generate', desc: 'Faithful & Reconstructed', sec: 'designer' as NavSection },
            { step: '6', title: 'Preview', desc: 'Desktop & Mobile', sec: 'preview' as NavSection },
            { step: '7', title: 'Validate & Export', desc: 'Audit & ZIP package', sec: 'export' as NavSection },
          ].map((item) => (
            <button
              key={item.step}
              onClick={() => onNavigate(item.sec)}
              className="p-3 rounded-lg border border-slate-100 hover:border-blue-300 hover:bg-blue-50/40 text-left transition"
            >
              <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center mb-1.5">
                {item.step}
              </div>
              <div className="text-xs font-semibold text-slate-800">{item.title}</div>
              <div className="text-[10px] text-slate-500 leading-tight mt-0.5">{item.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Documents Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-800">Recent Conversions</h3>
          <button
            onClick={() => onNavigate('upload')}
            className="text-xs text-blue-600 font-semibold hover:underline"
          >
            + Process New Document
          </button>
        </div>

        {documents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="p-3">Filename</th>
                  <th className="p-3">Pages</th>
                  <th className="p-3">Links Extracted</th>
                  <th className="p-3">QR Status</th>
                  <th className="p-3">Size</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documents.map((doc) => {
                  const isCurrent = activeDoc?.doc_id === doc.doc_id;
                  return (
                    <tr key={doc.doc_id} className={`hover:bg-slate-50 ${isCurrent ? 'bg-blue-50/40' : ''}`}>
                      <td className="p-3 font-medium text-slate-800 flex items-center gap-2">
                        <span>📄</span>
                        <span className="truncate max-w-xs">{doc.filename}</span>
                        {isCurrent && (
                          <span className="px-1.5 py-0.2 bg-blue-100 text-blue-700 text-[10px] font-bold rounded">
                            Active
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-slate-600">{doc.page_count}</td>
                      <td className="p-3 font-semibold text-blue-600">
                        {doc.total_hyperlinks} ({doc.mapped_hyperlinks} mapped)
                      </td>
                      <td className="p-3">
                        {doc.qr_detected ? (
                          <span className="text-emerald-600 font-medium">✓ Decoded</span>
                        ) : (
                          <span className="text-slate-400">None</span>
                        )}
                      </td>
                      <td className="p-3 text-slate-500">{(doc.file_size_bytes / 1024).toFixed(1)} KB</td>
                      <td className="p-3 text-right space-x-2">
                        <button
                          onClick={() => {
                            onSelectDoc(doc);
                            onNavigate('preview');
                          }}
                          className="text-blue-600 hover:underline font-semibold"
                        >
                          Preview
                        </button>
                        <button
                          onClick={() => {
                            onSelectDoc(doc);
                            onNavigate('hyperlinks');
                          }}
                          className="text-slate-600 hover:underline"
                        >
                          Links
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-slate-400 text-xs">
            No converted documents yet. Upload a PDF or click &ldquo;Process Reference PDF&rdquo; below to start.
          </div>
        )}
      </div>
    </div>
  );
}
