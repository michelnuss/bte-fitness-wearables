# Deploy the BTE site + Gemini agent to Google Cloud Run

Your “agent” is the **`/api/chat`** endpoint (Gemini + RAG). Cloud Run runs the whole FastAPI app (store + chat) on GCP.

---

## Install `gcloud` on macOS (if you see `command not found`)

### Option A — Use the SDK that Homebrew already downloaded

If this path exists, add it to your shell **once** (then open a new terminal):

```bash
# Bash (~/.bash_profile or ~/.bashrc)
echo 'export PATH="/usr/local/share/google-cloud-sdk/bin:$PATH"' >> ~/.bash_profile

# zsh (~/.zshrc) — use this if Terminal says zsh at the top
echo 'export PATH="/usr/local/share/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc
```

Reload: `source ~/.bash_profile` (or `source ~/.zshrc`), then run:

```bash
gcloud --version
```

If `brew install` failed because **pip** pointed at a private index (AWS CodeArtifact) and broke `gcloud`’s virtualenv, **only unsetting env vars is not enough** if `pip.conf` still sets `index-url`. Force PyPI for that terminal session, then recreate the venv:

```bash
export PATH="/usr/local/share/google-cloud-sdk/bin:$PATH"
export PIP_INDEX_URL=https://pypi.org/simple
export PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org"
unset PIP_EXTRA_INDEX_URL
gcloud config virtualenv create --enable-virtualenv
```

If it still uses CodeArtifact, run `pip config list -v` to find the config file, or try `conda deactivate` first (Conda `(base)` can interact oddly with pip).

### Option B — Official installer (avoids some Homebrew + pip issues)

Download and run the **Google Cloud SDK** installer for macOS:  
[https://cloud.google.com/sdk/docs/install#mac](https://cloud.google.com/sdk/docs/install#mac)

Follow the prompts, then **close and reopen Terminal** and run `gcloud init`.

---

## What you need

| Item | Purpose |
| --- | --- |
| **Google Cloud account** | Billing enabled (Cloud Run has a generous free tier; see [pricing](https://cloud.google.com/run/pricing)). |
| **`gcloud` CLI** | [Install Cloud SDK](https://cloud.google.com/sdk/docs/install), then `gcloud init` and pick project + region. |
| **`GOOGLE_API_KEY`** | From [Google AI Studio](https://aistudio.google.com/) — same key as local dev. **Do not commit it**; use Cloud Run env or Secret Manager (below). |

---

## Step 1 — Enable APIs

In [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Enable APIs**:

- **Cloud Run API**
- **Artifact Registry API** (often enabled automatically when you deploy)
- **Generative Language API** (for Gemini, same as local)

Or in terminal:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com generativelanguage.googleapis.com
```

---

## Step 2 — Deploy from your laptop (source build)

From the **project root** (folder that contains `Dockerfile`):

```bash
cd "/path/to/bte project"

# One-shot: build in Cloud Build and deploy (replace PROJECT_ID and region)
gcloud run deploy bte-fitness \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_MODEL=gemini-2.5-flash" \
  --set-secrets "GOOGLE_API_KEY=google-api-key:latest"
```

If you are **not** using Secret Manager yet, use a plain env var (only for class demos — rotate the key after):

```bash
gcloud run deploy bte-fitness \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=YOUR_KEY_HERE,GEMINI_MODEL=gemini-2.5-flash"
```

After deploy, the command prints a **HTTPS URL** — open it in a browser. That is your **Google Cloud website**; the chat widget calls the same origin `/api/chat`.

---

## Step 3 — (Recommended) Store the API key in Secret Manager

1. Create a secret (paste key when prompted, end with Ctrl+D):

   ```bash
   gcloud secrets create google-api-key --replication-policy=automatic
   echo -n 'PASTE_YOUR_GEMINI_KEY_HERE' | gcloud secrets versions add google-api-key --data-file=-
   ```

2. Allow Cloud Run’s service account to read it:

   ```bash
   PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
   gcloud secrets add-iam-policy-binding google-api-key \
     --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

3. Deploy with `--set-secrets` as in Step 2 (first example).

---

## Step 4 — Verify the agent

1. Open the Cloud Run URL.
2. Use the floating chat; ask about a product from your catalog.
3. If errors: **Cloud Run** → your service → **Logs** — look for missing `GOOGLE_API_KEY`, model errors, or API not enabled.

---

## Optional: custom domain

**Cloud Run** → your service → **Manage custom domains** — follow the wizard (DNS at your registrar).

---

## How this satisfies “agent on GCP”

| Piece | Where it runs |
| --- | --- |
| Store + UI | Cloud Run container (FastAPI serves `frontend/`) |
| RAG context | Files baked into the image (`backend/rag_data/`, `knowledge_base.txt`) |
| Gemini | Called from Cloud Run using `GOOGLE_API_KEY` |

To change RAG content after deploy: edit files, **rebuild and redeploy** (or mount GCS later for advanced setups).

---

## Troubleshooting

| Issue | Fix |
| --- | --- |
| Build fails | Run `gcloud auth login`; ensure Dockerfile is at repo root; check build logs in Cloud Console → Cloud Build. |
| 403 / API not enabled | Enable **Generative Language API** for the same project. |
| Model not found | Set `GEMINI_MODEL=gemini-1.5-flash` in env vars. |
| Chat works locally but not on Cloud Run | Confirm env var / secret is set on the **revision** (Cloud Run → Revisions → variables). |
