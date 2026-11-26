import { useState } from 'react';
import { createExportPackage } from '../services/api';
import type { DocumentAnalysis, ExportManifest } from '../types/api';

interface ExportCentrePageProps {
  activeDoc: DocumentAnalysis;
}

export default function ExportCentrePage({ activeDoc }: ExportCentrePageProps) {
  const [manifest, setManifest] = useState<ExportManifest | null>(null);
  const [isPackaging, setIsPackaging] = useState(false);
  const [activeEspTab, setActiveEspTab] = useState<'brevo' | 'mailchimp' | 'emailoctopus' | 'gmail'>('brevo');

  const handleCreatePackage = async () => {
    try {
      setIsPackaging(true);
      const res = await createExportPackage(activeDoc.doc_id);
      setManifest(res);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Packaging failed');
    } finally {
      setIsPackaging(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-800">Export Centre & Publishing Hub</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Download final production email files, original PDF attachments, hyperlinks metadata, and ZIP packages.
        </p>
      </div>

      {/* Main Download Package Card */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 text-center md:text-left">
          <span className="px-2.5 py-0.5 bg-blue-500/20 text-blue-300 font-bold text-[10px] uppercase tracking-wider rounded-full border border-blue-400/30">
            Complete Production Archive
          </span>
          <h3 className="text-xl font-bold">
            Pulse_R24_{activeDoc.doc_id}_Email_Package.zip
          </h3>
          <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
            Includes compiled <code className="bg-slate-800 px-1 py-0.5 rounded text-blue-300">email.html</code>,{' '}
            <code className="bg-slate-800 px-1 py-0.5 rounded text-blue-300">email.txt</code>, original PDF,{' '}
            supporting image assets, 41-link JSON/CSV registries, and audit report.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 shrink-0">
          <button
            onClick={handleCreatePackage}
            disabled={isPackaging}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-lg transition"
          >
            {isPackaging ? 'Compiling Package...' : '1. Generate ZIP Package'}
          </button>

          <a
            href={`/api/export/${activeDoc.doc_id}/download-zip`}
            download
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-lg text-center transition flex items-center justify-center gap-1.5"
          >
            <span>📦</span> Download ZIP Archive
          </a>
        </div>
      </div>

      {manifest && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-1">
          <span className="font-bold text-emerald-800">✓ Package Generated Successfully</span>
          <div className="flex gap-4 text-emerald-900 text-[11px]">
            <span>Included Assets: {manifest.assets_included}</span>
            <span>Archive: {manifest.zip_archive}</span>
          </div>
        </div>
      )}

      {/* Individual File Artifact Downloads */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">
          Individual File Artifacts
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {[
            {
              name: 'email.html',
              label: 'Final Responsive HTML Email',
              desc: 'Table layout, inline CSS, mapped links',
              href: `/api/export/${activeDoc.doc_id}/email.html`,
              icon: '🌐',
            },
            {
              name: 'email.txt',
              label: 'Plain-Text Alternative',
              desc: 'Accessible fallback text with all sources',
              href: `/api/export/${activeDoc.doc_id}/email.txt`,
              icon: '📝',
            },
            {
              name: 'original.pdf',
              label: 'Original Reference PDF',
              desc: 'Preserved for direct email attachment',
              href: `/api/export/${activeDoc.doc_id}/original.pdf`,
              icon: '📎',
            },
            {
              name: 'hyperlinks.csv',
              label: 'Hyperlinks Spreadsheet',
              desc: 'All 41 extracted sources with anchors',
              href: `/api/hyperlinks/${activeDoc.doc_id}/export/csv`,
              icon: '📊',
            },
            {
              name: 'hyperlinks.json',
              label: 'Hyperlinks Machine Registry',
              desc: 'Full coordinate & bounding box JSON',
              href: `/api/hyperlinks/${activeDoc.doc_id}/export/json`,
              icon: '📜',
            },
            {
              name: 'validation-report.json',
              label: '14-Point Pre-Flight Audit',
              desc: 'JSON audit record for compliance',
              href: `/api/export/${activeDoc.doc_id}/validation-report.json`,
              icon: '🛡️',
            },
          ].map((f) => (
            <div
              key={f.name}
              className="p-3.5 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/20 transition flex items-start justify-between gap-3"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span>{f.icon}</span>
                  <span className="font-bold text-slate-800 text-xs">{f.name}</span>
                </div>
                <div className="text-[11px] font-semibold text-slate-600 mt-1">{f.label}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">{f.desc}</div>
              </div>
              <a
                href={f.href}
                download
                className="px-2.5 py-1 bg-slate-100 hover:bg-blue-600 hover:text-white rounded text-[11px] font-semibold text-slate-700 shrink-0 transition"
              >
                Download
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* ESP & Gmail Import Instructions */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Email Client & Platform Import Instructions
          </h4>

          {/* ESP Switcher Tabs */}
          <div className="flex rounded-lg border border-slate-200 overflow-hidden text-xs">
            {(['brevo', 'mailchimp', 'emailoctopus', 'gmail'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveEspTab(tab)}
                className={`px-3 py-1 font-medium capitalize border-l first:border-l-0 border-slate-200 ${
                  activeEspTab === tab ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                {tab === 'gmail' ? 'Gmail Workflow' : tab}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700 leading-relaxed">
          {activeEspTab === 'brevo' && (
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900">Importing into Brevo (formerly Sendinblue):</h5>
              <ol className="list-decimal pl-5 space-y-1">
                <li>Log in to Brevo and click <strong>Campaigns &gt; Create an email campaign</strong>.</li>
                <li>In the <strong>Design</strong> section, select <strong>&ldquo;Code your own&rdquo;</strong> &rarr; <strong>&ldquo;Paste your code&rdquo;</strong>.</li>
                <li>Copy the entire content of <code className="bg-slate-200 px-1 py-0.5 rounded">email.html</code> and paste it into the editor.</li>
                <li>In the <strong>Advanced Options &gt; Attachments</strong>, upload <code className="bg-slate-200 px-1 py-0.5 rounded">original.pdf</code> so recipients can also download the reference PDF.</li>
                <li>Send a test email to verify Gmail and Outlook rendering.</li>
              </ol>
            </div>
          )}

          {activeEspTab === 'mailchimp' && (
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900">Importing into Mailchimp:</h5>
              <ol className="list-decimal pl-5 space-y-1">
                <li>Go to <strong>Campaigns &gt; Create Campaign &gt; Regular Email</strong>.</li>
                <li>In the <strong>Content</strong> step, choose <strong>&ldquo;Code your own&rdquo;</strong> &rarr; <strong>&ldquo;Paste in code&rdquo;</strong>.</li>
                <li>Paste <code className="bg-slate-200 px-1 py-0.5 rounded">email.html</code>.</li>
                <li>Upload extracted logo/image assets to your Mailchimp Content Studio or keep image links pointing to your public asset host.</li>
                <li>Attach the original PDF or link it directly in the header banner.</li>
              </ol>
            </div>
          )}

          {activeEspTab === 'emailoctopus' && (
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900">Importing into EmailOctopus:</h5>
              <ol className="list-decimal pl-5 space-y-1">
                <li>Click <strong>Campaigns &gt; Create campaign</strong>.</li>
                <li>Select the <strong>&ldquo;Import HTML&rdquo;</strong> template option.</li>
                <li>Paste or upload <code className="bg-slate-200 px-1 py-0.5 rounded">email.html</code>.</li>
                <li>All 41 hyperlinks and table structures will be preserved automatically.</li>
              </ol>
            </div>
          )}

          {activeEspTab === 'gmail' && (
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900">Direct Gmail Manual Workflow:</h5>
              <ol className="list-decimal pl-5 space-y-1">
                <li>Open <code className="bg-slate-200 px-1 py-0.5 rounded">email.html</code> in Google Chrome or any modern browser.</li>
                <li>Press <kbd className="bg-slate-200 px-1 rounded font-mono">Ctrl + A</kbd> (Select All), then <kbd className="bg-slate-200 px-1 rounded font-mono">Ctrl + C</kbd> (Copy).</li>
                <li>In your Gmail compose window, click the email body and press <kbd className="bg-slate-200 px-1 rounded font-mono">Ctrl + V</kbd> (Paste).</li>
                <li>Gmail will paste the rich, responsive table email with all formatted text, colors, and active clickable hyperlinks intact.</li>
                <li>Attach <code className="bg-slate-200 px-1 py-0.5 rounded">original.pdf</code> using the paperclip attachment icon.</li>
                <li>Send directly to your distribution list!</li>
              </ol>
              <p className="text-[11px] text-blue-600 font-medium mt-2">
                Note: In future versions, this step will be automated via the Gmail API draft integration.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
