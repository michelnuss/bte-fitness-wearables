# Vertex AI: upload data + “agent” (like Azure file upload)

On **Azure** you uploaded files and the service **indexed** them so the assistant could retrieve answers. On **Google Cloud** the closest match is:

1. **Vertex AI Search** (product family also referred to as *Generative AI App Builder* / *Discovery Engine* in APIs) — you create **data stores**, **import** documents or a **website**, and Google **indexes** them (people often call this “training”; it is **retrieval indexing**, not fine-tuning a model).
2. **Vertex AI Agent Builder** (and related **Conversational Agents** UIs) — you attach those data stores as **tools** so a **hosted agent** answers using your content.

Yes — this path is **on Vertex AI** (and related “AI Applications” / Search consoles). Exact menu labels change; use the search box at the top of the Cloud Console if a name moved.

**Official overview:** [Vertex AI Search documentation](https://cloud.google.com/generative-ai-app-builder/docs)

---

## Before you start

| Requirement | Why |
| --- | --- |
| **Billing enabled** | Search indexing and agent hosting are not free indefinitely; there is usually a trial/credit phase. |
| **Owner or Editor** on the project | To create apps and data stores. |
| **APIs enabled** | At minimum: **Discovery Engine API** (`discoveryengine.googleapis.com`), **Vertex AI API** (`aiplatform.googleapis.com`). The Console often prompts you to enable them when you open Search / Agent Builder. |

Enable from **APIs & Services → Library** or run:

```bash
gcloud services enable discoveryengine.googleapis.com aiplatform.googleapis.com
```

---

## Step 1 — Open Vertex AI Search (create an “app”)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and select your project (e.g. `numeric-nova-491121-b3`).
2. Open the **navigation menu (☰)** → **Vertex AI** (or search the top bar for **“Vertex AI Search”** / **“Search for commerce”** / **“Search and Conversation”** — naming varies by SKU).
3. Choose the flow that creates a **Search** application (options often include **generic search**, **media**, **commerce**). Pick what matches a **Q&A / website + docs** use case.

You are creating an **app** that will own one or more **data stores**.

---

## Step 2 — Create a data store (this is where uploads happen)

A **data store** holds the content your agent will retrieve from.

1. In the Search / App Builder UI, find **Data stores** (or **Data** during app creation).
2. **Create data store** and choose the source type:

   | Your rubric | Data store type (typical) |
   | --- | --- |
   | **Unstructured** | **Unstructured documents** — upload **PDF, HTML, TXT, DOCX** (limits apply). |
   | **Structured** | **Structured data** — often **BigQuery** or **Cloud Storage** with a schema (CSV/JSONL). |
   | **Website** | **Website** — enter **root URL** or **sitemap**; Google **crawls** and indexes pages. |

3. For **uploads** similar to Azure:
   - Use **Unstructured** and **upload files**, **or**
   - Put files in a **Cloud Storage bucket** and **import** from GCS (good for large sets).

4. **Import / sync** and wait until the job shows **success**. Large sites or many files can take **hours** (your “~24h” story usually refers to big crawls or huge corpora, not a small class project).

---

## Step 3 — Indexing = “training” in the Azure sense

- There is **no separate “train model”** button for your custom files in the same way as Azure OpenAI fine-tuning.
- What happens is **indexing + embeddings** inside Google’s retrieval system so **search/grounding** can find snippets.
- Status appears in the **data store** or **operation** details — wait until indexing is **complete** before relying on answers.

---

## Step 4 — Attach the data store to an agent (Vertex Agent Builder)

1. In **Vertex AI**, open **Agent Builder** (or **Conversational Agents** / **AI Applications** — see your project’s menu).
2. **Create agent** (or open your Search app’s **agent** / **assistant** configuration).
3. Add a **tool** or **data store** connection so the agent can **query** the data store you created (wording: **“Grounding”**, **“Data store tool”**, **“Search”**).
4. Set **system instructions** (e.g. “Only answer from BTE Fitness catalog and policies”).
5. Use the **preview / playground** in the Console to test questions (contact, location, products, pricing).

You now have a **hosted agent** on GCP backed by uploaded/crawled data — analogous to Azure Foundry + knowledge.

---

## Step 5 — Your FastAPI site vs the hosted agent (important)

| What you have now in Git | What Vertex gives you |
| --- | --- |
| FastAPI calls **Gemini** with text loaded from `knowledge_base.txt` + `rag_data/` | A **separate** Search + Agent stack in GCP with **APIs** and its own endpoints |

To **replace** the Git-based RAG with Vertex Search grounding you would:

- Call **Discovery Engine / Search API** from your backend, **or**
- Call the **Agent / session API** documented for your agent type,

then pass retrieved snippets to Gemini or use the agent’s built-in response path.

That is **extra integration work**; it is not automatic when you only deploy Cloud Run with env vars.

---

## Step 6 — APIs and authentication for your app (when you integrate)

- Prefer a **service account** with roles such as **Discovery Engine Editor** / **Vertex AI User** (exact roles depend on API version — grant what the error message asks for).
- For coursework, testing in the **Console playground** often satisfies “agent on GCP with RAG”; wiring the same into Python is the stretch goal.

---

## Troubleshooting

| Issue | What to check |
| --- | --- |
| Cannot find “Agent Builder” | Search the Console for **Vertex AI Agent Builder** or **Conversational Agents**. |
| Import failed | File types, size limits, bucket permissions (GCS), or website **robots.txt** blocking crawl. |
| Empty answers | Indexing not finished; data store not attached to the agent; wrong project/region. |
| Cost / quota | **Billing → Budgets**; Search has usage-based pricing. |

---

## Quick links (bookmark these)

- [Vertex AI Search (Generative AI App Builder) docs](https://cloud.google.com/generative-ai-app-builder/docs)
- [Vertex AI Agent Builder product page](https://cloud.google.com/products/agent-builder)
- [Data stores and documents](https://cloud.google.com/generative-ai-app-builder/docs/about-media-documents) (media/doc types; similar patterns for other stores)

---

## Summary

| Question | Answer |
| --- | --- |
| Is it on **Vertex AI**? | **Yes** — Search + Agent Builder live under the Vertex / AI Applications area. |
| Is it “training”? | It’s **indexing** your files/site for **retrieval** (same *idea* as Azure upload + vector store). |
| Same as your current `gcloud run deploy` app? | **No** — that deploys **your** container. Vertex Search/Agent is **another service** you configure in the Console and optionally call from code. |
