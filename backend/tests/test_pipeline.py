import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_full_pipeline_with_reference_pdf():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Analyze reference PDF
        res = await client.post("/api/pdf/analyze-reference")
        assert res.status_code == 200
        data = res.json()
        doc_id = data["doc_id"]
        assert doc_id == "ref_359"
        assert data["page_count"] == 3
        # Exactly 41 hyperlinks benchmark
        assert data["total_hyperlinks"] == 41
        assert data["mapped_hyperlinks"] > 35
        assert data["qr_detected"] is True
        assert "drive.google.com" in (data["qr_content"] or "")

        # 3. Retrieve hyperlinks
        res = await client.get(f"/api/hyperlinks/{doc_id}")
        assert res.status_code == 200
        links = res.json()
        assert len(links) == 41

        # Verify page-wise distribution
        p1_links = [l for l in links if l["page"] == 1]
        p2_links = [l for l in links if l["page"] == 2]
        p3_links = [l for l in links if l["page"] == 3]
        assert len(p1_links) == 10
        assert len(p2_links) == 18
        assert len(p3_links) == 13

        # 4. Test hyperlink update
        first_link = links[0]
        res = await client.put(
            f"/api/hyperlinks/{doc_id}/{first_link['id']}",
            json={"visible_text": "Siasat DGP Verified"},
        )
        assert res.status_code == 200
        assert res.json()["visible_text"] == "Siasat DGP Verified"

        # 5. Retrieve assets
        res = await client.get(f"/api/assets/{doc_id}")
        assert res.status_code == 200
        assets = res.json()
        assert len(assets) >= 5
        qr_assets = [a for a in assets if a["asset_type"] == "qr_code"]
        assert len(qr_assets) >= 1

        # 6. Generate Faithful Mode HTML
        res = await client.post(
            f"/api/generate/{doc_id}",
            json={"mode": "faithful", "include_source_directory": True},
        )
        assert res.status_code == 200
        gen_data = res.json()
        assert gen_data["mode"] == "faithful"
        assert "<!DOCTYPE" in gen_data["html_content"]
        assert "Page 1 Sources" in gen_data["html_content"]

        # 7. Generate Reconstructed Mode HTML
        res = await client.post(
            f"/api/generate/{doc_id}",
            json={"mode": "reconstructed"},
        )
        assert res.status_code == 200
        rec_data = res.json()
        assert rec_data["mode"] == "reconstructed"
        assert "<!DOCTYPE" in rec_data["html_content"]
        assert "table" in rec_data["html_content"]
        assert rec_data["total_links_included"] == 41

        # 8. Run 14-point Validation Engine
        res = await client.post(f"/api/validation/{doc_id}")
        assert res.status_code == 200
        val_report = res.json()
        assert val_report["total_checks"] == 14
        assert val_report["failed_count"] == 0
        assert val_report["passed_count"] >= 12

        # 9. Create Export Package (ZIP)
        res = await client.post(f"/api/export/{doc_id}/package")
        assert res.status_code == 200
        manifest = res.json()
        assert manifest["doc_id"] == doc_id
        assert manifest["assets_included"] >= 5

        # 10. Verify Settings API
        res = await client.get("/api/settings/branding")
        assert res.status_code == 200
        branding = res.json()
        assert branding["bulletin_name"] == "PULSE R24"
