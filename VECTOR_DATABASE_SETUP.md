# LexAI – Vector Database & RAG Architecture Setup Guide

This document explains the Retrieval-Augmented Generation (RAG) architecture in **LexAI**, how it solves the Vercel serverless bundle constraints, and how to configure vector storage in production.

---

## 1. The Serverless Challenge with Traditional Python RAG

In traditional local development, RAG pipelines often bundle:
1. `sentence-transformers` for local embedding calculation.
2. `torch` (PyTorch) as the underlying deep learning execution engine.
3. `chromadb` with SQLite on the local filesystem.

When deploying to **Vercel Functions**, two major architectural blockers arise:
* **The 250 MB Bundle Size Limit:** PyTorch (`torch`) alone is between **800 MB and 1.5 GB** on Linux. Vercel will reject any deployment bundle exceeding 250 MB.
* **Cold Start Latency:** Loading a 1 GB transformer model from cold storage into serverless RAM takes 10–20 seconds, exceeding free-tier function execution timeouts.
* **Filesystem Ephemerality:** A local SQLite database in `chroma_db/` does not persist across stateless serverless container recycles.

---

## 2. LexAI's Dual-Mode Embedding Architecture

To solve these constraints without sacrificing any user functionality, LexAI implements a **Dual-Mode Embedding Service** in `services/embedding_service.py`:

```
                           ┌──────────────────────────────┐
                           │      User Query / Chunk      │
                           └──────────────┬───────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
      [Environment: Local Dev]                       [Environment: Vercel Cloud]
                   │                                             │
                   ▼                                             ▼
       SentenceTransformer                              Google Gemini API
       (all-MiniLM-L6-v2)                              (text-embedding-004)
        384 dimensions                                   768 dimensions
      Requires PyTorch locally                        ZERO PyTorch Dependencies!
                                                       Runs over fast HTTPS REST
```

### Automatic Mode Selection:
* In `config.py`, `EMBEDDING_PROVIDER` defaults to `'auto'`.
* When deployed on Vercel without PyTorch installed, LexAI automatically uses **Google Gemini `text-embedding-004`** via the modern `google-genai` SDK.
* This reduces the entire Python deployment bundle from **1,500 MB down to ~55 MB**, allowing Vercel to build and launch in seconds.

---

## 3. Vector Database Storage Options

LexAI's `embedding_service.py` supports two ChromaDB storage targets:

### Option A: Hosted / Remote ChromaDB (Recommended for High Scale)
You can connect LexAI to a centrally hosted ChromaDB server (e.g., hosted on Render, Railway, AWS EC2, or Chroma Cloud).
Configure these environment variables in Vercel:
```bash
CHROMA_HOST=your-chroma-service.onrender.com
CHROMA_PORT=443
CHROMA_SSL=true
```
When `CHROMA_HOST` is configured, LexAI initializes `chromadb.HttpClient(...)`, ensuring that all vector embeddings persist across every user session and deployment.

### Option B: Built-in Ephemeral ChromaDB with Deterministic Fallback (Zero Extra Cost)
If you do not want to run an external ChromaDB server, LexAI initializes `chromadb.EphemeralClient()` in serverless environments.
* In document chat mode, the document's extracted text is stored in MySQL.
* When a user initiates a question, LexAI can quickly index the document in memory for that session.
* Furthermore, if vector retrieval is unavailable, LexAI's built-in **Deterministic Knowledge Base Fallback** (`construct_fallback_response` in `services/rag_service.py`) automatically parses the relevant statutory provisions and answers the user's legal question without interruption.

---

## 4. Embedding Dimensions & Re-Indexing

| Provider | Model | Embedding Dimension | Use Case |
| :--- | :--- | :--- | :--- |
| **Google Gemini** | `text-embedding-004` | **768** | **Production on Vercel (Default)** |
| **Local HuggingFace** | `all-MiniLM-L6-v2` | **384** | **Offline Local Development** |

> [!IMPORTANT]
> If you switch between local `all-MiniLM-L6-v2` (384 dimensions) and Gemini `text-embedding-004` (768 dimensions) on an existing ChromaDB collection, ChromaDB will throw a dimensionality mismatch error.
> To prevent this, simply click **Re-index** on any document in the Analysis screen, or use the Admin panel to re-index Knowledge Base entries. LexAI will automatically clear the old vectors and re-index using the active model.

---

## 5. Multi-Tenancy & User Isolation in RAG

When querying or deleting vectors, LexAI strictly enforces user-level filtering:

```python
# Specific Document Chat:
where_filter = {
    "$and": [
        {"user_id": {"$eq": int(user_id)}},
        {"document_id": {"$eq": str(document_id)}}
    ]
}

# Deleting Vectors:
collection.delete(
    where={
        "$and": [
            {"document_id": {"$eq": str(document_id)}},
            {"user_id": {"$eq": int(user_id)}}
        ]
    }
)
```
This guarantees that no user can ever retrieve or view context from another user's private legal contracts or confidential files.
