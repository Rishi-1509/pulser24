export interface BoundingBox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface TextBlock {
  id: string;
  page: number;
  text: string;
  font_name: string | null;
  font_size: number;
  is_bold: boolean;
  is_headline: boolean;
  bbox: BoundingBox;
  block_type: string;
}

export interface HyperlinkItem {
  id: string;
  page: number;
  url: string;
  visible_text: string;
  bbox: BoundingBox;
  link_type: string;
  mapping_status: 'mapped' | 'unmapped' | 'manual' | 'flagged';
  context_text: string;
  is_verified?: boolean | null;
}

export interface VisualAsset {
  id: string;
  page: number;
  filename: string;
  rel_path: string;
  asset_type: 'logo' | 'qr_code' | 'social_icon' | 'news_image' | 'page_render' | 'embedded_image';
  width: number;
  height: number;
  size_bytes: number;
  qr_decoded_data?: string | null;
  extraction_status: string;
}

export interface BrandingSettings {
  app_title: string;
  bulletin_name: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  font_family: string;
  max_email_width: number;
  social_links: Record<string, string>;
  ai_declaration: string;
  institutional_attribution: string;
}

export interface DocumentAnalysis {
  doc_id: string;
  filename: string;
  file_size_bytes: number;
  page_count: number;
  title: string | null;
  author: string | null;
  created_at: string;
  page_dimensions: Array<{ page: number; width: number; height: number }>;
  total_hyperlinks: number;
  mapped_hyperlinks: number;
  total_images: number;
  qr_detected: boolean;
  qr_content: string | null;
  text_blocks_count: number;
}

export interface EmailGenerationResponse {
  mode: string;
  html_content: string;
  plain_text_content: string;
  total_links_included: number;
  character_count: number;
  generated_at: string;
}

export interface ValidationItem {
  id: string;
  title: string;
  category: string;
  status: 'passed' | 'warning' | 'failed';
  message: string;
  affected_page?: number | null;
  affected_element?: string | null;
  recommendation?: string | null;
}

export interface ValidationReport {
  doc_id: string;
  timestamp: string;
  overall_status: 'passed' | 'warning' | 'failed';
  total_checks: number;
  passed_count: number;
  warning_count: number;
  failed_count: number;
  items: ValidationItem[];
}

export interface ExportManifest {
  doc_id: string;
  timestamp: string;
  html_file: string;
  plain_text_file: string;
  original_pdf: string;
  hyperlinks_json: string;
  hyperlinks_csv: string;
  validation_report_json: string;
  zip_archive: string;
  assets_included: number;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  engines: Record<string, string>;
}
