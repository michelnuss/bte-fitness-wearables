# BTE Fitness Wearables

E-commerce style site with a FastAPI backend and static frontend. The chat assistant uses Azure AI Foundry and signs in with **Azure CLI** locally.

## Prerequisites

- **Python 3.10+**
- **Azure CLI** (`az`) — required for the BTE Fitness Assistant chat (Entra ID token). [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).
- A **`.env`** file under `backend/` with your project settings (see below).

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

Create `backend/.env` (this file is gitignored) with at least:

```env
AZURE_AI_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project-name>
AZURE_AGENT_ID=asst_xxxxxxxxxxxxxxxxxxxxxxxx
```

Copy `AZURE_AI_ENDPOINT` and `AZURE_AGENT_ID` from **Azure AI Foundry** → your project → **Overview** / **Agents**. The chat feature does **not** use the API key for agent calls; it uses Azure identity (next step).

### 5. Sign in to Azure (needed for the chat widget)

The assistant uses `DefaultAzureCredential`, which uses your **Azure CLI** login on your machine:

```bash
az login
```

Use an account that has access to the Foundry project and agent.

### 6. Start the server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

- `--reload` restarts the server when you change Python files.

### 7. Open the site

In your browser, go to:

**http://localhost:8000**

Product pages and cart work without Azure. The floating **BTE Fitness Assistant** needs steps 4–6.

## Troubleshooting

| Issue | What to try |
| --- | --- |
| Chat errors about auth or 401/403 | Run `az login` again; confirm your user can open the same project in Azure AI Foundry. |
| `pip` SSL / certificate errors | Use the alternate `pip install` command in step 3, or fix certificates for your Python install (on macOS, run the “Install Certificates” command that ships with python.org installers). |
| Port 8000 already in use | Stop the other process or run: `uvicorn app:app --host 0.0.0.0 --port 8001 --reload` and open `http://localhost:8001`. |

## Project layout

- `backend/` — FastAPI app (`app.py`), `products.json`, `.env`
- `frontend/` — HTML, CSS, JS (served by FastAPI)

## Publish to GitHub safely

Secrets must **not** appear in the repository. This project is set up so the following stay local:

| Item | Notes |
| --- | --- |
| `backend/.env` | Listed in `.gitignore`. Contains your Foundry endpoint and agent id. |
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

If you ever committed a secret by mistake, remove it from git history (e.g. `git filter-repo` or BFG) and **rotate** the key in Azure.

## Production (Azure)

On Azure App Service, configure the same environment variables as in `.env`, enable **managed identity** for the app, and grant that identity access to your Foundry project so the chat can obtain tokens without `az login`.
