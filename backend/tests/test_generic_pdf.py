import pytest
import fitz
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_arbitrary_pdf_upload_and_conversion():
    # 1. Create a dynamic test PDF with 2 pages and custom links
    doc = fitz.open()
    
    # Page 1
    p1 = doc.new_page(width=600, height=800)
    p1.insert_text((50, 80), "BREAKING INTELLIGENCE REPORT", fontsize=18)
    p1.insert_text((50, 120), "Cybersecurity incident response update for industrial networks.", fontsize=11)
    p1.insert_text((50, 150), "Source: CISA Advisory Bulletin", fontsize=10)
    # Insert link
    link_rect = fitz.Rect(50, 140, 220, 155)
    p1.insert_link({"kind": fitz.LINK_URI, "from": link_rect, "uri": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"})

    # Page 2
    p2 = doc.new_page(width=600, height=800)
    p2.insert_text((50, 80), "REGIONAL CRITICAL INFRASTRUCTURE", fontsize=16)
    p2.insert_text((50, 120), "Grid stability and supply chain monitoring notes.", fontsize=11)
    p2.insert_text((50, 150), "Ref: National Power Portal", fontsize=10)
    link_rect2 = fitz.Rect(50, 140, 200, 155)
    p2.insert_link({"kind": fitz.LINK_URI, "from": link_rect2, "uri": "https://npp.gov.in"})

    pdf_bytes = doc.tobytes()
    doc.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload dynamic PDF
        files = {"file": ("dynamic_edition_999.pdf", pdf_bytes, "application/pdf")}
        res = await client.post("/api/pdf/upload", files=files)
        assert res.status_code == 200
        data = res.json()
        assert data["page_count"] == 2
        assert data["total_hyperlinks"] == 2
        assert data["mapped_hyperlinks"] >= 1

        doc_id = data["doc_id"]

        # Validate
        res = await client.post(f"/api/validation/{doc_id}")
        assert res.status_code == 200
        val = res.json()
        assert val["total_checks"] == 14
        assert val["failed_count"] == 0

        # Generate both modes
        res_f = await client.post(f"/api/generate/{doc_id}", json={"mode": "faithful"})
        assert res_f.status_code == 200
        assert "cisa.gov" in res_f.json()["html_content"]

        res_r = await client.post(f"/api/generate/{doc_id}", json={"mode": "reconstructed"})
        assert res_r.status_code == 200
        assert "BREAKING INTELLIGENCE REPORT" in res_r.json()["html_content"]
