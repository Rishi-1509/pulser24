import type { HealthStatus } from '../types/api';

interface StatusCardProps {
  health: HealthStatus | null;
  error: string | null;
}

export default function StatusCard({ health, error }: StatusCardProps) {
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          <h3 className="text-lg font-semibold text-red-800">Backend Disconnected</h3>
        </div>
        <p className="mt-2 text-sm text-red-600">{error}</p>
        <p className="mt-1 text-xs text-red-400">
          Start the backend server: <code className="bg-red-100 px-1 rounded">uv run uvicorn app.main:app --reload</code>
        </p>
      </div>
    );
  }

  if (!health) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-slate-300 rounded-full animate-pulse" />
          <h3 className="text-lg font-semibold text-slate-600">Connecting to backend...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-3 h-3 bg-emerald-500 rounded-full" />
        <h3 className="text-lg font-semibold text-emerald-800">Backend Connected</h3>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div>
          <span className="text-emerald-600 font-medium">Status</span>
          <p className="text-emerald-800">{health.status}</p>
        </div>
        <div>
          <span className="text-emerald-600 font-medium">Version</span>
          <p className="text-emerald-800">{health.version}</p>
        </div>
        <div>
          <span className="text-emerald-600 font-medium">Service</span>
          <p className="text-emerald-800">{health.service}</p>
        </div>
        <div>
          <span className="text-emerald-600 font-medium">Timestamp</span>
          <p className="text-emerald-800 text-xs font-mono">{health.timestamp}</p>
        </div>
      </div>

      {/* Engine Status */}
      <div className="mt-4 pt-4 border-t border-emerald-200">
        <h4 className="text-sm font-semibold text-emerald-700 mb-2">Processing Engines</h4>
        <div className="flex flex-wrap gap-2">
          {Object.entries(health.engines).map(([engine, status]) => (
            <span
              key={engine}
              className={`text-xs px-2 py-1 rounded font-medium ${
                status === 'ready'
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-amber-100 text-amber-700'
              }`}
            >
              {engine}: {status}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
