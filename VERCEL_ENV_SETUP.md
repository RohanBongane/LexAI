# Vercel Environment Variables Setup Guide for LexAI

This guide details every environment variable required to run **LexAI** in production on Vercel.

---

## 1. Where to Configure Variables in Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com/).
2. Select your imported **LexAI** project.
3. Click on the **Settings** tab at the top.
4. In the left sidebar, click **Environment Variables**.
5. Add each variable listed below, ensuring you select **Production**, **Preview**, and **Development** environments.

---

## 2. Mandatory Environment Variables

### A. Core Flask Settings
| Variable Name | Example / Recommended Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `f3a9c7b8d1e2f4a5b6c7d8e9f0123456789abcdef...` | High-entropy secret key used to sign session cookies and CSRF tokens. Generate one using `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `FLASK_ENV` | `production` | Sets the application to production mode. |
| `FLASK_DEBUG` | `False` | Disables debug mode and tracebacks in production. |
| `SESSION_COOKIE_SECURE` | `True` | Forces browser session cookies to be transmitted only over HTTPS. |

### B. Hosted MySQL Database
| Variable Name | Example / Recommended Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `mysql+pymysql://<user>:<password>@<host>:4000/<dbname>?ssl_accept=strict` | Complete connection string to your hosted cloud MySQL database (e.g., TiDB Cloud, Aiven, PlanetScale, AWS RDS). |
| `DB_SSL` | `true` | Enables SSL encryption for database traffic. |

> **Note:** If your cloud database provider gives you individual credentials instead of a single URI, you can alternatively provide:
> * `DB_USER`
> * `DB_PASSWORD`
> * `DB_HOST`
> * `DB_PORT`
> * `DB_NAME`

### C. Google Gemini AI Service
| Variable Name | Example / Recommended Value | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `AIzaSyD...` | Your secret API key from [Google AI Studio](https://aistudio.google.com/). |
| `AI_PROVIDER` | `gemini` | AI backend provider. |
| `AI_MODEL` | `gemini-3.6-flash` | The Gemini model used for legal contract analysis and query classification. |

---

## 3. Persistent Document Storage Variables (Cloudinary)

Vercel Functions run on an ephemeral filesystem (`/tmp` only). To preserve uploaded PDFs and DOCXs across deployments and serverless container lifecycles, configure Cloudinary:

| Variable Name | Example / Recommended Value | Description |
| :--- | :--- | :--- |
| `STORAGE_PROVIDER` | `cloudinary` | Activates cloud object storage mode. |
| `CLOUDINARY_URL` | `cloudinary://<api_key>:<api_secret>@<cloud_name>` | Unified Cloudinary connection URL from your Cloudinary dashboard. |

*(Alternatively, provide `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` individually).*

---

## 4. Vector & Embedding Variables

| Variable Name | Recommended Value | Description |
| :--- | :--- | :--- |
| `EMBEDDING_PROVIDER` | `gemini` (or `auto`) | Uses Google Gemini's `text-embedding-004` API to generate embeddings without bundling massive PyTorch libraries. |
| `CHROMA_HOST` | *(Optional)* | Hostname of an external hosted ChromaDB server if utilized. |
| `CHROMA_PORT` | `8000` *(Optional)* | Port of external ChromaDB server. |

---

## 5. Verification Checklist

After adding the variables in Vercel:
1. Go to the **Deployments** tab and trigger a **Redeploy**.
2. Visit `https://your-app.vercel.app/health` to confirm the application boots (`{"status": "ok", "application": "LexAI"}`).
3. Visit `https://your-app.vercel.app/health/detailed` to verify that database connectivity reports `"ok"`.
