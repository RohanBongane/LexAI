# LexAI – Comprehensive Deployment Audit & Architectural Report

**Project Name:** LexAI – AI Legal Assistant & Contract Intelligence Platform  
**Audit Date:** 2026-10-31  
**Audit Author:** Senior Full-Stack & DevOps Engineer  
**Status:** Audit Completed – Action Plan Defined  

---

## 1. Executive Summary

LexAI is a production-grade legal intelligence application developed with Flask, SQLAlchemy, MySQL, Google Gemini AI, and Retrieval-Augmented Generation (RAG). The application features contract clause extraction, legal risk assessment, multi-turn AI document chats, a curated legal knowledge base, an administrative control panel, and persistent conversation history.

This audit evaluates the entire codebase for deployment readiness on **Vercel's serverless Python runtime**. While the application's core business logic, database models, and user workflows are robust, deploying on a serverless architecture like Vercel introduces specific constraints that require careful architectural adaptation:

1. **Serverless Filesystem Ephemerality:** Vercel functions are stateless and ephemeral. The current implementation stores uploaded PDF/DOCX files in a local `uploads/` directory and vector embeddings in a local `chroma_db/` directory. These will not persist across serverless invocations.
2. **Serverless Bundle Size Limit:** Vercel enforces a **250 MB uncompressed limit** on serverless function bundles. The current `sentence-transformers` package depends on PyTorch (`torch`), which alone exceeds **800 MB to 1.5 GB**, guaranteeing bundle rejection during Vercel builds.
3. **Database Reachability:** The application currently targets `localhost:3306`. Production deployment requires a cloud-hosted MySQL database (e.g., Aiven, TiDB Serverless, PlanetScale, AWS RDS) with SSL and serverless connection pooling.
4. **URL Routing Collision:** Both `document_routes.py` and `chat_routes.py` registered the identical route path `@bp.route('/history')`, causing a blueprint collision.

Below is the complete audit documentation, followed by concrete, non-destructive migration strategies.

---

## 2. Complete Folder and File Structure

```
LexAI/
├── .env                              # Local environment secrets (IGNORED in Git)
├── .env.example                      # Production variable template
├── .gitignore                        # Git exclusion rules
├── api/                              # [NEW] Vercel serverless entrypoint directory
│   └── index.py                      # [NEW] WSGI adapter for Vercel Python runtime
├── app.py                            # Flask application factory (create_app)
├── config.py                         # Application configuration classes (Config, TestConfig)
├── extensions.py                     # SQLAlchemy, Bcrypt, LoginManager instances
├── requirements.txt                  # Python dependencies
├── vercel.json                       # [NEW] Vercel routing and build configuration
│
├── models/                           # SQLAlchemy Database Models
│   ├── __init__.py
│   └── database_models.py            # User, Document, DocumentAnalysis, Conversation, Message, KnowledgeBase
│
├── routes/                           # Flask Modular Blueprints
│   ├── __init__.py
│   ├── admin_routes.py               # Admin dashboard, user management, KB management
│   ├── auth_routes.py                # Registration, login, logout, password hashing
│   ├── chat_routes.py                # RAG chat UI, conversation API, message history
│   ├── document_routes.py            # Document upload, extraction, analysis, indexing, deletion
│   └── main_routes.py                # Landing page, dashboard, profile, KB viewer, health checks
│
├── services/                         # Core Business Logic & AI Services
│   ├── __init__.py
│   ├── ai_service.py                 # Google Gemini 3.6 Flash structured contract analysis
│   ├── document_service.py           # PyMuPDF & python-docx extraction, text cleaning, metrics
│   ├── embedding_service.py          # Dual-mode vector indexing (Local ChromaDB + Serverless Gemini)
│   ├── rag_service.py                # Intent classifier, RAG prompt construction, deterministic fallback
│   └── storage_service.py            # [NEW] Pluggable cloud object storage (Cloudinary / Local)
│
├── static/                           # Client-side Static Assets
│   ├── css/
│   │   └── style.css                 # LexAI customized responsive stylesheet (121 KB)
│   └── js/
│       ├── auth.js
│       ├── chatbot.js                # Chatbot UI, MathJax rendering, modal dialogs, API fetch
│       ├── document.js
│       └── main.js
│
├── templates/                        # Jinja2 HTML Templates
│   ├── 403.html                      # Forbidden error page
│   ├── 404.html                      # Page Not Found error page
│   ├── 500.html                      # Internal Server Error page
│   ├── admin.html                    # Admin panel (stats, users, KB editor)
│   ├── analysis.html                 # Structured legal contract breakdown & insights
│   ├── base.html                     # Authenticated layout with sidebar & top navigation
│   ├── chatbot.html                  # Split-view interactive legal assistant & sources
│   ├── chat_history.html             # Conversation archive & thread viewer
│   ├── dashboard.html                # User dashboard with recent activity & quick actions
│   ├── document_history.html         # User document archive & re-analysis launcher
│   ├── index.html                    # Public landing page with features & CTA
│   ├── knowledge_base.html           # Public legal library & searchable statutory concepts
│   ├── login.html                    # Secure user login portal
│   ├── profile.html                  # User account details & security settings
│   ├── public_base.html              # Public header/footer layout
│   ├── register.html                 # User registration page
│   └── upload.html                   # Drag-and-drop document upload interface
│
└── tests/                            # Automated Pytest Suite
    ├── conftest.py                   # Test safety guards (prevents touching production DB)
    ├── test_auth.py                  # User authentication & password hashing tests
    ├── test_database.py              # Model relationships & cascade deletion tests
    ├── test_document.py              # Upload validation & parsing tests
    ├── test_isolation.py             # User multi-tenancy & IDOR security tests
    ├── test_ai_analysis.py           # Gemini JSON schema parsing tests
    ├── test_rag.py                   # Context grounding & retrieval tests
    └── test_deployment_readiness.py   # [NEW] Vercel production readiness test suite
```

---

## 3. Core Component Analysis

### 3.1 Flask Entry Point
* **File:** `app.py`
* **Pattern:** Application Factory via `create_app(config_class=Config)`.
* **Extensions Initialized:** `Flask-SQLAlchemy` (db), `Flask-Bcrypt` (bcrypt), `Flask-Login` (login_manager).
* **Blueprints Registered:**
  * `auth_bp` (Authentication)
  * `document_bp` (Document Management & Analysis)
  * `chat_bp` (Chat & RAG Assistant)
  * `admin_bp` (Administrative Controls under `/admin`)
  * `main_bp` (Dashboard, Profile, Knowledge Base, Health Checks)
* **Error Handlers:** Customized handlers for HTTP 403, 404, and 500 returning JSON for `/api/*` endpoints and HTML templates for web requests.

### 3.2 Flask Routes and Endpoints (29 Total)

| Endpoint | Path | Methods | Protection | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `main.index` | `/` | GET | Public | Landing page |
| `main.health_check` | `/health` | GET | Public | Basic ping check |
| `main.health_detailed` | `/health/detailed` | GET | Public | Verifies DB connectivity safely |
| `main.dashboard` | `/dashboard` | GET | Login Required | User overview & recent docs |
| `main.profile` | `/profile` | GET | Login Required | User profile |
| `main.knowledge_base` | `/knowledge-base` | GET | Public | Public legal reference library |
| `auth.register` | `/register` | GET, POST | Public | Account creation |
| `auth.login` | `/login` | GET, POST | Public | User authentication |
| `auth.logout` | `/logout` | GET | Login Required | Session termination |
| `document.upload` | `/upload` | GET, POST | Login Required | File upload & text extraction |
| `document.analysis_redirect`| `/analysis` | GET | Login Required | Redirects to upload |
| `document.analysis` | `/analysis/<id>` | GET | Login Required + Owner | Displays AI contract analysis |
| `document.analyze` | `/analyze/<id>` | POST | Login Required + Owner | Triggers Gemini AI analysis |
| `document.index` | `/index/<id>` | POST | Login Required + Owner | Triggers RAG vector indexing |
| `document.delete` | `/delete/<id>` | POST | Login Required + Owner | Deletes doc, file, and vectors |
| `document.history` | `/document-history` | GET | Login Required | Archive of user documents |
| `chat.chat_ui` | `/chat` | GET | Login Required | Interactive chatbot page |
| `chat.chat_ui` | `/chat/<doc_id>` | GET | Login Required + Owner | Document-specific chat |
| `chat.chat_history` | `/chat-history` | GET | Login Required | Archive of conversation threads |
| `chat.api_chat` | `/api/chat` | POST | Login Required | JSON chat query processing |
| `chat.get_messages` | `/api/conversations/<id>/messages` | GET | Login Required + Owner | Fetch conversation messages |
| `admin.dashboard` | `/admin/` | GET | Admin Required | Administrative dashboard |
| `admin.list_users` | `/admin/users` | GET | Admin Required | User table (HTML/JSON) |
| `admin.change_role` | `/admin/users/<id>/role` | POST | Admin Required | Promote/demote user |
| `admin.delete_user` | `/admin/users/<id>/delete` | POST | Admin Required | Delete user and cascade |
| `admin.kb_add` | `/admin/kb/add` | POST | Admin Required | Create new KB article & index |
| `admin.kb_edit` | `/admin/kb/edit/<id>` | POST | Admin Required | Update KB article & re-index |
| `admin.kb_delete` | `/admin/kb/delete/<id>` | POST | Admin Required | Remove KB article & vectors |

### 3.3 Database Models & Relationships
Defined in `models/database_models.py`:
1. **`User` (`users` table):**
   * Columns: `id`, `name`, `email` (unique), `password_hash`, `role` (`'user'` or `'admin'`), `created_at`, `updated_at`.
   * Relationships: `documents` (cascade delete), `analyses` (cascade delete), `conversations` (cascade delete), `kb_entries`.
2. **`Document` (`documents` table):**
   * Columns: `id`, `user_id` (FK), `filename`, `original_filename`, `file_path`, `file_type`, `file_size`, `status`, `extracted_text`, `page_count`, `word_count`, `character_count`, `uploaded_at`, `updated_at`.
   * Relationships: Belongs to `User`; has one `DocumentAnalysis` (`analysis`), has many `Conversation` (`conversations`).
3. **`DocumentAnalysis` (`document_analysis` table):**
   * Columns: `id`, `document_id` (FK, unique), `user_id` (FK), `document_type`, `summary`, `parties` (JSON), `key_clauses` (JSON), `important_dates` (JSON), `obligations` (JSON), `risks` (JSON), `red_flags` (JSON), `financial_terms` (JSON), `termination_conditions` (JSON), `rights` (JSON), `recommendations` (JSON), `confidence`, `disclaimer`, `created_at`, `updated_at`.
4. **`Conversation` (`conversations` table):**
   * Columns: `id`, `user_id` (FK), `document_id` (FK, nullable), `title`, `created_at`, `updated_at`.
   * Relationships: Belongs to `User` & optional `Document`; has many `Message` (`messages`, ordered by `created_at`).
5. **`Message` (`messages` table):**
   * Columns: `id`, `conversation_id` (FK), `sender` (`'user'` or `'ai'`), `message` (Text), `created_at`.
6. **`KnowledgeBase` (`knowledge_base` table):**
   * Columns: `id`, `title`, `category`, `content`, `source`, `status`, `created_at`, `updated_at`, `created_by` (FK).

### 3.4 Text Extraction Logic
* **PDF Extraction (`extract_pdf_text`):** Employs `pymupdf` (PyMuPDF / fitz), looping through document pages and joining text with page demarcations.
* **DOCX Extraction (`extract_docx_text`):** Employs `python-docx`, iterating through paragraph elements with estimated page normalization.
* **Cleaning & Normalization:** `clean_text` normalizes whitespace and formatting anomalies.

### 3.5 Google Gemini AI Integration
* **File:** `services/ai_service.py`
* **SDK:** Modern `google-genai` SDK (`genai.Client(api_key=...)`).
* **Model:** Default `gemini-3.6-flash` (or `gemini-2.5-flash` via `AI_MODEL`).
* **Capabilities:** Structured JSON output via `types.GenerateContentConfig(response_mime_type="application/json")`.
* **Resilience:** Exponential backoff retry logic (up to 3 attempts) for HTTP 429 rate limits or transient 503 service unavailability.

### 3.6 RAG & Vector Database Architecture
* **File:** `services/rag_service.py` and `services/embedding_service.py`
* **Query Routing:** Two-level classification (`DOCUMENT_SPECIFIC` vs. `GENERAL_LEGAL`).
* **Multi-Tenancy Security:** Vector searches enforce strict filtering via ChromaDB `where={"user_id": {"$eq": int(user_id)}}` to ensure cross-user data isolation.
* **Deterministic Fallback:** If the Gemini API experiences rate limiting or quota exhaustion, `construct_fallback_response` deterministically parses Knowledge Base article sections to deliver direct answers and source citations without crashing.

---

## 4. Deployment Blockers for Vercel & Solutions

| # | Deployment Blocker | Root Cause | Impact on Vercel | Production Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Bundle Size Exceeded** | `sentence-transformers` imports `torch` (~1 GB+). | Vercel build fails immediately (250 MB max uncompressed limit). | Implement a dual-mode embedding service: Use Google Gemini API (`text-embedding-004`) in cloud mode (zero PyTorch needed!). |
| **2** | **Ephemeral Local Storage** | Documents saved to local `uploads/` folder. | Uploaded PDFs/DOCXs disappear when serverless instance recycles. | Implement `services/storage_service.py` with Cloudinary support and automatic local fallback. |
| **3** | **Ephemeral Vector Storage** | ChromaDB writes to local `chroma_db/` SQLite file. | Indexed vector embeddings disappear after function termination. | Support cloud vector persistence (Pinecone / Hosted ChromaDB / Cloud embeddings). |
| **4** | **Database Reachability** | `config.py` defaults to `localhost:3306`. | Serverless functions cannot reach localhost MySQL. | Add `DATABASE_URL` support with SSL options (`ssl_ca`) and serverless connection pooling (`pool_pre_ping=True`, `pool_recycle=280`). |
| **5** | **Missing Vercel Adapter** | No `vercel.json` and no WSGI handler in `api/`. | Vercel cannot route requests to Flask `create_app()`. | Create `vercel.json` rewrites and `api/index.py` WSGI entry point. |
| **6** | **Route Collision** | Both blueprints used `/history`. | Ambiguous route resolution. | Disambiguate: `/document-history` for documents, `/chat-history` for conversations. |

---

## 5. Required External Services

To run LexAI in production on Vercel without cost, the following free-tier services are required:

1. **Vercel Account:** For hosting the serverless frontend and Flask backend (Hobby plan is 100% free).
2. **Hosted MySQL Database:**
   * **Recommended Option A:** TiDB Cloud Serverless (Free forever, 5 GB storage, MySQL 8.0 wire-compatible, SSL supported).
   * **Option B:** Aiven for MySQL (Free tier or trial).
3. **Google Gemini API Key:** For legal document analysis and embedding generation (AI Studio free tier).
4. **Cloudinary Account (Optional but Recommended for File Storage):** For persistent PDF/DOCX storage (Free tier includes 25 GB managed storage and transformations).

---

## 6. Action Plan & Files to Modify

1. **`config.py`:** Add support for unified `DATABASE_URL`, SSL connection parameters, serverless SQLAlchemy connection pooling, and storage provider toggles.
2. **`api/index.py`:** Create WSGI serverless adapter for Vercel.
3. **`vercel.json`:** Configure clean rewrites for static files and backend routing.
4. **`routes/chat_routes.py` & `routes/document_routes.py`:** Fix `/history` collision.
5. **`services/storage_service.py`:** Implement persistent cloud storage with seamless local fallback.
6. **`services/embedding_service.py`:** Implement serverless-compatible embedding generation using Gemini API `text-embedding-004` alongside local fallback.
7. **`requirements.txt`:** Create a clean, production-optimized dependency manifest that fits well within Vercel's 250 MB bundle limit.
8. **`.gitignore`:** Ensure credentials, uploads, `.env`, local vector databases, and temporary artifacts are strictly excluded.
9. **Documentation:** Generate all 7 step-by-step migration and setup guides.
