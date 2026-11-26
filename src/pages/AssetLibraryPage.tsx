import { useState, useEffect } from 'react';
import { getAssets } from '../services/api';
import type { DocumentAnalysis, VisualAsset } from '../types/api';

interface AssetLibraryPageProps {
  activeDoc: DocumentAnalysis;
}

export default function AssetLibraryPage({ activeDoc }: AssetLibraryPageProps) {
  const [assets, setAssets] = useState<VisualAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [previewAsset, setPreviewAsset] = useState<VisualAsset | null>(null);

  useEffect(() => {
    setLoading(true);
    getAssets(activeDoc.doc_id)
      .then(setAssets)
      .catch(() => setAssets([]))
      .finally(() => setLoading(false));
  }, [activeDoc.doc_id]);

  const filteredAssets = assets.filter((a) => {
    return selectedType === 'all' || a.asset_type === selectedType;
  });

  const qrAsset = assets.find((a) => a.asset_type === 'qr_code');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-800">Visual Asset Library</h2>
            <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-xs font-bold rounded-full">
              {assets.length} Extracted Assets
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Logos, news card graphics, social media icons, page renders, and OpenCV-decoded QR codes.
          </p>
        </div>

        {/* Filter */}
        <div className="flex rounded-lg border border-slate-200 overflow-hidden bg-white text-xs">
          {['all', 'logo', 'qr_code', 'social_icon', 'news_image', 'embedded_image'].map((t) => (
            <button
              key={t}
              onClick={() => setSelectedType(t)}
              className={`px-3 py-1.5 font-medium capitalize border-l first:border-l-0 border-slate-200 ${
                selectedType === t ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {t.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* QR Code Highlight Card */}
      {qrAsset && (
        <div className="bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 border border-emerald-200 rounded-2xl p-5 flex flex-col md:flex-row items-center gap-5">
          <div className="w-24 h-24 bg-white rounded-xl p-2 border border-emerald-200 shadow-xs shrink-0 flex items-center justify-center">
            <img
              src={qrAsset.rel_path}
              alt="QR Code"
              className="w-full h-full object-contain"
            />
          </div>
          <div className="flex-1 space-y-1 text-center md:text-left">
            <div className="flex items-center gap-2 justify-center md:justify-start">
              <span className="px-2 py-0.5 bg-emerald-600 text-white rounded text-[10px] font-bold uppercase">
                OpenCV Decoded QR Code
              </span>
              <span className="text-xs text-slate-500">Page {qrAsset.page} &middot; {qrAsset.width}×{qrAsset.height} px</span>
            </div>
            <h4 className="text-sm font-bold text-slate-900 mt-1">Digital Intelligence Repository</h4>
            <p className="text-xs text-emerald-900 font-mono break-all bg-emerald-100/70 p-2 rounded-lg border border-emerald-200">
              {qrAsset.qr_decoded_data || 'Decoding...'}
            </p>
          </div>
          {qrAsset.qr_decoded_data && (
            <a
              href={qrAsset.qr_decoded_data}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold rounded-xl shadow-xs shrink-0 transition"
            >
              Test Destination ↗
            </a>
          )}
        </div>
      )}

      {/* Asset Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading asset collection...</div>
      ) : filteredAssets.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredAssets.map((asset) => (
            <div
              key={asset.id}
              onClick={() => setPreviewAsset(asset)}
              className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs hover:shadow-md transition cursor-pointer flex flex-col"
            >
              <div className="h-32 bg-slate-50 flex items-center justify-center p-3 border-b border-slate-100 relative">
                <img
                  src={asset.rel_path}
                  alt={asset.filename}
                  className="max-h-full max-w-full object-contain"
                />
                <span className="absolute top-2 left-2 px-1.5 py-0.5 bg-slate-800/80 text-white text-[9px] font-mono rounded">
                  P{asset.page}
                </span>
                <span className="absolute top-2 right-2 px-1.5 py-0.5 bg-blue-100 text-blue-800 text-[9px] font-bold rounded uppercase">
                  {asset.asset_type.replace('_', ' ')}
                </span>
              </div>
              <div className="p-3 text-[11px] space-y-1 mt-auto">
                <p className="font-semibold text-slate-800 truncate" title={asset.filename}>
                  {asset.filename}
                </p>
                <div className="flex items-center justify-between text-slate-400 text-[10px]">
                  <span>{asset.width} × {asset.height} px</span>
                  <span>{(asset.size_bytes / 1024).toFixed(1)} KB</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center text-xs text-slate-400">
          No assets found in this category.
        </div>
      )}

      {/* Full Preview Modal */}
      {previewAsset && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-800 truncate">{previewAsset.filename}</h3>
                <span className="text-xs text-slate-400">
                  Page {previewAsset.page} &middot; {previewAsset.width} × {previewAsset.height} px &middot; {(previewAsset.size_bytes / 1024).toFixed(1)} KB
                </span>
              </div>
              <button onClick={() => setPreviewAsset(null)} className="text-slate-400 hover:text-slate-600 text-lg">
                ✕
              </button>
            </div>

            <div className="bg-slate-100 rounded-xl p-4 flex items-center justify-center max-h-80 overflow-hidden border border-slate-200">
              <img
                src={previewAsset.rel_path}
                alt={previewAsset.filename}
                className="max-h-72 max-w-full object-contain"
              />
            </div>

            {previewAsset.qr_decoded_data && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-xs">
                <span className="font-bold text-emerald-800 block mb-1">Decoded QR Destination:</span>
                <span className="text-emerald-900 font-mono break-all">{previewAsset.qr_decoded_data}</span>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <a
                href={previewAsset.rel_path}
                download={previewAsset.filename}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-xs transition"
              >
                Download Asset File
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
