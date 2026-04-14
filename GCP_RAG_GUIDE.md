# GCP RAG: three data types for your customer agent

Your rubric asks for **RAG** fed by **website**, **structured**, and **unstructured** data, covering **services**, **contact**, **location**, **products**, and **pricing**.

Below is how that maps to Google Cloud and to this repo.

---

## 1. What each data type means (and how to satisfy it)

| Type | What it is | Examples for BTE | Typical GCP options |
| --- | --- | --- | --- |
| **Structured** | Rows/columns, easy to query | `products.json`, CSV exports, store hours in JSON, pricing tables | **BigQuery** tables, **Cloud SQL**, JSON/CSV in **Cloud Storage**, or files in-repo for demos |
| **Unstructured** | Free text, PDFs, docs | FAQs, return policy, long-form product blurbs, PDF manuals | **Cloud Storage** buckets (PDF/DOCX/TXT), or `.txt`/`.md` in-repo; **Vertex AI Search** can index these |
| **Website** | Public site content | About, shipping page, contact page | **URL ingestion** in Vertex AI Search / periodic **export** of HTML→text into GCS, or **static snapshots** (markdown) checked into `rag_data/website/` (valid for coursework if you document that the snapshot mirrors the live site) |

**Coverage check for the five categories:**

| Category | Where it usually lives |
| --- | --- |
| **a. Any service** | Unstructured (FAQ, “Services” page text) + optional structured (service codes in JSON) |
| **b. Contact** | Structured (`phone`, `email`, `support_hours`) or website snapshot |
| **c. Location** | Structured (`address`, `warehouse_region`) + website “About / Contact” |
| **d. Product** | Structured catalog (`products.json`) + `knowledge_base.txt` / embeddings |
| **e. Pricing** | Structured (price fields) + shipping tiers in text/JSON |

---

## 2. Two ways to build it on GCP

### Path A — **Course project / app-integrated RAG** (what this repo does)

1. Keep **three folders** under `backend/rag_data/` (see below).
2. At request time (or at server startup), **load + merge** those sources into the **system prompt** (or into retrieved chunks) and call **Gemini** (`GOOGLE_API_KEY`).
3. **Pros:** Simple to explain, no mandatory Vertex Search bill. **Cons:** Not “Google-managed vector search”; you document ingestion clearly in the report.

This satisfies **RAG** in the sense: *retrieve relevant knowledge from multiple corpora, then generate*. For a stricter “vector DB” story, add Path B later.

### Path B — **Full GCP-native RAG** (stronger “GCP platform” story)

1. **Upload** structured + unstructured + website exports to **Cloud Storage**.
2. Use **Vertex AI Search** (or **Vertex AI RAG Engine** with a **Vertex AI Vector Search** index) to index those objects and/or **BigQuery** for structured facets.
3. Build a **Vertex AI Agent** (or your FastAPI app) that **queries** the search API and passes **snippets** to **Gemini** on Vertex with a **service account** (not only API key).

**Pros:** Aligns with “agent on GCP + enterprise RAG.” **Cons:** More console setup, billing, IAM.

Official starting points:

- [Vertex AI Search](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction) — website + unstructured document stores.
- [Vertex AI RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview) — connect data stores to Gemini.

---

## 3. This repository: three on-disk sources

`backend/app.py` merges these into the Gemini **system instruction** (simple RAG: all relevant corpora in context; tune to chunking/embeddings later if required):

1. **`knowledge_base.txt`** — catalog + shipping/discounts (generated from `products.json`); covers **products** + **pricing** heavily.
2. **`rag_data/structured/*.json`** — e.g. **`store_info.json`**: **contact**, **location**, **services** in structured form.
3. **`rag_data/unstructured/*.txt`** (and `.md`) — policies, FAQs (unstructured).
4. **`rag_data/website/*.md`** (and `.txt`/`.html`) — **snapshots** of web-style content (mirror of pages you would host).

Edit these files as your store evolves. Regenerate `knowledge_base.txt` after catalog changes:

```bash
cd backend && python generate_knowledge_base.py
```

---

## 4. What to write in your report / demo script

1. **Diagram:** User → FastAPI → (retrieve from 3 corpora) → Gemini → reply.  
2. **Table:** Each rubric row mapped to a file or GCS path.  
3. **If using Path B:** Screenshot Vertex Search data store + query, and explain IAM + service account.

---

## 5. Security

- Do not commit real API keys; use `backend/.env` and **Secret Manager** in production.
- If you crawl a real website, respect **robots.txt** and terms of service; for class, **owner-provided** snapshots are safest.
