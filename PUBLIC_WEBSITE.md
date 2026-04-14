# Making this website public

This project is a **single FastAPI app** that serves the storefront and the chat API. To make it **public** means anyone on the internet can open it over **HTTPS** without VPN or localhost tricks.

The recommended approach in this repo is **Google Cloud Run**: you get a stable URL, TLS, and you keep the **Gemini API key on the server** (the browser only calls `/api/chat` on your domain).

---

## What you need first

| Requirement | Why |
| --- | --- |
| A **Google Cloud** project with **billing** enabled | Cloud Run and related APIs need a billable project (there is a generous free tier; see [Cloud Run pricing](https://cloud.google.com/run/pricing)). |
| **`gcloud` CLI** installed and logged in | Deploy and manage the service from your machine. |
| A **Gemini API key** (`GOOGLE_API_KEY`) | Same kind of key as local dev ([Google AI Studio](https://aistudio.google.com/)). Never commit it; use Cloud Run env vars or Secret Manager. |

Full CLI install, PATH fixes on macOS, and pip/CodeArtifact workarounds are in **[GCP_DEPLOY.md](GCP_DEPLOY.md)**.

---

## Recommended: deploy to Cloud Run (public HTTPS URL)

1. **From the project root** (the folder that contains `Dockerfile`), enable the APIs your project needs:

   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com generativelanguage.googleapis.com
   ```

2. **Deploy** so the service accepts anonymous web traffic and has your model + key configured:

   - **Production-style:** store the key in **Secret Manager** and map it into the service (see **[GCP_DEPLOY.md](GCP_DEPLOY.md)** Step 3). Then deploy with `--set-secrets` and `--allow-unauthenticated`.
   - **Quick demo:** set `GOOGLE_API_KEY` as an environment variable on the service (rotate the key afterward if it was exposed).

   The important flag for a **public** site is **`--allow-unauthenticated`**, which lets anyone load the homepage and use the store UI; the API key stays in Cloud Run’s environment, not in the browser.

3. When `gcloud run deploy` finishes, it prints an **HTTPS URL** (for example `https://bte-fitness-xxxxx-uc.a.run.app`). That is your public site. Open it in any browser.

4. **Optional — your own domain:** In Google Cloud Console, open **Cloud Run** → your service → **Manage custom domains** and follow the DNS steps. Details: **[GCP_DEPLOY.md](GCP_DEPLOY.md)** (“Optional: custom domain”).

5. **After you change products or RAG files:** rebuild and redeploy so the container includes updated `backend/knowledge_base.txt` and `backend/rag_data/`. See **[GCP_DEPLOY.md](GCP_DEPLOY.md)** (“How this satisfies agent on GCP”).

Copy-paste deploy examples (including `GEMINI_MODEL=gemini-2.5-flash`) live in **[GCP_DEPLOY.md](GCP_DEPLOY.md)**.

---

## Temporary public URL (not for production)

If you only need to **show the site for a few minutes** (for example a live demo from your laptop), you can tunnel local port 8000 with a tool such as **ngrok**. That exposes your machine; use a strong local setup and do not rely on it for real users. Production traffic should use **Cloud Run** (or another managed host) instead.

---

## Security checklist for a public site

- Do **not** put `GOOGLE_API_KEY` in frontend JavaScript or in any file committed to git. Use server-side env vars (Cloud Run or Secret Manager).
- Prefer **Secret Manager** for the API key on GCP; rotate keys if they were ever pasted into chat, logs, or a public repo.
- Re-read **[README.md](README.md)** (“Publish to GitHub safely”) before pushing code.

---

## Related docs

| Doc | Topic |
| --- | --- |
| **[GCP_DEPLOY.md](GCP_DEPLOY.md)** | Step-by-step Cloud Run deploy, secrets, IAM, troubleshooting |
| **[GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md)** | Gemini API key and model setup |
| **[README.md](README.md)** | Run locally, project layout, env vars |
