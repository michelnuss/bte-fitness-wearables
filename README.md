# BTE Fitness Wearables

E-commerce style site with a FastAPI backend and static frontend. The chat assistant uses **Google Gemini** (see **GOOGLE_CLOUD_SETUP.md**). The API key stays on the server; the browser only calls `/api/chat`.

## Prerequisites

- **Python 3.10+**
- A **Google Gemini API key** (Google AI Studio) — see **GOOGLE_CLOUD_SETUP.md**
- A **`backend/.env`** file with `GOOGLE_API_KEY` (see below)

## Run the app locally (step by step)

### 1. Open a terminal and go to the backend folder

```bash
cd "/path/to/bte project/backend"
```

Replace `/path/to/bte project` with the folder where you cloned or copied this project.

### 2. (Recommended) Create and activate a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt):**

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

If your machine uses a private PyPI mirror and installs fail with SSL errors, install from the public index:

```bash
pip install --index-url https://pypi.org/simple/ --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### 4. Configure environment variables

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Edit **`backend/.env`** and set your Gemini key:

   ```env
   GOOGLE_API_KEY=your_key_here
   ```

Full setup (API enablement, key restrictions, optional Vertex notes) is in **GOOGLE_CLOUD_SETUP.md**.

### 5. Start the server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

- `--reload` restarts the server when you change Python files (needed after editing `knowledge_base.txt`).

### 6. Open the site

In your browser, go to:

**http://localhost:8000**

Product pages and cart work without Gemini. The floating **BTE Fitness Assistant** needs step 4.

## Troubleshooting

| Issue | What to try |
| --- | --- |
| Chat returns a server error about `GOOGLE_API_KEY` | Ensure `backend/.env` exists and contains a valid key (see **GOOGLE_CLOUD_SETUP.md**). |
| Model not found | Set `GEMINI_MODEL=gemini-1.5-flash` (or another model your account supports). |
| `pip` SSL / certificate errors | Use the alternate `pip install` command in step 3, or fix certificates for your Python install (on macOS, run the “Install Certificates” command that ships with python.org installers). |
| Port 8000 already in use | Stop the other process or run: `uvicorn app:app --host 0.0.0.0 --port 8001 --reload` and open `http://localhost:8001`. |

## Project layout

- `backend/` — FastAPI app (`app.py`), `products.json`, `knowledge_base.txt`, `.env`
- `backend/rag_data/` — **RAG sources**: `structured/store_info.json`, `unstructured/policies_and_faq.txt`, `website/site_snapshot.md` — keep in sync with the shop; see **GCP_RAG_GUIDE.md**
- After changing **`products.json`**, run **`python generate_knowledge_base.py`** in `backend/` so **`knowledge_base.txt`** matches the storefront.
- `frontend/` — HTML, CSS, JS (served by FastAPI). **`/assistant.html`** — full-page AI chat (products, pricing, HQ, contact).
- **GOOGLE_CLOUD_SETUP.md** — step-by-step Google / Gemini configuration
- **GCP_RAG_GUIDE.md** — how website + structured + unstructured data map to GCP and this repo
- **GCP_DEPLOY.md** — deploy the store + chat agent to **Cloud Run** (your “Google Cloud website”)
- **VERTEX_UPLOAD_AGENT_GUIDE.md** — **Vertex AI Search + Agent Builder**: upload files / website (like Azure), index (“train”), use a hosted agent

## Publish to GitHub safely

Secrets must **not** appear in the repository. This project is set up so the following stay local:

| Item | Notes |
| --- | --- |
| `backend/.env` | Listed in `.gitignore`. Contains `GOOGLE_API_KEY`. |
| `deploy.zip` / `*.zip` | Ignored (deployment bundles may include credentials). |
| API keys | Do not paste keys into code, README, or issues. Use env vars or GitHub **Secrets** for CI/CD. |

**Template for collaborators:** copy `backend/.env.example` to `backend/.env` and fill in your own values.

**First-time push (replace `YOUR-USER` and `YOUR-REPO`):**

```bash
cd "/path/to/bte project"
git init
git add .
git status   # confirm backend/.env and deploy.zip are NOT listed
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
git push -u origin main
```

Create the empty repository on GitHub first (**Repositories** → **New**), then run the commands above.

If you ever committed a secret by mistake, remove it from git history (e.g. `git filter-repo` or BFG) and **rotate** the key in Google Cloud.

## Production

Set **`GOOGLE_API_KEY`** (or your host’s secret equivalent) in the deployment environment. Do not expose the key to the browser. If you use **Vertex AI** with a service account instead of an AI Studio key, you will need additional code changes (see **GOOGLE_CLOUD_SETUP.md**).
