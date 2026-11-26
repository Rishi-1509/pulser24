import { useState, useEffect } from 'react';
import { runValidation, getValidationReport } from '../services/api';
import type { DocumentAnalysis, ValidationReport } from '../types/api';

interface ValidationPageProps {
  activeDoc: DocumentAnalysis;
}

export default function ValidationPage({ activeDoc }: ValidationPageProps) {
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'passed' | 'warning' | 'failed'>('all');

  const executeValidation = () => {
    setLoading(true);
    runValidation(activeDoc.doc_id)
      .then(setReport)
      .catch(() => setReport(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    setLoading(true);
    getValidationReport(activeDoc.doc_id)
      .then(setReport)
      .catch(() => executeValidation())
      .finally(() => setLoading(false));
  }, [activeDoc.doc_id]);

  const filteredItems = report?.items.filter((item) => {
    return filter === 'all' || item.status === filter;
  });

  const downloadReportJson = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pulse_${activeDoc.doc_id}_validation_report.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-800">Pre-Flight Validation Engine</h2>
            {report && (
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                  report.overall_status === 'passed'
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : report.overall_status === 'warning'
                    ? 'bg-amber-100 text-amber-800 border border-amber-300'
                    : 'bg-red-100 text-red-800 border border-red-300'
                }`}
              >
                Overall: {report.overall_status}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            14 automated structural, hyperlink, asset, and email compatibility audits before export.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={downloadReportJson}
            disabled={!report}
            className="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-50 disabled:opacity-50 text-slate-700 text-xs font-medium rounded-lg shadow-xs transition"
          >
            📥 Download Report JSON
          </button>
          <button
            onClick={executeValidation}
            disabled={loading}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-medium rounded-lg shadow-xs transition"
          >
            {loading ? 'Auditing...' : 'Re-Run All Checks'}
          </button>
        </div>
      </div>

      {/* Summary Scorecard */}
      {report && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Total Checks</span>
            <div className="text-2xl font-bold text-slate-800 mt-1">{report.total_checks}</div>
            <span className="text-[11px] text-slate-500">Comprehensive audit suite</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Passed</span>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{report.passed_count}</div>
            <span className="text-[11px] text-emerald-700 font-medium">
              {((report.passed_count / report.total_checks) * 100).toFixed(0)}% passing rate
            </span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Warnings</span>
            <div className="text-2xl font-bold text-amber-600 mt-1">{report.warning_count}</div>
            <span className="text-[11px] text-amber-700">Non-blocking notices</span>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
            <span className="text-[10px] font-bold text-slate-400 uppercase">Failed</span>
            <div className="text-2xl font-bold text-red-600 mt-1">{report.failed_count}</div>
            <span className="text-[11px] text-slate-500">
              {report.failed_count === 0 ? '✓ Zero blocking errors' : 'Requires correction'}
            </span>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex rounded-lg border border-slate-200 overflow-hidden bg-white w-fit text-xs">
        {(['all', 'passed', 'warning', 'failed'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`px-3 py-1.5 font-medium capitalize border-l first:border-l-0 border-slate-200 ${
              filter === t ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Validation Checklist Items */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Running validation audit...</div>
      ) : filteredItems && filteredItems.length > 0 ? (
        <div className="space-y-3">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className={`p-4 rounded-xl border shadow-xs transition bg-white flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                item.status === 'passed'
                  ? 'border-emerald-200/80 bg-emerald-50/10'
                  : item.status === 'warning'
                  ? 'border-amber-200 bg-amber-50/20'
                  : 'border-red-200 bg-red-50/30'
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 ${
                      item.status === 'passed'
                        ? 'bg-emerald-500'
                        : item.status === 'warning'
                        ? 'bg-amber-500'
                        : 'bg-red-500'
                    }`}
                  >
                    {item.status === 'passed' ? '✓' : item.status === 'warning' ? '!' : '✕'}
                  </span>
                  <h4 className="text-sm font-bold text-slate-800">{item.title}</h4>
                  <span className="px-1.5 py-0.2 bg-slate-100 text-slate-500 text-[10px] font-mono rounded capitalize">
                    {item.category}
                  </span>
                </div>
                <p className="text-xs text-slate-600 pl-7">{item.message}</p>
                {item.recommendation && (
                  <p className="text-[11px] text-amber-700 pl-7 font-medium">
                    Recommendation: {item.recommendation}
                  </p>
                )}
              </div>

              <div className="shrink-0 pl-7 md:pl-0">
                <span
                  className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                    item.status === 'passed'
                      ? 'bg-emerald-100 text-emerald-800'
                      : item.status === 'warning'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {item.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center text-xs text-slate-400">
          No validation items match the filter.
        </div>
      )}
    </div>
  );
}
