import type { HealthStatus } from '../types/api';
import StatusCard from '../components/StatusCard';

interface HomePageProps {
  health: HealthStatus | null;
  error: string | null;
}

export default function HomePage({ health, error }: HomePageProps) {
  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="text-center py-8">
        <h2 className="text-3xl font-bold text-slate-800 mb-3">
          PDF → Email-Ready HTML
        </h2>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto">
          Convert Pulse R24 PDF newsletters into responsive, email-compatible HTML
          while preserving content, formatting, images, and links.
        </p>
      </div>

      {/* Backend Connection Status */}
      <StatusCard health={health} error={error} />

      {/* Placeholder Workflow Steps */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            step: '1',
            title: 'Upload PDF',
            desc: 'Upload your Pulse R24 newsletter PDF for processing.',
            status: 'Pending implementation',
          },
          {
            step: '2',
            title: 'Extract & Process',
            desc: 'Extract text, images, tables, links, QR codes, and logos.',
            status: 'Pending implementation',
          },
          {
            step: '3',
            title: 'Generate HTML',
            desc: 'Generate responsive, email-client-compatible HTML output.',
            status: 'Pending implementation',
          },
        ].map((item) => (
          <div
            key={item.step}
            className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm"
          >
            <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-lg font-bold text-slate-400">{item.step}</span>
            </div>
            <h3 className="text-lg font-semibold text-slate-700 mb-2">{item.title}</h3>
            <p className="text-sm text-slate-500 mb-3">{item.desc}</p>
            <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-1 rounded">
              {item.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
