import { useState, useRef } from 'react';
import type { ChangeEvent, DragEvent } from 'react';
import { uploadPDF, analyzeReferencePDF } from '../services/api';
import type { DocumentAnalysis } from '../types/api';
import type { NavSection } from '../layouts/MainLayout';

interface UploadPageProps {
  onUploadSuccess: (doc: DocumentAnalysis) => void;
  onNavigate: (section: NavSection) => void;
}

export default function UploadPage({ onUploadSuccess, onNavigate }: UploadPageProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressMsg, setProgressMsg] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await processFile(files[0]);
    }
  };

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF file.');
      return;
    }

    try {
      setError(null);
      setIsProcessing(true);
      setProgressMsg('Uploading document securely to storage...');
      
      const doc = await uploadPDF(file);
      setProgressMsg('Analysis complete! Redirecting...');
      onUploadSuccess(doc);
      onNavigate('analysis');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAnalyzeReference = async () => {
    try {
      setError(null);
      setIsProcessing(true);
      setProgressMsg('Loading & analyzing reference PDF (Issue 359)...');
      const doc = await analyzeReferencePDF();
      setProgressMsg('41 hyperlinks and assets extracted! Redirecting...');
      onUploadSuccess(doc);
      onNavigate('analysis');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h2 className="text-xl font-bold text-slate-800">New PDF Conversion</h2>
        <p className="text-xs text-slate-500 mt-1">
          Upload any Pulse R24 newsletter PDF for automated text, image, hyperlink, and QR extraction.
        </p>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-600 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="font-bold">&times;</button>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-blue-500 bg-blue-50/50 scale-[1.01]'
            : 'border-slate-300 hover:border-blue-400 bg-white hover:bg-slate-50/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto text-2xl mb-4 shadow-xs">
          📄
        </div>

        <h3 className="text-sm font-bold text-slate-800">
          Drop your Pulse R24 PDF here, or <span className="text-blue-600 underline">browse</span>
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Supports up to 50 MB PDFs &middot; High-fidelity vector text & hyperlink preservation
        </p>

        {isProcessing && (
          <div className="mt-6 max-w-xs mx-auto">
            <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-blue-600 animate-pulse w-3/4"></div>
            </div>
            <p className="text-xs font-semibold text-blue-600 mt-2">{progressMsg}</p>
          </div>
        )}
      </div>

      {/* Quick Action: Benchmark Reference PDF */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200/70 rounded-2xl p-5 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="px-2 py-0.5 bg-blue-600 text-white rounded text-[10px] font-bold uppercase tracking-wider">
            Benchmark Test File
          </span>
          <h4 className="text-sm font-bold text-slate-900 mt-1">
            Analyze Reference Issue 359 (25 Nov 2026 Edition)
          </h4>
          <p className="text-xs text-slate-600 mt-0.5">
            Pre-staged test edition containing 3 pages, 41 embedded hyperlinks, news cards, logos, and QR code.
          </p>
        </div>
        <button
          disabled={isProcessing}
          onClick={handleAnalyzeReference}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold text-xs rounded-xl shadow-xs shrink-0 transition"
        >
          {isProcessing ? 'Analyzing...' : 'Load & Analyze Benchmark PDF'}
        </button>
      </div>

      {/* Upload Guidelines */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 text-xs text-slate-600 space-y-2">
        <h5 className="font-bold text-slate-800">Deterministic Extraction Standards</h5>
        <ul className="list-disc pl-5 space-y-1 text-slate-500">
          <li>Original PDF files are preserved byte-for-byte in secure storage for email attachments.</li>
          <li>All 41 embedded hyperlink annotations are mapped with geometric coordinate clipping.</li>
          <li>QR code image is preserved and automatically decoded with OpenCV.</li>
          <li>No synthetic content replacement or arbitrary text rewriting.</li>
        </ul>
      </div>
    </div>
  );
}
