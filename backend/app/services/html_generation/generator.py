"""
Pulse R24 Faithful Email Generator
Matches the exact PDF layout: white cards, inline severity badges,
proper Watch List / Radar tables, CAREVIA block, footer with logos.
"""

import html
import re
from app.models.schemas import BrandingSettings, HyperlinkItem, TextBlock, VisualAsset
from app.services.pdf_extraction.layout_analyzer import get_layout_and_colors


class EmailGeneratorService:
    # ── Colour palette (from PDF drawings) ──────────────────────────
    NAVY   = "#01093d"
    CRIMSON= "#7e1015"
    AMBER  = "#e8b31b"
    ORANGE = "#df6a12"
    GREEN  = "#3c8b57"
    DARK   = "#1b1d24"
    WHITE  = "#ffffff"
    LGRAY  = "#f5f6fa"
    BORDER = "#d1d5db"

    def __init__(
        self,
        doc_id: str,
        text_blocks: list[TextBlock],
        hyperlinks: list[HyperlinkItem],
        assets: list[VisualAsset],
        page_images: list[str],
        branding: BrandingSettings | None = None,
        base_asset_url: str = "http://localhost:8000",
        pdf_path: str | None = None,
        embed_base64: bool = True,
    ):
        self.doc_id = doc_id
        self.text_blocks = text_blocks
        self.hyperlinks = hyperlinks
        self.assets = assets
        self.page_images = page_images
        self.branding = branding or BrandingSettings()
        self.base = base_asset_url.rstrip("/")
        self.pdf_path = pdf_path
        self.embed_base64 = embed_base64

        # Dynamic layout & color extraction from uploaded PDF
        self.dynamic_glance = []
        self.dynamic_card_bgs = {}
        if self.pdf_path:
            try:
                self.dynamic_glance, self.dynamic_card_bgs = get_layout_and_colors(self.pdf_path)
            except Exception:
                pass

        # Helpers
        self.links_by_page: dict[int, list[HyperlinkItem]] = {}
        for lnk in self.hyperlinks:
            self.links_by_page.setdefault(lnk.page, []).append(lnk)

    def _get_asset_src(self, asset: VisualAsset | None, fallback_path: str = "") -> str:
        """Returns base64 data URI if embed_base64 is True and file exists, otherwise hosted URL."""
        if not asset and not fallback_path:
            return ""
        rel = asset.rel_path if asset else fallback_path
        if self.embed_base64 and rel:
            from pathlib import Path
            import base64
            fname = Path(rel).name
            candidates = [
                Path(f"storage/extracted/{self.doc_id}/assets") / fname,
                Path(f"backend/storage/extracted/{self.doc_id}/assets") / fname,
                Path(f"storage/extracted/{self.doc_id}") / fname,
                Path(f"backend/storage/extracted/{self.doc_id}") / fname,
            ]
            for p in candidates:
                if p.exists():
                    try:
                        b64 = base64.b64encode(p.read_bytes()).decode('ascii')
                        mime = "image/png" if fname.endswith('.png') else "image/jpeg"
                        return f"data:{mime};base64,{b64}"
                    except Exception:
                        pass
        return f"{self.base}{rel}"

    # ═══════════════════════════════════════════════════════════════
    # PUBLIC – MODE A : Faithful (page renders + interactive overlay + source index)
    # ═══════════════════════════════════════════════════════════════
    def generate_faithful_mode(self, max_width: int = 680) -> tuple[str, str]:
        # Discover rendered page_*.png on disk if needed
        page_imgs = list(self.page_images)
        from pathlib import Path
        import base64
        
        candidates_dir = [
            Path(f"storage/extracted/{self.doc_id}"),
            Path(f"backend/storage/extracted/{self.doc_id}"),
            Path(__file__).resolve().parent.parent.parent.parent / "storage" / "extracted" / self.doc_id,
        ]
        
        if not page_imgs:
            for c in candidates_dir:
                if c.exists():
                    found = sorted([str(p) for p in c.glob("page_*.png")])
                    if found:
                        page_imgs = found
                        break

        page_rows = []
        num_pages = len(page_imgs) if page_imgs else 3
        for idx in range(num_pages):
            pno = idx + 1
            
            # Embed image as base64 data URI if embed_base64 is enabled, otherwise use API url
            src = f"{self.base}/api/pages/{self.doc_id}/page_{pno}.png"
            if self.embed_base64:
                file_candidates = [
                    Path(f"storage/extracted/{self.doc_id}/page_{pno}.png"),
                    Path(f"backend/storage/extracted/{self.doc_id}/page_{pno}.png"),
                    Path(__file__).resolve().parent.parent.parent.parent / "storage" / "extracted" / self.doc_id / f"page_{pno}.png",
                ]
                if page_imgs and idx < len(page_imgs):
                    file_candidates.insert(0, Path(page_imgs[idx]))
                    
                for p in file_candidates:
                    if p.exists():
                        try:
                            b64 = base64.b64encode(p.read_bytes()).decode('ascii')
                            src = f"data:image/png;base64,{b64}"
                            break
                        except Exception:
                            pass

            p_links = self.links_by_page.get(pno, [])
            
            # Use original PDF dimensions if available, default to A4 (595 x 842)
            pw = 595.0
            ph = 842.0
            
            # HTML image map areas
            map_name = f"pdf_map_{self.doc_id}_{pno}"
            areas = []
            overlays = []
            
            for lnk in p_links:
                u = html.escape(lnk.url)
                t = html.escape(self._clean_title(lnk.visible_text, lnk.url))
                
                # Coordinates
                bx0, by0, bx1, by1 = lnk.bbox.x0, lnk.bbox.y0, lnk.bbox.x1, lnk.bbox.y1
                
                # Image map coordinates (scaled to max_width)
                scale = max_width / pw
                mx0 = round(bx0 * scale)
                my0 = round(by0 * scale)
                mx1 = round(bx1 * scale)
                my1 = round(by1 * scale)
                areas.append(f'<area shape="rect" coords="{mx0},{my0},{mx1},{my1}" href="{u}" target="_blank" rel="noopener noreferrer" alt="{t}" title="{t}" />')
                
                # Absolute percentage overlay for responsive clients
                left = round(bx0 / pw * 100, 3)
                top = round(by0 / ph * 100, 3)
                w_pct = round((bx1 - bx0) / pw * 100, 3)
                h_pct = round((by1 - by0) / ph * 100, 3)
                overlays.append(
                    f'<a href="{u}" target="_blank" rel="noopener noreferrer" title="{t}" '
                    f'style="position:absolute;left:{left}%;top:{top}%;width:{w_pct}%;height:{h_pct}%;'
                    f'display:block;text-decoration:none;z-index:10;-webkit-tap-highlight-color:rgba(0,0,0,0);">'
                    f'<span style="display:none;">{t}</span></a>'
                )

            map_html = f'<map name="{map_name}">\n              ' + '\n              '.join(areas) + '\n            </map>' if areas else ''
            overlay_html = '\n              '.join(overlays)

            page_rows.append(f"""
            <tr>
              <td align="center" style="padding:0;background:#ffffff;border-bottom:2px solid {self.BORDER};line-height:0;font-size:0;">
                <div style="position:relative;width:100%;max-width:{max_width}px;margin:0 auto;display:inline-block;">
                  <img src="{src}" alt="Pulse R24 Page {pno}" width="{max_width}" usemap="#{map_name}"
                       style="display:block;width:100%;max-width:{max_width}px;height:auto;border:0;outline:none;" />
                  {overlay_html}
                </div>
                {map_html}
              </td>
            </tr>""")

        source_sections = []
        for pno in sorted(self.links_by_page):
            p_links = self.links_by_page[pno]
            items = []
            for lnk in p_links:
                t = html.escape(self._clean_title(lnk.visible_text, lnk.url))
                u = html.escape(lnk.url)
                items.append(f"""
                <li style="margin-bottom:6px;line-height:1.4;">
                  <a href="{u}" target="_blank" rel="noopener noreferrer"
                     style="color:#1a56db;font-weight:600;text-decoration:underline;font-size:12px;">{t}</a>
                  <div style="color:#6b7280;font-size:10px;word-break:break-all;margin-top:1px;">{u}</div>
                </li>""")
            source_sections.append(f"""
            <div style="margin-bottom:18px;">
              <div style="font-size:11px;font-weight:800;color:{self.NAVY};text-transform:uppercase;
                          border-bottom:2px solid {self.BORDER};padding-bottom:3px;margin-bottom:8px;">
                Page {pno} Sources ({len(p_links)} Links)
              </div>
              <ul style="margin:0;padding-left:16px;font-size:12px;color:#374151;">{''.join(items)}</ul>
            </div>""")

        b = self.branding
        html_out = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Pulse R24 – Faithful Edition</title>
  <style>body,table,td,a{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}}
  body{{margin:0;padding:0;background:#e5e7eb;}}
  img{{border:0;height:auto;line-height:100%;}}
  @media(max-width:680px){{.ec{{width:100%!important;}}}}</style>
</head>
<body style="margin:0;padding:0;background:#e5e7eb;">
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="background:#e5e7eb;">
  <tr><td align="center" style="padding:16px 8px;">
    <table border="0" cellpadding="0" cellspacing="0" width="{max_width}" class="ec"
           style="background:#ffffff;border-radius:6px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);">
      <tr><td bgcolor="{self.NAVY}" style="padding:12px 20px;">
        <span style="color:#fff;font-size:18px;font-weight:900;letter-spacing:.5px;">PULSE-R24</span>
        <span style="color:#93c5fd;font-size:11px;margin-left:8px;">FAITHFUL VISUAL EDITION</span>
      </td></tr>
      {''.join(page_rows)}
      <tr><td style="padding:20px;background:{self.LGRAY};border-top:2px solid {self.BORDER};">
        <div style="font-size:13px;font-weight:800;color:{self.NAVY};margin-bottom:12px;">
          Hyperlink Directory — {len(self.hyperlinks)} Verified Sources
        </div>
        {''.join(source_sections)}
      </td></tr>
      {self._footer_row(b)}
    </table>
  </td></tr>
</table>
</body></html>"""
        return html_out, self._plain_text(b)
        return html_out, self._plain_text(b)

    # ═══════════════════════════════════════════════════════════════
    # PUBLIC – MODE B : Reconstructed (matches PDF visually)
    # ═══════════════════════════════════════════════════════════════
    def generate_reconstructed_mode(self, max_width: int = 680) -> tuple[str, str]:
        is_pulse = any("DAILY INTEL" in b.text.upper() or "PULSE" in b.text.upper()
                       for b in self.text_blocks)
        if not is_pulse or len(self.text_blocks) < 10:
            return self._generic_html(max_width)
        return self._pulse_html(max_width)

    # ═══════════════════════════════════════════════════════════════
    # GENERIC fallback for non-Pulse PDFs
    # ═══════════════════════════════════════════════════════════════
    def _generic_html(self, max_width: int) -> tuple[str, str]:
        b = self.branding
        cards = []
        for pno in sorted({blk.page for blk in self.text_blocks}):
            p_blocks = sorted([x for x in self.text_blocks if x.page == pno],
                              key=lambda x: x.bbox.y0)
            p_links  = self.links_by_page.get(pno, [])
            rows = []
            for blk in p_blocks:
                txt = blk.text.strip()
                if not txt:
                    continue
                if blk.is_headline or blk.font_size >= 13:
                    rows.append(f'<h2 style="margin:0 0 8px 0;color:{self.NAVY};font-size:15px;font-weight:700;">{html.escape(txt)}</h2>')
                else:
                    rows.append(f'<p style="margin:0 0 6px 0;color:#374151;font-size:12px;line-height:1.6;">{html.escape(txt)}</p>')
            link_items = " &middot; ".join(
                f'<a href="{html.escape(lnk.url)}" target="_blank" rel="noopener noreferrer" '
                f'style="color:#1a56db;font-weight:600;text-decoration:underline;font-size:11px;">'
                f'{html.escape(self._clean_title(lnk.visible_text, lnk.url))}</a>'
                for lnk in p_links)
            links_html = f'<div style="margin-top:10px;padding-top:6px;border-top:1px dotted {self.BORDER};font-size:11px;"><strong style="color:#6b7280;">Sources:</strong> <span style="margin-left:4px;">{link_items}</span></div>' if link_items else ""
            cards.append(f"""
            <table border="0" cellpadding="0" cellspacing="0" width="100%"
                   style="background:#fff;border:1px solid {self.BORDER};border-top:3px solid {self.NAVY};
                          border-radius:5px;margin-bottom:14px;">
              <tr><td style="padding:14px 16px;">{''.join(rows)}{links_html}</td></tr>
            </table>""")

        html_out = self._wrap(max_width, ''.join(cards), b)
        return html_out, self._plain_text(b)

    # ═══════════════════════════════════════════════════════════════
    # MAIN Pulse R24 Reconstructed renderer
    # ═══════════════════════════════════════════════════════════════
    def _pulse_html(self, max_width: int) -> tuple[str, str]:
        b = self.branding

        # ── Header banner image ──────────────────────────────────────
        banner = next((a for a in self.assets if a.page == 1 and a.asset_type == "logo"), None)
        banner_html = ""
        if banner:
            banner_src = self._get_asset_src(banner)
            banner_html = f"""
            <tr>
              <td align="center" style="padding:0;background:#fff;">
                <img src="{banner_src}" alt="Pulse R24"
                     width="{max_width}" style="display:block;width:100%;max-width:{max_width}px;height:auto;border:0;" />
              </td>
            </tr>"""

        # ── Sub-banner description row ───────────────────────────────
        desc_block = next((b2 for b2 in self.text_blocks
                           if b2.page == 1 and "security pulse" in b2.text.lower()), None)
        desc_text  = desc_block.text.replace("\n", " ").strip() if desc_block else \
            "PULSE-R24 — Where the nation's security pulse meets insight."

        # ── Issue sub-header ─────────────────────────────────────────
        date_block  = next((b2 for b2 in self.text_blocks if "Daily Intel Pulse" in b2.text), None)
        issue_block = next((b2 for b2 in self.text_blocks if "ISSP_RRUPY" in b2.text), None)
        date_text   = date_block.text.strip()  if date_block  else "Daily Intel Pulse"
        issue_text  = issue_block.text.strip() if issue_block else ""

        # ── Today at a Glance ────────────────────────────────────────
        glance_html = self._glance_grid()

        # ── PAGE 1 articles ──────────────────────────────────────────
        p1_lead  = self._card(1, 270, 500)
        p1_left  = self._card(1, 500, 820, x_max=290)
        p1_right = self._card(1, 500, 820, x_min=290)

        # ── PAGE 2 articles ──────────────────────────────────────────
        p2_top   = self._card(2,  40, 250)
        p2_ml    = self._card(2, 250, 530, x_max=290)
        p2_mr    = self._card(2, 250, 530, x_min=290)
        p2_bl    = self._card(2, 530, 820, x_max=290)
        p2_br    = self._card(2, 530, 820, x_min=290)

        # ── PAGE 3 ───────────────────────────────────────────────────
        p3_watchlist = self._watchlist_table()
        p3_radar     = self._radar_table()
        p3_desk      = self._desk_coverage()
        p3_carevia   = self._carevia_block()
        p3_footer    = self._full_footer(b)

        # ── Background colors detected dynamically from PDF drawings ─
        bgs = self.dynamic_card_bgs or {}
        bg_p1_lead  = bgs.get('p1_lead',  self.WHITE)
        bg_p1_left  = bgs.get('p1_left',  self.NAVY)
        bg_p1_right = bgs.get('p1_right', self.WHITE)
        bg_p2_top   = bgs.get('p2_top',   self.NAVY)
        bg_p2_ml    = bgs.get('p2_ml',    self.NAVY)
        bg_p2_mr    = bgs.get('p2_mr',    self.WHITE)
        bg_p2_bl    = bgs.get('p2_bl',    self.NAVY)
        bg_p2_br    = bgs.get('p2_br',    self.WHITE)

        # ── Render article cards ──────────────────────────────────────
        def article_card(card, bg_color=None, border_color=None):
            if not card:
                return ""
            bg = bg_color or self.WHITE
            bc = border_color or (self.ORANGE if bg == self.WHITE else "#2e6fb3")
            return self._render_card(card, bg_color=bg, border_color=bc)

        # ─────────────────────────────────────────────────────────────
        # ASSEMBLE HTML
        # ─────────────────────────────────────────────────────────────
        html_out = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>PULSE-R24 Daily Intel Pulse</title>
  <style type="text/css">
    body,table,td,a{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}}
    table,td{{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;}}
    img{{border:0;height:auto;line-height:100%;outline:none;text-decoration:none;}}
    body{{margin:0;padding:0;background:#e5e7eb;font-family:Georgia,'Times New Roman',serif;}}
    .sans{{font-family:Arial,Helvetica,sans-serif!important;}}
    @media screen and (max-width:680px){{
      .ec{{width:100%!important;max-width:100%!important;}}
      .col{{display:block!important;width:100%!important;box-sizing:border-box!important;padding-right:0!important;padding-left:0!important;}}
      .gc{{display:block!important;width:33%!important;}}
    }}
  </style>
</head>
<body style="margin:0;padding:0;background:#e5e7eb;">
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="background:#e5e7eb;">
<tr><td align="center" style="padding:16px 8px;">
<table border="0" cellpadding="0" cellspacing="0" width="{max_width}" class="ec"
       style="background:#fff;border-radius:4px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.12);">

  <!-- ░░ BANNER IMAGE ░░ -->
  {banner_html}

  <!-- ░░ DESCRIPTION ROW ░░ -->
  <tr>
    <td style="background:#f9fafb;padding:8px 20px;border-bottom:1px solid {self.BORDER};">
      <span class="sans" style="font-size:11px;color:{self.DARK};line-height:1.4;">{html.escape(desc_text)}</span>
    </td>
  </tr>

  <!-- ░░ ISSUE HEADER ░░ -->
  <tr>
    <td style="padding:10px 20px 6px 20px;background:#fff;border-bottom:2px solid {self.DARK};">
      <table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
        <td valign="top" width="58%">
          <div style="font-size:17px;font-weight:800;color:{self.CRIMSON};font-family:Georgia,'Times New Roman',serif;line-height:1.2;">
            {html.escape(date_text)}
          </div>
          <div class="sans" style="font-size:10px;color:{self.DARK};margin-top:2px;font-weight:600;">
            {html.escape(issue_text)}
          </div>
        </td>
        <td valign="top" align="right" width="42%">
          <div style="font-size:14px;font-weight:800;color:{self.CRIMSON};font-family:Georgia,'Times New Roman',serif;line-height:1.3;text-align:right;">
            Ranked by incident impact timeline<br/>across Tier-1 cities
          </div>
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- ░░ TODAY AT A GLANCE ░░ -->
  {glance_html}

  <!-- ░░ PAGE 1 LEAD STORY ░░ -->
  <tr>
    <td style="padding:18px 20px 10px 20px;background:#fff;">
      {article_card(p1_lead, bg_p1_lead, self.NAVY)}
    </td>
  </tr>

  <!-- ░░ PAGE 1 2-COLUMN ░░ -->
  <tr>
    <td style="padding:0 20px 18px 20px;background:#fff;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
        <td class="col" valign="top" width="48%" style="padding-right:8px;">
          {article_card(p1_left, bg_p1_left, self.NAVY)}
        </td>
        <td class="col" valign="top" width="52%" style="padding-left:8px;">
          {article_card(p1_right, bg_p1_right, self.NAVY)}
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- ░░ PAGE 2 DIVIDER ░░ -->
  <tr>
    <td style="padding:0;background:{self.LGRAY};border-top:3px solid {self.BORDER};">&nbsp;</td>
  </tr>

  <!-- ░░ PAGE 2 TOP (FULL WIDTH CYBER) ░░ -->
  <tr>
    <td style="padding:18px 20px 10px 20px;background:{self.LGRAY};">
      {article_card(p2_top, bg_p2_top, self.ORANGE)}
    </td>
  </tr>

  <!-- ░░ PAGE 2 MID 2-COLUMN ░░ -->
  <tr>
    <td style="padding:0 20px 10px 20px;background:{self.LGRAY};">
      <table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
        <td class="col" valign="top" width="48%" style="padding-right:8px;">
          {article_card(p2_ml, bg_p2_ml, self.NAVY)}
        </td>
        <td class="col" valign="top" width="52%" style="padding-left:8px;">
          {article_card(p2_mr, bg_p2_mr, self.NAVY)}
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- ░░ PAGE 2 BOT 2-COLUMN ░░ -->
  <tr>
    <td style="padding:0 20px 18px 20px;background:{self.LGRAY};">
      <table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
        <td class="col" valign="top" width="48%" style="padding-right:8px;">
          {article_card(p2_bl, bg_p2_bl, self.NAVY)}
        </td>
        <td class="col" valign="top" width="52%" style="padding-left:8px;">
          {article_card(p2_br, bg_p2_br, self.NAVY)}
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- ░░ SCIM FOOTER BAR (between pages) ░░ -->
  <tr>
    <td align="center" style="padding:6px;background:#fff;border-top:2px solid {self.BORDER};border-bottom:2px solid {self.BORDER};">
      <span class="sans" style="font-size:11px;font-weight:700;color:{self.DARK};letter-spacing:1px;">SCIM | RRU–PY | ISSP</span>
    </td>
  </tr>

  <!-- ░░ PAGE 3: WATCH LIST ░░ -->
  <tr>
    <td style="padding:18px 20px 10px 20px;background:#fff;">
      {p3_watchlist}
    </td>
  </tr>

  <!-- ░░ PAGE 3: RADAR ░░ -->
  <tr>
    <td style="padding:0 20px 10px 20px;background:#fff;">
      {p3_radar}
    </td>
  </tr>

  <!-- ░░ PAGE 3: DESK COVERAGE ░░ -->
  <tr>
    <td style="padding:0 20px 10px 20px;background:#fff;">
      {p3_desk}
    </td>
  </tr>

  <!-- ░░ PAGE 3: CAREVIA + QR ░░ -->
  <tr>
    <td style="padding:0 20px 18px 20px;background:#fff;">
      {p3_carevia}
    </td>
  </tr>

  <!-- ░░ SCIM BAR ░░ -->
  <tr>
    <td align="center" style="padding:10px 20px;background:#fff;">
      <span class="sans" style="display:inline-block;background:#7a1c24;color:#ffffff;padding:5px 18px;border-radius:3px;font-size:11px;font-weight:700;letter-spacing:1px;">SCIM | RRU–PY | ISSP</span>
    </td>
  </tr>

  <!-- ░░ FULL FOOTER ░░ -->
  {p3_footer}

</table>
</td></tr>
</table>
</body></html>"""
        return html_out, self._plain_text(b)

    # ═══════════════════════════════════════════════════════════════
    # SECTION BUILDERS
    # ═══════════════════════════════════════════════════════════════

    def _glance_grid(self) -> str:
        """9-desk Today at a Glance grid matching PDF vector drawings dynamically."""
        cells = []
        if self.dynamic_glance:
            for item in self.dynamic_glance:
                name = html.escape(item['name'])
                color = item['color']
                snip_clean = html.escape(item['text'].replace("\n", " ")[:28])
                cells.append(f"""
                <td class="gc" align="center" valign="top" style="padding:2px 1px;width:11%;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                         style="background:{color};border-radius:3px;">
                    <tr><td align="center" style="padding:5px 3px;">
                      <div class="sans" style="font-size:8px;font-weight:800;color:{self.DARK};
                                               text-transform:uppercase;letter-spacing:.3px;">{name}</div>
                      <div class="sans" style="font-size:7.5px;color:{self.DARK};line-height:1.15;
                                               margin-top:2px;">{snip_clean}</div>
                    </td></tr>
                  </table>
                </td>""")
        else:
            p1_blks = [b for b in self.text_blocks if b.page == 1 and 215 <= b.bbox.y0 <= 280]
            desks = [
                ("CHENNAI",   45,  self.AMBER,  "Isolated heavy\nrain to Fri"),
                ("BENGALURU", 100, self.AMBER,  "Protest deadline;\nstrike 1 Dec"),
                ("HYDERABAD", 159, self.AMBER,  "Padayatra today;\nauction Fri"),
                ("MUMBAI",    218, self.AMBER,  "Water cut; 26/11\nparking curbs"),
                ("PUNE",      278, self.GREEN,  "Citywide water\ncut today"),
                ("KOLKATA",   341, self.AMBER,  "Fog; Metro\nclosure Sun"),
                ("NCR",       395, self.AMBER,  "Unpermitted\nmarch; GRAP II"),
                ("NATIONAL",  455, self.AMBER,  "Riyadh attack;\nGulf flights"),
                ("CYBER",     509, self.ORANGE, "vCenter zero-day;\nclaims open"),
            ]
            for name, dx, color, default in desks:
                matching = [b for b in p1_blks if abs(b.bbox.x0 - dx) < 35]
                if matching:
                    matching.sort(key=lambda b: b.bbox.y0)
                    for i, (n, d, c, _) in enumerate(desks):
                        if n == name:
                            desks[i] = (n, d, c, " ".join(b.text.strip() for b in matching))
                            break

            for name, _, color, snip in desks:
                snip_clean = html.escape(snip.replace("\n", " ")[:28])
                cells.append(f"""
                <td class="gc" align="center" valign="top" style="padding:2px 1px;width:11%;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%"
                         style="background:{color};border-radius:3px;">
                    <tr><td align="center" style="padding:5px 3px;">
                      <div class="sans" style="font-size:8px;font-weight:800;color:{self.DARK};
                                               text-transform:uppercase;letter-spacing:.3px;">{name}</div>
                      <div class="sans" style="font-size:7.5px;color:{self.DARK};line-height:1.15;
                                               margin-top:2px;">{snip_clean}</div>
                    </td></tr>
                  </table>
                </td>""")

        return f"""
        <tr>
          <td style="padding:8px 16px 10px;background:#f9fafb;border-bottom:2px solid {self.BORDER};">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td valign="middle" width="38%">
                  <span class="sans" style="font-size:9px;font-weight:800;color:{self.DARK};
                                            text-transform:uppercase;letter-spacing:.5px;">
                    TODAY AT A GLANCE &middot; HIGHEST SEVERITY BY DESK
                  </span>
                </td>
                <td valign="middle" align="right" width="62%">
                  <span class="sans" style="font-size:9px;color:#6b7280;">
                    9 desks &middot; 56 city&ndash;category cells + cyber sweep
                  </span>
                </td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:6px;">
                  <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>{''.join(cells)}</tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    def _card(self, page, y_min, y_max, x_min=0, x_max=1000) -> dict | None:
        """Extract article card data from text_blocks and hyperlinks."""
        blks = sorted(
            [b for b in self.text_blocks if b.page == page
             and y_min <= b.bbox.y0 < y_max and x_min <= b.bbox.x0 < x_max],
            key=lambda b: (round(b.bbox.y0 / 4) * 4, b.bbox.x0)
        )
        lnks = [l for l in self.hyperlinks if l.page == page
                and y_min <= l.bbox.y0 < y_max and x_min <= l.bbox.x0 < x_max]

        if not blks:
            return None

        # First significant block = headline
        headline_idx = 0
        for i, b in enumerate(blks):
            if b.is_headline or b.font_size >= 11 or i == 0:
                headline_idx = i
                break

        badge_blks, body_blks, src_blk = [], [], None
        for i, b in enumerate(blks):
            if i == headline_idx:
                continue
            txt = b.text.strip()
            skip_words = {"SCIM", "FINAL EDITION", "RRU–PY", "RRU-PY", "ISSP"}
            if any(s in txt for s in skip_words):
                continue
            if "Sources:" in txt:
                src_blk = b
            elif any(k in txt for k in ["HIGH", "MODERATE", "LOW", "IMPACT:"]) and len(txt) < 150:
                badge_blks.append(b)
            else:
                if src_blk is None:
                    body_blks.append(b)

        return {
            "headline": blks[headline_idx].text.strip(),
            "badges":   " ".join(b.text.replace("\n", " ") for b in badge_blks),
            "body":     "\n\n".join(b.text.strip() for b in body_blks),
            "sources":  src_blk.text.strip() if src_blk else "",
            "links":    lnks,
        }

    def _render_card(self, card: dict, bg_color: str = None, border_color: str = None) -> str:
        """Render one article card with exact background and text contrast matching the PDF."""
        bg = bg_color or self.WHITE
        is_dark = (bg == self.NAVY or bg == "#01093d")
        
        # Text and border styling based on card background
        text_color = "#ffffff" if is_dark else self.DARK
        body_color = "#e2e8f0" if is_dark else self.DARK
        border_box = "none" if is_dark else f"1px solid {self.BORDER}"
        bc = border_color or (self.NAVY if not is_dark else "#2e6fb3")

        # ── Severity badges ──────────────────────────────────────────
        badges_html = ""
        badge_text = card.get("badges", "")
        if badge_text:
            badge_parts = re.split(r"\n|(?<=\b)(HIGH|MODERATE|LOW|IMPACT:)", badge_text)
            badge_parts = [p.strip() for p in badge_parts if p.strip()]

            pill_parts = []
            for part in badge_parts:
                if part in ("HIGH",):
                    pill_parts.append(f'<span style="background:{self.ORANGE};color:#fff;'
                                      f'font-size:9px;font-weight:800;padding:2px 7px;'
                                      f'border-radius:3px;margin-right:4px;display:inline-block;'
                                      f'font-family:Arial,sans-serif;text-transform:uppercase;">{html.escape(part)}</span>')
                elif part in ("MODERATE",):
                    pill_parts.append(f'<span style="background:{self.AMBER};color:{self.DARK};'
                                      f'font-size:9px;font-weight:800;padding:2px 7px;'
                                      f'border-radius:3px;margin-right:4px;display:inline-block;'
                                      f'font-family:Arial,sans-serif;text-transform:uppercase;">{html.escape(part)}</span>')
                elif part in ("LOW",):
                    pill_parts.append(f'<span style="background:{self.GREEN};color:#fff;'
                                      f'font-size:9px;font-weight:800;padding:2px 7px;'
                                      f'border-radius:3px;margin-right:4px;display:inline-block;'
                                      f'font-family:Arial,sans-serif;text-transform:uppercase;">{html.escape(part)}</span>')
                else:
                    # City / category tags
                    tag_bg = "rgba(255,255,255,0.15)" if is_dark else "#fff"
                    tag_color = "#ffffff" if is_dark else self.DARK
                    tag_border = "1px solid rgba(255,255,255,0.3)" if is_dark else f"1px solid {self.BORDER}"
                    pill_parts.append(f'<span style="background:{tag_bg};color:{tag_color};'
                                      f'border:{tag_border};font-size:9px;font-weight:700;'
                                      f'padding:2px 7px;border-radius:3px;margin-right:4px;display:inline-block;'
                                      f'font-family:Arial,sans-serif;text-transform:uppercase;">{html.escape(part)}</span>')

            badges_html = f'<div style="margin-bottom:8px;line-height:1.8;">{"".join(pill_parts)}</div>'

        # ── Body paragraphs ──────────────────────────────────────────
        body_text = card.get("body", "")
        paras = [p.strip() for p in body_text.split("\n\n") if p.strip()]
        body_html = "".join(
            f'<p style="margin:0 0 8px 0;font-size:12px;line-height:1.65;color:{body_color};'
            f'text-align:justify;font-family:Georgia,serif;">{html.escape(p)}</p>'
            for p in paras
        )

        # ── Sources with clickable links ─────────────────────────────
        links = card.get("links", [])
        sources_html = self._sources_line(card.get("sources", ""), links, is_dark=is_dark)

        # ── Headline ─────────────────────────────────────────────────
        headline = html.escape(card.get("headline", ""))
        headline_size = "16px" if len(card.get("headline", "")) < 80 else "14px"

        return f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%"
               style="background:{bg};border:{border_box};border-top:3px solid {bc};
                      border-radius:3px;margin-bottom:0;">
          <tr>
            <td style="padding:12px 14px;">
              <h2 style="margin:0 0 8px 0;font-size:{headline_size};font-weight:800;
                         color:{text_color};line-height:1.3;
                         font-family:Georgia,'Times New Roman',serif;">{headline}</h2>
              {badges_html}
              {body_html}
              {sources_html}
            </td>
          </tr>
        </table>"""

    def _sources_line(self, sources_text: str, links: list, is_dark: bool = False) -> str:
        if not links and not sources_text:
            return ""

        link_color = "#93c5fd" if is_dark else "#1a56db"
        label_color = "#cbd5e1" if is_dark else "#374151"
        border_top = "1px solid rgba(255,255,255,0.2)" if is_dark else f"1px solid {self.BORDER}"

        link_parts = []
        for lnk in links:
            title = self._clean_title(lnk.visible_text, lnk.url)
            link_parts.append(
                f'<a href="{html.escape(lnk.url)}" target="_blank" rel="noopener noreferrer" '
                f'style="color:{link_color};font-weight:600;text-decoration:underline;'
                f'font-family:Arial,sans-serif;font-size:10.5px;">{html.escape(title)}</a>'
            )

        # Confidence statement from raw source text
        confidence = ""
        if sources_text and "Confidence:" in sources_text:
            conf_match = re.search(r"Confidence:\s*(.+?)(?:\||$)", sources_text)
            if conf_match:
                conf_color = "#94a3b8" if is_dark else "#6b7280"
                confidence = f' <span style="color:{conf_color};font-size:10px;font-family:Arial,sans-serif;">| Confidence: {html.escape(conf_match.group(1).strip())}</span>'

        links_rendered = " &middot; ".join(link_parts) if link_parts else ""
        return f"""
        <div style="margin-top:10px;padding-top:6px;border-top:{border_top};
                    font-size:10.5px;line-height:1.5;font-family:Arial,sans-serif;">
          <strong style="color:{label_color};">Sources:</strong>
          <span style="margin-left:4px;">{links_rendered}{confidence}</span>
        </div>"""

    def _watchlist_table(self) -> str:
        """Page 3 Watch List — Developing Situations (3 columns)."""
        p3_blks = sorted(
            [b for b in self.text_blocks if b.page == 3 and 70 <= b.bbox.y0 <= 185],
            key=lambda b: b.bbox.y0
        )
        # Skip header rows
        rows_data = [b for b in p3_blks if "Watch List" not in b.text
                     and "SITUATION" not in b.text and "WHERE IT STANDS" not in b.text]

        rows_html = []
        for i, blk in enumerate(rows_data):
            lines = [line.strip() for line in blk.text.split("\n") if line.strip()]
            if not lines:
                continue

            # In PyMuPDF blocks, each row is structured as:
            # line 0: Situation title
            # line 1: Date badge (e.g. "25–27 Nov", "to 29 Nov")
            # line 2: Where it stands
            # line 3: What to watch next
            if len(lines) >= 4:
                situation = lines[0]
                date_str = lines[1]
                where_stands = lines[2]
                watch_next = " ".join(lines[3:])
            elif len(lines) == 3:
                situation = lines[0]
                date_str = ""
                where_stands = lines[1]
                watch_next = lines[2]
            else:
                txt = " ".join(lines)
                parts = [p.strip() for p in txt.split("  ") if p.strip()]
                situation = parts[0] if len(parts) > 0 else txt
                date_str = ""
                where_stands = parts[1] if len(parts) > 1 else ""
                watch_next = parts[2] if len(parts) > 2 else ""

            date_badge = (
                f'<span style="background:{self.AMBER};color:{self.DARK};font-size:9px;font-weight:700;'
                f'padding:1px 6px;border-radius:3px;font-family:Arial,sans-serif;white-space:nowrap;margin-left:4px;">'
                f'{html.escape(date_str)}</span>'
            ) if date_str else ""

            bg = "#fff" if i % 2 == 0 else "#f9fafb"
            rows_html.append(f"""
            <tr style="background:{bg};">
              <td style="padding:7px 10px;border-bottom:1px solid {self.BORDER};width:28%;
                         font-size:11.5px;font-weight:700;color:{self.DARK};font-family:Georgia,serif;vertical-align:top;">
                {html.escape(situation)}{date_badge}
              </td>
              <td style="padding:7px 10px;border-bottom:1px solid {self.BORDER};width:36%;
                         font-size:11px;color:#374151;font-family:Arial,sans-serif;vertical-align:top;">
                {html.escape(where_stands)}
              </td>
              <td style="padding:7px 10px;border-bottom:1px solid {self.BORDER};width:36%;
                         font-size:11px;color:#374151;font-family:Arial,sans-serif;vertical-align:top;">
                {html.escape(watch_next)}
              </td>
            </tr>""")

        if not rows_html:
            rows_html.append(f'<tr><td colspan="3" style="padding:10px;font-size:11px;color:#6b7280;">Watch list situations tracked for this edition.</td></tr>')

        return f"""
        <div style="margin-bottom:4px;">
          <span style="font-size:16px;font-weight:800;color:{self.CRIMSON};
                       font-family:Georgia,'Times New Roman',serif;">Watch List &mdash; Developing Situations</span>
        </div>
        <table border="0" cellpadding="0" cellspacing="0" width="100%"
               style="border:1px solid {self.BORDER};border-radius:3px;overflow:hidden;">
          <tr style="background:{self.LGRAY};">
            <th align="left" style="padding:6px 10px;font-size:9px;font-weight:700;
                color:#6b7280;font-family:Arial,sans-serif;text-transform:uppercase;
                border-bottom:2px solid {self.BORDER};width:28%;">SITUATION</th>
            <th align="left" style="padding:6px 10px;font-size:9px;font-weight:700;
                color:#6b7280;font-family:Arial,sans-serif;text-transform:uppercase;
                border-bottom:2px solid {self.BORDER};width:36%;">WHERE IT STANDS</th>
            <th align="left" style="padding:6px 10px;font-size:9px;font-weight:700;
                color:#6b7280;font-family:Arial,sans-serif;text-transform:uppercase;
                border-bottom:2px solid {self.BORDER};width:36%;">WHAT TO WATCH NEXT</th>
          </tr>
          {''.join(rows_html)}
        </table>"""

    def _radar_table(self) -> str:
        """Page 3 Also on the Radar — City Briefs."""
        # Restrict y0 to < 460 to strictly exclude Desk coverage and Student desk blocks
        p3_blks = sorted(
            [b for b in self.text_blocks if b.page == 3 and 225 <= b.bbox.y0 < 460],
            key=lambda b: b.bbox.y0
        )
        p3_links = [l for l in self.hyperlinks if l.page == 3 and 220 <= l.bbox.y0 < 465]

        # Filter out headers and desk coverage / student desk statistics
        rows_data = [
            b for b in p3_blks
            if "Also on the Radar" not in b.text
            and "CITY" not in b.text
            and "SEVERITY" not in b.text
            and "Desk coverage" not in b.text
            and "Student desk" not in b.text
            and "7 cities" not in b.text
            and "gap list" not in b.text
            and "gap tasks" not in b.text
            and "findings" not in b.text
        ]

        rows_html = []
        seen_texts = set()
        for i, blk in enumerate(rows_data):
            lines = [l.strip() for l in blk.text.split("\n") if l.strip()]
            if not lines:
                continue

            # Check if this is an orphaned source citation line like "Telangana Today, 24 Nov"
            if len(lines) == 1 and ("Today" in lines[0] or "Mail" in lines[0] or "FPJ" in lines[0]) and len(lines[0]) < 60:
                continue

            # Avoid duplicate rows
            norm_key = " ".join(lines)[:60].lower()
            if norm_key in seen_texts:
                continue
            seen_texts.add(norm_key)

            # Standard block structure:
            # line 0: City (e.g. "National", "Cyber", "Hyderabad", "Mumbai", "Kolkata")
            # line 1: Severity (e.g. "HIGH", "MODERATE", "LOW")
            # line 2+: Description and briefing
            city = lines[0]
            if len(lines) > 1 and lines[1] in ("HIGH", "MODERATE", "LOW"):
                severity = lines[1]
                desc = " ".join(lines[2:])
            else:
                # Fallback regex if lines merged
                sev_match = re.search(r"\b(HIGH|MODERATE|LOW)\b", blk.text)
                if sev_match:
                    severity = sev_match.group(1)
                    parts = blk.text.split(severity, 1)
                    city = parts[0].strip()
                    desc = parts[1].replace("\n", " ").strip()
                else:
                    severity = "LOW"
                    desc = " ".join(lines[1:]) if len(lines) > 1 else lines[0]

            if severity == "HIGH":
                sev_color = self.ORANGE
                sev_text_color = "#fff"
            elif severity == "MODERATE":
                sev_color = self.AMBER
                sev_text_color = self.DARK
            else:
                sev_color = self.GREEN
                sev_text_color = "#fff"

            # Match links for this row
            row_lnks = [l for l in p3_links if abs(l.bbox.y0 - blk.bbox.y0) < 25]
            link_html = ""
            if row_lnks:
                link_parts = []
                for lnk in row_lnks:
                    t = self._clean_title(lnk.visible_text, lnk.url)
                    link_parts.append(
                        f'<a href="{html.escape(lnk.url)}" target="_blank" rel="noopener noreferrer" '
                        f'style="color:#1a56db;font-weight:600;text-decoration:underline;font-size:10px;">'
                        f'{html.escape(t)}</a>'
                    )
                link_html = " &middot; " + " &middot; ".join(link_parts)

            bg = "#fff" if len(rows_html) % 2 == 0 else "#f9fafb"
            rows_html.append(f"""
            <tr style="background:{bg};">
              <td style="padding:7px 10px;border-bottom:1px solid {self.BORDER};
                         vertical-align:top;font-size:11px;color:#374151;
                         font-family:Arial,sans-serif;">
                <strong style="color:{self.DARK};font-size:11.5px;margin-right:8px;">{html.escape(city)}</strong>
                <span style="background:{sev_color};color:{sev_text_color};font-size:9px;
                             font-weight:800;padding:2px 7px;border-radius:3px;
                             font-family:Arial,sans-serif;text-transform:uppercase;
                             margin-right:8px;display:inline-block;">{severity}</span>
                {html.escape(desc)}{link_html}
              </td>
            </tr>""")

        if not rows_html:
            rows_html.append(f'<tr><td style="padding:10px;font-size:11px;color:#6b7280;">City briefs for this edition.</td></tr>')

        return f"""
        <div style="margin-bottom:4px;margin-top:16px;">
          <span style="font-size:16px;font-weight:800;color:{self.CRIMSON};
                       font-family:Georgia,'Times New Roman',serif;">Also on the Radar &mdash; City Briefs</span>
        </div>
        <table border="0" cellpadding="0" cellspacing="0" width="100%"
               style="border:1px solid {self.BORDER};border-radius:3px;overflow:hidden;">
          <tr style="background:{self.LGRAY};">
            <th align="left" style="padding:6px 10px;font-size:9px;font-weight:700;
                color:#6b7280;font-family:Arial,sans-serif;text-transform:uppercase;
                border-bottom:2px solid {self.BORDER};">CITY &nbsp;&nbsp; SEVERITY &nbsp;&nbsp; WHAT IT MEANS AND WHAT TO DO</th>
          </tr>
          {''.join(rows_html)}
        </table>"""

    def _desk_coverage(self) -> str:
        """Desk coverage & student desk statistics block."""
        # Find desk coverage label and body (page 3, y between 450 and 560)
        p3_cov_blks = [b for b in self.text_blocks if b.page == 3 and 450 <= b.bbox.y0 <= 570]
        
        # Desk coverage (left column: x0 < 250)
        desk_body_blk = next((b for b in p3_cov_blks if "7 cities" in b.text), None)
        if not desk_body_blk:
            # fallback to block in left column that is not the header
            desk_body_blk = next((b for b in p3_cov_blks if b.bbox.x0 < 200 and "Desk coverage" not in b.text and "Student desk" not in b.text), None)
            
        # Student desk (right column: x0 >= 350)
        stud_body_blk = next((b for b in p3_cov_blks if any(k in b.text.lower() for k in ["gap list", "gap tasks", "findings", "blocked-site"])), None)
        if not stud_body_blk:
            stud_body_blk = next((b for b in p3_cov_blks if b.bbox.x0 >= 350 and "Desk coverage" not in b.text and "Student desk" not in b.text), None)

        desk_label = "Desk coverage:"
        desk_body = desk_body_blk.text.replace("\n", " ").strip() if desk_body_blk else "7 cities × 8 risk categories, a national desk and a Cyber desk, swept with process v2.17."
        stud_label = "Student desk:"
        stud_body = stud_body_blk.text.replace("\n", " ").strip() if stud_body_blk else ""

        return f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%"
               style="border-top:1px solid {self.BORDER};padding-top:10px;margin-top:12px;">
          <tr>
            <td valign="top" width="62%" style="padding:8px 14px 8px 0;">
              <div class="sans" style="font-size:10px;font-weight:700;color:{self.DARK};margin-bottom:3px;">{desk_label}</div>
              <div class="sans" style="font-size:10px;color:#374151;line-height:1.5;text-align:justify;">{html.escape(desk_body)}</div>
            </td>
            <td valign="top" width="38%" style="padding:8px 0 8px 14px;border-left:1px solid {self.BORDER};">
              <div class="sans" style="font-size:10px;font-weight:700;color:{self.DARK};margin-bottom:3px;">{stud_label}</div>
              <div class="sans" style="font-size:10px;color:#374151;line-height:1.5;">{html.escape(stud_body)}</div>
            </td>
          </tr>
        </table>"""

    def _carevia_block(self) -> str:
        """CAREVIA support block + QR code."""
        carevia_blk = next((b for b in self.text_blocks if b.page == 3 and "CAREVIA" in b.text), None)
        carevia_txt = carevia_blk.text.strip() if carevia_blk else \
            "PULSE-R24 IS SUPPORTED BY CAREVIA\nSupporting the PULSE-R24 platform's hosting, AI and delivery costs."

        # QR asset
        qr_asset = next((a for a in self.assets if a.asset_type == "qr_code"), None)
        qr_url   = qr_asset.qr_decoded_data if (qr_asset and qr_asset.qr_decoded_data) else \
            "https://drive.google.com/drive/folders/18LhFhrpUOXOIFIoLRZOtuqhrWnxsr61D"

        qr_img = ""
        if qr_asset:
            qr_src = self._get_asset_src(qr_asset)
            qr_img = f"""<a href="{html.escape(qr_url)}" target="_blank" rel="noopener noreferrer">
              <img src="{qr_src}" alt="QR" width="90" height="90"
                   style="display:block;border:1px solid {self.BORDER};border-radius:3px;" />
            </a>"""

        # CAREVIA logo asset (asset_p3_1_81 = Carevia hand logo)
        carevia_logo_asset = next((a for a in self.assets if a.page == 3 and a.asset_type in ("news_image", "logo") and a.width < 450), None)
        logo_html = ""
        if carevia_logo_asset:
            carevia_src = self._get_asset_src(carevia_logo_asset)
            logo_html = f'<img src="{carevia_src}" alt="CAREVIA" width="52" height="44" style="display:block;margin-bottom:4px;" />'

        # Explore Repository link text
        explore_blk = next((b for b in self.text_blocks if b.page == 3 and "Explore Repository" in b.text), None)
        explore_text = explore_blk.text.strip() if explore_blk else "Explore Repository"

        # Find explore link
        explore_lnk = next((l for l in self.hyperlinks if l.page == 3 and "drive.google.com" in l.url), None)
        explore_href = explore_lnk.url if explore_lnk else qr_url

        return f"""
        <table border="0" cellpadding="0" cellspacing="0" width="100%"
               style="border:1px solid {self.BORDER};border-radius:4px;background:#f9fafb;margin-top:14px;">
          <tr>
            <td valign="middle" width="68" style="padding:12px 8px 12px 14px;">
              {logo_html}
            </td>
            <td valign="middle" style="padding:12px 8px;">
              <div class="sans" style="font-size:9px;font-weight:700;color:{self.CRIMSON};
                                       text-transform:uppercase;letter-spacing:.5px;">PULSE-R24 IS SUPPORTED BY</div>
              <div class="sans" style="font-size:17px;font-weight:900;color:{self.DARK};line-height:1.1;margin-top:1px;">CAREVIA</div>
              <div class="sans" style="font-size:11px;color:#374151;margin-top:3px;line-height:1.4;">
                Supporting the PULSE-R24 platform&rsquo;s hosting, AI and delivery costs.
              </div>
            </td>
            <td valign="middle" align="center" width="110" style="padding:12px 14px 12px 8px;border-left:1px solid {self.BORDER};">
              {qr_img}
              <div style="margin-top:6px;">
                <a href="{html.escape(explore_href)}" target="_blank" rel="noopener noreferrer"
                   style="color:{self.CRIMSON};font-weight:700;font-size:10.5px;
                          text-decoration:underline;font-family:Arial,sans-serif;">
                  {html.escape(explore_text)}
                </a>
              </div>
            </td>
          </tr>
        </table>"""

    def _full_footer(self, b: BrandingSettings) -> str:
        """Full Page 3 footer: logos + social icons + AI declaration."""
        # Sort all page-3 social icons by filename (p3_4, p3_5, … p3_9) to preserve PDF order
        soc_assets = sorted(
            [a for a in self.assets if a.page == 3 and a.asset_type == "social_icon"],
            key=lambda a: a.filename
        )

        # Find the SCIM logo: specifically asset_p3_3 (320×320 circular SCIM logo).
        # Fallback: news_image with width 280-349 (excludes CAREVIA at 400px).
        scim_logo = next((a for a in self.assets if a.page == 3 and "p3_3" in a.filename), None)
        if not scim_logo:
            scim_logo = next((a for a in self.assets if a.page == 3
                              and a.asset_type in ("news_image", "logo")
                              and 280 <= a.width <= 349), None)

        # Find RRU/Cyber logo: specifically asset_p3_10 (200×200 circular logo).
        cyber_logo = next((a for a in self.assets if a.page == 3 and "p3_10" in a.filename), None)
        if not cyber_logo:
            cyber_logo = next((a for a in self.assets if a.page == 3
                               and a.asset_type == "embedded_image"), None)

        scim_img = ""
        if scim_logo:
            scim_src = self._get_asset_src(scim_logo)
            scim_img = (
                f'<div style="display:inline-block;background:#ffffff;padding:4px;border-radius:4px;">'
                f'<img src="{scim_src}" alt="SCIM" width="76" height="76" '
                f'style="display:block;border-radius:50%;" /></div>'
            )
        cyber_img = ""
        if cyber_logo:
            cyber_src = self._get_asset_src(cyber_logo)
            cyber_img = (
                f'<div style="display:inline-block;background:#ffffff;padding:4px;border-radius:4px;margin-left:auto;">'
                f'<img src="{cyber_src}" alt="RRU Cyber" width="68" height="68" '
                f'style="display:block;border-radius:50%;" /></div>'
            )

        # Social icons row — ordered by filename to match PDF left-to-right order
        s = b.social_links
        social_names = ["Website", "LinkedIn", "Instagram", "YouTube", "Facebook", "X / Twitter"]
        social_hrefs = [
            s.get("website", "#"),
            s.get("linkedin", "#"),
            s.get("instagram", "#"),
            s.get("youtube", "#"),
            s.get("facebook", "#"),
            s.get("twitter", "#"),
        ]
        icon_cells = []
        for i, asset in enumerate(soc_assets[:6]):
            name = social_names[i] if i < len(social_names) else f"Social {i+1}"
            href = social_hrefs[i] if i < len(social_hrefs) else "#"
            soc_src = self._get_asset_src(asset)
            icon_cells.append(
                f'<td align="center" style="padding:0 2px;">'
                f'<a href="{html.escape(href)}" target="_blank" rel="noopener noreferrer">'
                f'<img src="{soc_src}" alt="{name}" width="26" height="26" '
                f'style="display:block;border-radius:50%;" /></a></td>'
            )
        social_row = f'<table border="0" cellpadding="0" cellspacing="0"><tr>{"".join(icon_cells)}</tr></table>'

        # Extract dynamic text from PDF blocks on Page 3
        p3_blks = [blk for blk in self.text_blocks if blk.page == 3 and blk.bbox.y0 >= 600]

        # 1. Institutional attribution
        inst_blk = next((blk for blk in p3_blks if any(k in blk.text for k in [
            "Created by the Students", "Published by the Center",
            "International Society", "RRU\u2013Puducherry", "RRU-Puducherry"
        ])), None)
        inst_text = (inst_blk.text.replace("\n", " ").strip() if inst_blk
                     else (b.institutional_attribution or
                           "Created by the Students of Security and Corporate Intelligence Management "
                           "(2025\u201326), RRU\u2013Puducherry, and mentored by the International Society "
                           "For Security Professionals."))

        # 2. Tagline
        tagline_blk = next((blk for blk in p3_blks if "SHAPING THE FUTURE" in blk.text), None)
        tagline_text = (tagline_blk.text.replace("\n", " ").strip() if tagline_blk
                        else "SHAPING THE FUTURE OF CORPORATE SECURITY INTELLIGENCE IN INDIA")

        # 3. AI Declaration (combine both continuation lines)
        ai_blks = [blk for blk in p3_blks if
                   "AI usage declaration" in blk.text or "Student desk findings" in blk.text]
        if ai_blks:
            ai_blks.sort(key=lambda x: x.bbox.y0)
            ai_text = " ".join(blk.text.replace("\n", " ").strip() for blk in ai_blks)
        else:
            ai_text = (b.ai_declaration or
                       "AI usage declaration: this edition was collected, triaged, written and "
                       "fact-checked with AI assistance (Claude, Anthropic) in the PULSE-R24 live "
                       "pilot run by CAREVIA with ISSP and RRU Puducherry. Student desk findings are "
                       "added overnight; RRU reviewers validate the edition before release.")

        BG = self.NAVY
        return f"""
        <tr>
          <td style="padding:18px 20px 14px 20px;background:{BG};">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <!-- LEFT: Prepared & curated by + SCIM logo -->
                <td valign="top" width="94" align="center" style="padding-right:10px;">
                  <div class="sans" style="font-size:8px;font-weight:700;color:#e2e8f0;
                       margin-bottom:6px;white-space:nowrap;font-family:Georgia,'Times New Roman',serif;">
                    Prepared &amp; curated by
                  </div>
                  {scim_img}
                </td>
                <!-- CENTER: Institution text + tagline + social icons -->
                <td valign="top" align="center" style="padding:0 10px;">
                  <div class="sans" style="font-size:10.5px;font-weight:700;color:#ffffff;
                       line-height:1.4;margin-bottom:6px;
                       font-family:Georgia,'Times New Roman',serif;">
                    {html.escape(inst_text)}
                  </div>
                  <div class="sans" style="font-size:9px;font-weight:800;color:#ffffff;
                       text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;
                       font-family:Georgia,'Times New Roman',serif;">
                    {html.escape(tagline_text)}
                  </div>
                  <div class="sans" style="font-size:8.5px;color:#cbd5e1;margin-bottom:6px;
                       font-weight:700;font-family:Georgia,'Times New Roman',serif;">
                    FOLLOW US ON
                  </div>
                  {social_row}
                </td>
                <!-- RIGHT: Technical Support by + RRU Cyber logo -->
                <td valign="top" width="94" align="center" style="padding-left:10px;text-align:center;">
                  <div class="sans" style="font-size:8px;font-weight:700;color:#e2e8f0;
                       margin-bottom:6px;white-space:nowrap;text-align:center;
                       font-family:Georgia,'Times New Roman',serif;">
                    Technical Support by
                  </div>
                  {cyber_img}
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td align="center" style="padding:8px 20px 14px 20px;background:{BG};
               border-top:1px solid rgba(255,255,255,0.15);">
            <p class="sans" style="margin:0;font-size:8.5px;color:#cbd5e1;line-height:1.5;
                 text-align:center;font-family:Arial,Helvetica,sans-serif;">
              {html.escape(ai_text)}
            </p>
          </td>
        </tr>"""

    def _footer_row(self, b: BrandingSettings) -> str:
        """Simple dark footer for Faithful mode."""
        return f"""
        <tr>
          <td bgcolor="{self.NAVY}" style="padding:14px 20px;text-align:center;">
            <p class="sans" style="margin:0 0 4px 0;color:#e2e8f0;font-size:11px;">{b.institutional_attribution}</p>
            <p class="sans" style="margin:0;color:#9ca3af;font-size:10px;">{b.ai_declaration}</p>
          </td>
        </tr>"""

    def _wrap(self, max_width: int, body: str, b: BrandingSettings) -> str:
        return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>Pulse R24</title>
  <style>body,table,td,a{{-webkit-text-size-adjust:100%;}}body{{margin:0;padding:0;background:#e5e7eb;}}
  .sans{{font-family:Arial,Helvetica,sans-serif!important;}}
  @media(max-width:680px){{.ec{{width:100%!important;}}}}</style>
</head>
<body style="margin:0;padding:0;background:#e5e7eb;">
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="background:#e5e7eb;">
  <tr><td align="center" style="padding:16px 8px;">
    <table border="0" cellpadding="0" cellspacing="0" width="{max_width}" class="ec"
           style="background:#fff;border-radius:4px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);">
      <tr><td bgcolor="{self.NAVY}" style="padding:12px 20px;">
        <span style="color:#fff;font-size:18px;font-weight:900;">PULSE-R24</span>
      </td></tr>
      <tr><td style="padding:20px;">{body}</td></tr>
      {self._footer_row(b)}
    </table>
  </td></tr>
</table>
</body></html>"""

    # ═══════════════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════════════
    @staticmethod
    def _clean_title(visible_text: str | None, url: str) -> str:
        """Return a readable link label — strips PyMuPDF OCR artefacts."""
        if not visible_text:
            # derive from domain
            m = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", url or "")
            return m.group(1).split(".")[0].capitalize() if m else "Source"

        t = visible_text.strip()
        # Remove trailing single-char noise (e.g. "d b h k ) (")
        t = re.sub(r"(\s+[a-z0-9]{1,2}){3,}\s*[\)\(\/\|]*$", "", t).strip()
        t = re.sub(r"[\s\)\(\|\/]+$", "", t).strip()

        # If still looks noisy or too short, use domain
        if len(t) < 4 or re.match(r"^[\s\)\(\|\/a-z0-9]{0,8}$", t):
            m = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", url or "")
            return m.group(1).split(".")[0].capitalize() if m else "Source"
        return t

    def _plain_text(self, b: BrandingSettings) -> str:
        lines = ["PULSE-R24 DAILY INTEL PULSE",
                 "=" * 50,
                 f"Curated by {b.institutional_attribution}",
                 "", "VERIFIED HYPERLINKS:", "-" * 50]
        for lnk in self.hyperlinks:
            lines.append(f"- {self._clean_title(lnk.visible_text, lnk.url)}: {lnk.url}")
        lines += ["", "=" * 50, b.ai_declaration]
        return "\n".join(lines)
