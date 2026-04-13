# BTE Fitness Wearables — Azure & Google Cloud Setup Guide

---

## Part A: Azure App Service Deployment

### Step 1: Create the App Service

1. Go to [portal.azure.com](https://portal.azure.com) and sign in.
2. Click **"Create a resource"** → search **"Web App"** → click **Create**.
3. Fill in the form:
   - **Subscription**: your subscription
   - **Resource Group**: click **"Create new"** → name it `bte-fitness-rg`
   - **Name**: `bte-fitness` (this becomes `bte-fitness.azurewebsites.net`)
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: pick the closest to your users
   - **Pricing plan**: select **Free (F1)** for testing, or **Basic (B1)** for production

> **BILLING FLAG**: The **Free (F1)** tier is genuinely free. The **B1** tier costs ~$13/month. If you select B1 or higher, billing will apply immediately.

4. Click **Review + create** → **Create**. Wait for deployment to finish (~1–2 min).

### Step 2: Configure the Startup Command

1. Go to your App Service → **Settings** → **Configuration**.
2. Click the **"General settings"** tab.
3. In the **"Startup Command"** field, enter:
   ```
   bash /home/site/wwwroot/startup.sh
   ```
4. Click **Save** at the top.

### Step 3: Set Environment Variables (if needed)

1. Still on **Configuration** → **"Application settings"** tab.
2. Click **"+ New application setting"** for each variable you need. For this project, no secrets are required, but if you later add payment APIs or database connections, add them here.
3. Useful setting to add:
   - Name: `WEBSITES_PORT`, Value: `8000` (tells Azure which port your app listens on)
4. Click **Save**.

### Step 4: Deploy via GitHub Actions

1. Push this project to a GitHub repository.
2. In the Azure Portal, go to your App Service → **Deployment Center**.
3. Under **Source**, select **GitHub**. Authorize Azure to access your GitHub account.
4. Select your repo and branch (`main`). Azure will auto-create a workflow file — you can use the one already in `.github/workflows/deploy.yml` instead.
5. Alternatively, deploy manually with the publish profile:
   - Go to App Service → **Overview** → click **"Download publish profile"**.
   - In GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`, Value: paste the downloaded XML.
   - Also add a **Repository variable** (not secret): Name: `AZURE_WEBAPP_NAME`, Value: `bte-fitness` (your app name).
6. Push to `main` — the GitHub Action will deploy automatically.

### Step 5: Deploy via Azure CLI (alternative to GitHub Actions)

```bash
# Install Azure CLI if needed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login
az login

# Create resource group (skip if already created via portal)
az group create --name bte-fitness-rg --location eastus

# Create app service plan (F1 = free)
az appservice plan create \
  --name bte-fitness-plan \
  --resource-group bte-fitness-rg \
  --sku F1 \
  --is-linux

# Create web app
az webapp create \
  --name bte-fitness \
  --resource-group bte-fitness-rg \
  --plan bte-fitness-plan \
  --runtime "PYTHON:3.11"

# Set startup command
az webapp config set \
  --name bte-fitness \
  --resource-group bte-fitness-rg \
  --startup-file "bash /home/site/wwwroot/startup.sh"

# Set port
az webapp config appsettings set \
  --name bte-fitness \
  --resource-group bte-fitness-rg \
  --settings WEBSITES_PORT=8000

# Deploy from local folder (zip deploy)
cd "/path/to/bte-project"
zip -r deploy.zip backend/ frontend/ startup.sh
az webapp deploy \
  --name bte-fitness \
  --resource-group bte-fitness-rg \
  --src-path deploy.zip \
  --type zip
```

> **BILLING FLAG**: `--sku F1` is free. If you use `B1` or higher, billing applies.

---

## Part B: Azure Blob Storage for Product Images

### Step 1: Create a Storage Account

1. In Azure Portal → **"Create a resource"** → search **"Storage account"** → **Create**.
2. Fill in:
   - **Resource group**: `bte-fitness-rg`
   - **Storage account name**: `btefitnessstorage` (lowercase, no hyphens)
   - **Region**: same as your App Service
   - **Performance**: Standard
   - **Redundancy**: LRS (Locally Redundant — cheapest)
3. Click **Review + Create** → **Create**.

> **BILLING FLAG**: Storage accounts are pay-as-you-go. For a few product images (< 1 GB), the cost is typically under $0.01/month. However, a billing method (credit card) must be on file.

### Step 2: Create a Container with Public Access

1. Go to your storage account → **Data storage** → **Containers**.
2. Click **"+ Container"**.
   - **Name**: `product-images`
   - **Anonymous access level**: **Blob (anonymous read access for blobs only)**

> **NOTE**: If the "Anonymous access level" dropdown is grayed out, go to **Storage account** → **Settings** → **Configuration** → set **"Allow Blob anonymous access"** to **Enabled** → **Save**. Then retry creating the container.

3. Click **Create**.

### Step 3: Upload Images

1. Click into the `product-images` container.
2. Click **"Upload"** → select your product image files → **Upload**.
3. After upload, click on each blob to see its **URL**, which looks like:
   ```
   https://btefitnessstorage.blob.core.windows.net/product-images/ankletrack-pro.jpg
   ```
4. Copy each URL and paste it into the corresponding product's `image_url` field in `backend/products.json`.
5. Redeploy after updating the JSON.

---

## Part C: Google Cloud AI Agent

See the detailed instructions below for setting up a Dialogflow CX or Vertex AI Agent Builder agent.

### Step 1: Enable Google Cloud APIs

1. Go to [console.cloud.google.com](https://console.cloud.google.com).
2. Create a new project or select an existing one.
3. Go to **APIs & Services** → **Enable APIs**.
4. Enable:
   - **Dialogflow API**
   - **Vertex AI Agent Builder** (if using Agent Builder instead of Dialogflow CX)

> **BILLING FLAG**: Google Cloud requires a billing account. Dialogflow CX offers a free tier of 100 text requests/month. Beyond that, charges apply (~$0.007/request). You must link a billing account before enabling APIs.

> **IAM FLAG**: You need the **Dialogflow API Admin** role (or **Owner**) on the project to create agents.

### Step 2: Generate the Knowledge Base

Run the included script to auto-generate a text file from `products.json`:

```bash
cd backend
python generate_knowledge_base.py
```

This creates `knowledge_base.txt` — a human-readable document the AI agent uses to answer product questions.

### Step 3: Create the Agent (Dialogflow CX)

1. Go to [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx).
2. Select your project → click **"Create Agent"**.
   - **Display name**: `BTE Fitness Assistant`
   - **Location**: pick your region
   - **Default language**: English
3. Click **Create**.

#### Add the Knowledge Base (Data Store)

1. In the agent, go to **Manage** → **Data Stores** → **"Create Data Store"**.
2. Select **"Unstructured documents"** → **Upload** → select `knowledge_base.txt`.
3. Name the data store `Product Catalog` → **Create**.
4. Go to the **Start** flow → **Start Page** → add a **Route** with:
   - **Condition**: `true` (default fallback)
   - **Fulfillment**: enable **"Data Store"** → select `Product Catalog`
   - This lets the agent answer any question using the knowledge base.

#### Alternative: Vertex AI Agent Builder

1. Go to [Agent Builder Console](https://console.cloud.google.com/gen-app-builder).
2. Click **"Create App"** → select **"Chat"**.
3. **App name**: `BTE Fitness Assistant`
4. Under **Data Stores**, click **"Create Data Store"** → **"Cloud Storage"** or **"Upload"**.
5. Upload `knowledge_base.txt` → create the data store.
6. Link the data store to your app → **Create**.

### Step 4: Embed the Agent in the Website

#### Option A: Dialogflow CX Messenger (recommended)

1. In Dialogflow CX → your agent → **Manage** → **Integrations** → **Dialogflow CX Messenger**.
2. Click **Enable** → **Connect**.
3. Copy the provided `<df-messenger>` snippet. It looks like this:

```html
<link rel="stylesheet" href="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/themes/df-messenger-default.css">
<script src="https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js"></script>
<df-messenger
  project-id="YOUR_PROJECT_ID"
  agent-id="YOUR_AGENT_ID"
  language-code="en"
  max-query-length="-1">
  <df-messenger-chat-bubble chat-title="BTE Fitness Assistant">
  </df-messenger-chat-bubble>
</df-messenger>
<style>
  df-messenger {
    z-index: 999;
    position: fixed;
    bottom: 16px;
    right: 16px;
  }
</style>
```

4. Paste this snippet just before `</body>` in each of your HTML files (index.html, product.html, cart.html, checkout.html).

#### Option B: Vertex AI Agent Builder Widget

1. In Agent Builder → your app → **Integration** → **Widget**.
2. Copy the provided embed code (similar `<script>` + `<iframe>` snippet).
3. Paste into your HTML files before `</body>`.

### Step 5: Test the Agent

After embedding, visit your Azure-hosted site. The chat widget should appear in the bottom-right corner. Test with questions like:

- "What does the ankle monitor track?"
- "How much is shipping to Texas?"
- "What's the cheapest product?"
- "Tell me about the smart ring"
- "Which products have GPS?"

### Keeping the Knowledge Base in Sync

Whenever you update `products.json`, re-run:

```bash
python generate_knowledge_base.py
```

Then re-upload `knowledge_base.txt` to your Dialogflow CX data store (Manage → Data Stores → select store → re-upload the file).

---

## Quick Reference: What Requires Billing

| Resource | Free? | Cost if not free |
|----------|-------|-----------------|
| Azure App Service F1 | Yes | — |
| Azure App Service B1 | No | ~$13/month |
| Azure Blob Storage (< 1 GB) | Practically free | < $0.01/month, but billing method required |
| Google Cloud Dialogflow CX | 100 requests/month free | ~$0.007/request after |
| Google Cloud Vertex AI Agent Builder | Trial credits may apply | Varies |

---

## Quick Reference: Required Permissions

| Action | Azure Role Needed | Google Cloud Role Needed |
|--------|-------------------|--------------------------|
| Create App Service | Contributor on subscription | — |
| Create Storage Account | Contributor on subscription | — |
| Download Publish Profile | Contributor on App Service | — |
| Create Dialogflow Agent | — | Dialogflow API Admin |
| Enable APIs | — | Project Editor or Owner |
