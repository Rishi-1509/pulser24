import type {
  BrandingSettings,
  DocumentAnalysis,
  EmailGenerationResponse,
  ExportManifest,
  HealthStatus,
  HyperlinkItem,
  TextBlock,
  ValidationReport,
  VisualAsset,
} from '../types/api';

const API_BASE = '/api';

export async function checkHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Backend unavailable (HTTP ${res.status})`);
  return res.json();
}

export async function uploadPDF(file: File): Promise<DocumentAnalysis> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/pdf/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

export async function analyzeReferencePDF(): Promise<DocumentAnalysis> {
  const res = await fetch(`${API_BASE}/pdf/analyze-reference`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to analyze reference PDF');
  return res.json();
}

export async function listDocuments(): Promise<DocumentAnalysis[]> {
  const res = await fetch(`${API_BASE}/pdf/documents`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
}

export async function getDocument(docId: string): Promise<DocumentAnalysis> {
  const res = await fetch(`${API_BASE}/pdf/documents/${docId}`);
  if (!res.ok) throw new Error('Failed to load document');
  return res.json();
}

export async function getTextBlocks(docId: string): Promise<TextBlock[]> {
  const res = await fetch(`${API_BASE}/pdf/documents/${docId}/text-blocks`);
  if (!res.ok) throw new Error('Failed to load text blocks');
  return res.json();
}

export async function getHyperlinks(docId: string): Promise<HyperlinkItem[]> {
  const res = await fetch(`${API_BASE}/hyperlinks/${docId}`);
  if (!res.ok) throw new Error('Failed to load hyperlinks');
  return res.json();
}

export async function updateHyperlink(
  docId: string,
  linkId: string,
  update: { visible_text?: string; url?: string; mapping_status?: string }
): Promise<HyperlinkItem> {
  const res = await fetch(`${API_BASE}/hyperlinks/${docId}/${linkId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(update),
  });
  if (!res.ok) throw new Error('Failed to update hyperlink');
  return res.json();
}

export async function addHyperlink(docId: string, item: HyperlinkItem): Promise<HyperlinkItem> {
  const res = await fetch(`${API_BASE}/hyperlinks/${docId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item),
  });
  if (!res.ok) throw new Error('Failed to add hyperlink');
  return res.json();
}

export async function getAssets(docId: string): Promise<VisualAsset[]> {
  const res = await fetch(`${API_BASE}/assets/${docId}`);
  if (!res.ok) throw new Error('Failed to load visual assets');
  return res.json();
}

export async function generateEmail(
  docId: string,
  mode: 'faithful' | 'reconstructed',
  includeSourceDirectory = true
): Promise<EmailGenerationResponse> {
  const res = await fetch(`${API_BASE}/generate/${docId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode, include_source_directory: includeSourceDirectory }),
  });
  if (!res.ok) throw new Error('Failed to generate email');
  return res.json();
}

export async function getValidationReport(docId: string): Promise<ValidationReport> {
  const res = await fetch(`${API_BASE}/validation/${docId}`);
  if (!res.ok) throw new Error('Failed to load validation report');
  return res.json();
}

export async function runValidation(docId: string): Promise<ValidationReport> {
  const res = await fetch(`${API_BASE}/validation/${docId}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to run validation');
  return res.json();
}

export async function createExportPackage(docId: string): Promise<ExportManifest> {
  const res = await fetch(`${API_BASE}/export/${docId}/package`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to create export package');
  return res.json();
}

export async function getBrandingSettings(): Promise<BrandingSettings> {
  const res = await fetch(`${API_BASE}/settings/branding`);
  if (!res.ok) throw new Error('Failed to load branding settings');
  return res.json();
}

export async function saveBrandingSettings(settings: BrandingSettings): Promise<BrandingSettings> {
  const res = await fetch(`${API_BASE}/settings/branding`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error('Failed to save branding settings');
  return res.json();
}
