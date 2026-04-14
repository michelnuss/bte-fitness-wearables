# Google Cloud / Gemini setup for the BTE Fitness Assistant

The chat widget calls your FastAPI backend (`POST /api/chat`), which uses **Google Gemini** with the **Google AI Studio API key** (simplest path). Answers are grounded with `backend/knowledge_base.txt` (same idea as uploading a catalog to an Azure agent).

---

## Option A — Google AI Studio (recommended to start)

Use this for local development and small deployments. Billing and quotas are tied to your Google account / Cloud project when you enable billing.

### 1. Open Google AI Studio

Go to **[Google AI Studio](https://aistudio.google.com/)** and sign in with your Google account.

### 2. Create an API key

1. Click **Get API key** (or open the key menu from the left sidebar).
2. Choose **Create API key in new project** (or attach the key to an existing Google Cloud project).
3. Copy the key and store it somewhere safe (you will not be able to see it again in full on some screens).

### 3. Restrict the key (recommended)

In [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Credentials**:

- Edit the API key.
- Under **API restrictions**, restrict to **Generative Language API** (or the APIs your team uses).
- Under **Application restrictions**, for production use HTTP referrers or IP restrictions as appropriate.

**Note:** The key is used **only on your server** (`GOOGLE_API_KEY` in `backend/.env`), never in the browser.

### 4. Enable the Generative Language API

In the same Google Cloud project:

1. Go to **APIs & Services** → **Library**.
2. Search for **Generative Language API**.
3. Click **Enable**.

If the API is not enabled, Gemini calls from the backend will fail with permission or API-not-enabled errors.

### 5. Configure this project

1. Copy the example env file:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env`:

   ```env
   GOOGLE_API_KEY=paste_your_key_here
   ```

3. Optional — pick a model (default is `gemini-2.5-flash`; `gemini-2.0-flash` is not available to new API users):

```env
GEMINI_MODEL=gemini-2.5-flash
```

   If a model is unavailable in your region or account, try `gemini-1.5-flash` or check [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini).

4. Install dependencies and run the app (see **README.md**).

5. Open the site and use the floating **BTE Fitness Assistant** chat.

---

## Option B — Vertex AI (enterprise / GCP-only)

If your organization requires **Vertex AI** instead of the AI Studio key:

1. Create or select a **Google Cloud project**.
2. Enable **Vertex AI API**.
3. Create a **service account** with a role that can call Vertex (for example **Vertex AI User**).
4. Download a JSON key file and set `GOOGLE_APPLICATION_CREDENTIALS` to its path, **or** use Workload Identity on GKE / Cloud Run.

The current codebase uses the **`google-generativeai`** package with **`GOOGLE_API_KEY`** (AI Studio). Moving to Vertex typically means switching to the Vertex SDK and `vertexai` + IAM; that is a separate code change if you need it later.

---

## Product knowledge (replacing Azure “file search”)

In Azure you attached a file to the agent. Here, the same catalog text lives in:

- `backend/knowledge_base.txt`

To refresh it after you change products:

1. Update `products.json` or run `backend/generate_knowledge_base.py` if you use that script.
2. Restart the API server so Gemini reloads the system instructions.

---

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `GOOGLE_API_KEY not configured` | `backend/.env` exists and contains `GOOGLE_API_KEY=...` |
| `API key not valid` / 400 from Google | Key copied correctly; correct GCP project; Generative Language API enabled |
| `404` / model not found | Set `GEMINI_MODEL` to a model name available for your account (e.g. `gemini-1.5-flash`) |
| `401` / `ACCESS_TOKEN_TYPE_UNSUPPORTED` on `generativelanguage.googleapis.com` | The app forces **Google AI Studio** auth (`vertexai=False`). This happens if the SDK used **OAuth** instead of your **API key** (common on **Cloud Run** when ADC is present). Ensure **`GOOGLE_API_KEY`** is set on the service; the code uses `genai.Client(api_key=..., vertexai=False)`. |
| Empty or blocked reply | Rephrase the prompt; Gemini may block some outputs (safety). |

---

## Security checklist

- Never commit `backend/.env` or API keys to Git.
- Rotate the key if it was ever exposed.
- Use **GitHub Actions secrets** or your host’s secret store for `GOOGLE_API_KEY` in production.
