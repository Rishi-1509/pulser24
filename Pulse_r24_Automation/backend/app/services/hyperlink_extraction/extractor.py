import csv
import io
import json
from pathlib import Path
import fitz
from app.models.schemas import BoundingBox, HyperlinkItem


class HyperlinkExtractor:
    """Intelligent hyperlink extraction and geometric mapping engine."""

    def __init__(self, doc: fitz.Document):
        self.doc = doc

    def extract_hyperlinks(self) -> list[HyperlinkItem]:
        """Extract all hyperlink annotations across all pages with geometric text mapping."""
        hyperlinks: list[HyperlinkItem] = []
        global_link_counter = 0

        for pno, page in enumerate(self.doc):
            page_num = pno + 1
            raw_links = page.get_links()

            for l_idx, link in enumerate(raw_links):
                uri = link.get("uri")
                rect = link.get("from")  # fitz.Rect
                if not uri:
                    continue

                global_link_counter += 1
                link_id = f"link_p{page_num}_{l_idx + 1}"

                link_rect = fitz.Rect(rect)
                # Calculate strict bounding box overlap with words on the page
                all_words = page.get_text("words")
                matched_words = []
                for w in all_words:
                    overlap_x = max(0, min(w[2], link_rect.x1) - max(w[0], link_rect.x0))
                    overlap_y = max(0, min(w[3], link_rect.y1) - max(w[1], link_rect.y0))
                    w_w = w[2] - w[0]
                    w_h = w[3] - w[1]
                    if w_w > 0 and w_h > 0:
                        if (overlap_x / w_w > 0.35) and (overlap_y / w_h > 0.35):
                            matched_words.append(w)

                if matched_words:
                    matched_words.sort(key=lambda w: (w[6], w[0]))
                    visible_text = " ".join([w[4] for w in matched_words]).strip()
                else:
                    visible_text = page.get_text("text", clip=link_rect).replace("\n", " ").strip()

                # Get surrounding context (the full line/paragraph intersecting the link)
                context_clip = fitz.Rect(
                    max(0, link_rect.x0 - 100),
                    max(0, link_rect.y0 - 8),
                    min(page.rect.width, link_rect.x1 + 100),
                    min(page.rect.height, link_rect.y1 + 18),
                )
                context_text = page.get_text("text", clip=context_clip).replace("\n", " ").strip()

                # Determine link type
                link_type = "external"
                if uri.startswith("mailto:"):
                    link_type = "email"
                elif uri.startswith("#") or not uri.startswith("http"):
                    link_type = "internal"

                # Status
                mapping_status = "mapped" if visible_text else "unmapped"

                hyperlinks.append(
                    HyperlinkItem(
                        id=link_id,
                        page=page_num,
                        url=uri,
                        visible_text=visible_text or f"[Source P{page_num} #{l_idx+1}]",
                        bbox=BoundingBox(
                            x0=round(link_rect.x0, 2),
                            y0=round(link_rect.y0, 2),
                            x1=round(link_rect.x1, 2),
                            y1=round(link_rect.y1, 2),
                        ),
                        link_type=link_type,
                        mapping_status=mapping_status,
                        context_text=context_text[:200],
                        is_verified=None,
                    )
                )

        return hyperlinks

    @staticmethod
    def export_to_json(hyperlinks: list[HyperlinkItem]) -> str:
        data = [link.model_dump() for link in hyperlinks]
        return json.dumps(data, indent=2)

    @staticmethod
    def export_to_csv(hyperlinks: list[HyperlinkItem]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Page", "Visible Text", "Original URL", "Type", "Status", "Context"])
        for link in hyperlinks:
            writer.writerow([
                link.id,
                link.page,
                link.visible_text,
                link.url,
                link.link_type,
                link.mapping_status,
                link.context_text,
            ])
        return output.getvalue()
