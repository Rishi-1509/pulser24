# Pulse R24 — Email Publishing Studio

A professional web application that converts **Pulse R24 PDF intelligence bulletins** into responsive, email-compatible HTML. All images are embedded as base64 data URIs so the email renders correctly when pasted into Gmail.

---

## Features

- **Upload any Pulse R24 PDF** — extracts text, tables, links, images, QR codes, logos, and social icons automatically
- **Two output modes:**
  - **Reconstructed HTML** — semantic, table-based email with inline styles, fully rendered sections (Today at a Glance, Radar table, Desk Coverage, Student Desk, CAREVIA block, Footer)
  - **Faithful Page Slices** — pixel-perfect page images with clickable hyperlink overlays
- **Base64 image embedding** — all images embedded as data URIs; works in Gmail when pasted directly
- **Dynamic extraction** — content is never hardcoded; every field comes from the uploaded PDF

---

## Tech Stack

| Layer    | Technology                                             |
| -------- | ------------------------------------------------------ |
| Backend  | Python 3.11, FastAPI, PyMuPDF, pdfplumber              |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4             |
| Tools    | uv (Python package manager), npm / Node.js             |

---

## Prerequisites

- **Node.js** ≥ 20 — [nodejs.org](https://nodejs.org/)
- **uv** (Python package manager) — [docs.astral.sh/uv](https://docs.astral.sh/uv/)
  - `uv` will automatically download Python 3.11 if not installed.

---

## Quick Start

### 1. Backend

```bash
cd backend

# Install Python dependencies
uv sync

# Start the API server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API available at **http://localhost:8000**  
Swagger docs at **http://localhost:8000/api/docs**

### 2. Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm run dev
```

App available at **http://localhost:5173**

> The Vite dev server proxies `/api/*` requests to the backend at port 8000.

---

## Windows Quick-Start Scripts

Double-click the included `.bat` files to start both servers:

- `start-backend.bat` — starts the FastAPI backend on port 8000
- `start-frontend.bat` — starts the Vite frontend on port 5173

---

## Usage

1. Open **http://localhost:5173** in your browser
2. Upload a Pulse R24 PDF using the upload button
3. Wait for extraction to complete (usually 10–30 seconds)
4. Click **Generate Email** to produce the reconstructed HTML
5. Preview the email in the browser
6. Click **Download** to save `email.html`
7. Open Gmail → Compose → paste the HTML content (Ctrl+V)

---

## Project Structure

```
pulse r/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # Route handlers (upload, generate, assets)
│   │   ├── core/               # Configuration & settings
│   │   ├── models/             # Pydantic schemas
│   │   └── services/
│   │       ├── pdf/            # PDF extraction engine
│   │       ├── html_generation/ # Email HTML generator
│   │       └── image/          # Image processing
│   └── pyproject.toml
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── vite.config.ts
│   └── package.json
├── sample-data/                # Reference PDF(s)
├── start-backend.bat
├── start-frontend.bat
└── README.md
```

---

## API Endpoints

| Method | Endpoint                        | Description                        |
| ------ | ------------------------------- | ---------------------------------- |
| GET    | `/api/health`                   | Health check                       |
| POST   | `/api/upload`                   | Upload a PDF for extraction        |
| GET    | `/api/documents`                | List all extracted documents       |
| POST   | `/api/generate/{doc_id}`        | Generate email HTML from a doc     |
| GET    | `/api/download/{doc_id}/{mode}` | Download generated HTML file       |
| GET    | `/api/assets/{doc_id}/{file}`   | Serve an extracted asset image     |

---

## Notes

- **Never hardcode content** — all text, links, and images are extracted dynamically from the uploaded PDF.
- **Gmail compatibility** — the generated HTML uses table-based layout with inline styles and base64-embedded images, following email HTML best practices.
- The `storage/` directory (uploads, extracted data, generated HTML) is excluded from the project zip — it is created automatically at runtime.
