# Master Vercel Deployment & Production Guide for LexAI

Welcome to the definitive deployment manual for **LexAI – AI Legal Assistant & Contract Intelligence Platform**.

This guide covers everything required to deploy the complete LexAI application—including frontend templates, Flask backend, hosted MySQL database, Cloudinary document storage, Google Gemini AI contract analysis, and persistent chat history—to **Vercel** with zero guesswork.

---

## 1. External Accounts Required (All 100% Free)

Before deploying, ensure you have these accounts ready:

| Account | Provider | Purpose | Free Tier Allowance | Link |
| :--- | :--- | :--- | :--- | :--- |
| **GitHub** | GitHub | Version control & Vercel deployment trigger | Unlimited public/private repos | [github.com](https://github.com/) |
| **Vercel** | Vercel | Serverless hosting for Python/Flask web app | 100% Free Hobby Tier | [vercel.com](https://vercel.com/) |
| **Cloud MySQL** | TiDB Cloud (Recommended) | Hosted MySQL database for users, docs, chat | Free Forever (5 GB storage) | [tidbcloud.com](https://tidbcloud.com/) |
| **Google AI Studio**| Google Gemini | Legal AI analysis & embeddings API key | Free tier (Generous quota) | [aistudio.google.com](https://aistudio.google.com/) |
| **Cloudinary** *(Optional)* | Cloudinary | Persistent cloud storage for uploaded documents | Free tier (25 GB storage) | [cloudinary.com](https://cloudinary.com/) |

---

## 2. Step 1: Prepare Your Cloud MySQL Database

1. Go to [https://tidbcloud.com/](https://tidbcloud.com/) and register.
2. Click **Create Cluster** -> Select **Serverless** -> Pick cloud region (e.g., `Mumbai (AWS ap-south-1)`).
3. Set a root password.
4. Once created, click **Connect** -> Choose **SQLAlchemy** or **General**.
5. Copy your connection URL. It looks like this:
   ```
   mysql+pymysql://<USER>:<PASSWORD>@gateway01.ap-south-1.prod.aws.tidbcloud.com:4000/lexai_db?ssl_accept=strict
   ```
6. *(Optional)* To import your existing local database tables and data, follow [`database_migration_guide.md`](file:///C:/Users/Rohan%20Bongane/.gemini/antigravity/scratch/LexAI/database_migration_guide.md).

---

## 3. Step 2: Get Your Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google account.
3. Click **Get API key** -> **Create API key**.
4. Copy the API key string (e.g., `AIzaSyD...`).

---

## 4. Step 3: Get Your Cloudinary Storage Credentials

1. Visit [Cloudinary](https://cloudinary.com/) and sign up.
2. In your **Cloudinary Dashboard**, locate the **API Environment Variable**.
3. Copy the string starting with:
   ```
   cloudinary://<api_key>:<api_secret>@<cloud_name>
   ```

---

## 5. Step 4: Safely Push LexAI to GitHub

Your project repository already has `.gitignore` properly configured so that `.env`, local `uploads/`, `venv/`, and `chroma_db/` are strictly excluded and will not be leaked.

Open PowerShell in `C:\Users\Rohan Bongane\.gemini\antigravity\scratch\LexAI`:

```powershell
# 1. Check git status to ensure sensitive files are not staged
git status

# 2. Stage all deployment files, documentation, and tests
git add api/ vercel.json config.py requirements.txt requirements-local.txt .gitignore
git add services/ routes/ tests/ DEPLOYMENT_AUDIT.md DEPLOYMENT_GUIDE.md VERCEL_ENV_SETUP.md
git add database_migration_guide.md STORAGE_SETUP.md VECTOR_DATABASE_SETUP.md TESTING_REPORT.md .env.example

# 3. Commit the changes
git commit -m "Configure LexAI for Vercel deployment: serverless entrypoint, cloud storage, and robust error handling"

# 4. Push to your GitHub repository
git push origin main
```

---

## 6. Step 5: Import & Deploy on Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com/).
2. Click **Add New...** -> **Project**.
3. Select your GitHub repository (`LexAI`).
4. In the **Configure Project** screen:
   * **Framework Preset:** Leave as `Other` (Vercel automatically detects `vercel.json` and Python).
   * **Root Directory:** `./`
5. Expand **Environment Variables** and enter the following keys and values:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `SECRET_KEY` | `9b3a7c8e2f1d4a5b6c7d8e9f0123456789abcdef0123456789abcdef01234567` | Any 32+ character random secret string |
| `FLASK_ENV` | `production` | Production mode |
| `FLASK_DEBUG` | `False` | Disables debug mode |
| `SESSION_COOKIE_SECURE` | `True` | Forces HTTPS cookies |
| `DATABASE_URL` | `mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<PORT>/lexai_db?ssl_accept=strict` | Your hosted cloud MySQL connection string |
| `DB_SSL` | `true` | Required for TiDB / Aiven |
| `GEMINI_API_KEY` | `AIzaSy...` | Your Google AI Studio API key |
| `AI_PROVIDER` | `gemini` | AI engine |
| `AI_MODEL` | `gemini-3.6-flash` | Gemini model |
| `STORAGE_PROVIDER` | `cloudinary` | Activates cloud storage |
| `CLOUDINARY_URL` | `cloudinary://<api_key>:<api_secret>@<cloud_name>` | Cloudinary credentials |
| `EMBEDDING_PROVIDER` | `gemini` | Generates embeddings via API (No heavy PyTorch bundle) |

6. Click **Deploy**.
7. Vercel will install dependencies, package the function, and assign you a live URL:
   ```
   https://lex-ai-your-username.vercel.app
   ```

---

## 7. Step 6: Testing & Verifying Your Live Deployment

Once Vercel reports **Deployment Complete**, test the live site in your browser:

1. **Health Verification:**
   * Visit `https://your-app.vercel.app/health` -> Expect `{"status": "ok", "application": "LexAI"}`.
   * Visit `https://your-app.vercel.app/health/detailed` -> Expect `{"checks": {"database": "ok", "chromadb": "ok"}, "status": "ok"}`.
2. **User Registration & Login:**
   * Go to `https://your-app.vercel.app/register` and create an account.
   * Log in at `https://your-app.vercel.app/login`.
   * Confirm the `/dashboard` loads with your user profile.
3. **Document Upload & AI Analysis:**
   * Go to `/upload` and upload a test NDA or contract (`.pdf` or `.docx`).
   * Click **Run AI Analysis**.
   * Confirm that structured clauses, obligations, financial terms, and risks display in `/analysis/<id>`.
4. **Interactive Legal Chatbot:**
   * Go to `/chat` and select your uploaded document.
   * Ask: *"What are the termination conditions in this agreement?"*.
   * Verify that grounded answers appear with citations.
5. **Chat History Persistence:**
   * Navigate to `/chat-history`.
   * Verify that previous conversation threads load and can be resumed.

---

## 8. Troubleshooting Common Errors

### Error: `500 Internal Server Error` on database queries
* **Cause:** The database is unreachable or credentials are wrong.
* **Fix:** Check `https://your-app.vercel.app/health/detailed`. Ensure `DB_SSL=true` is enabled in Vercel environment variables, and verify that your cloud database allows connections from all IPs (`0.0.0.0/0`).

### Error: `AI service authentication failed (401 UNAUTHENTICATED)`
* **Cause:** The `GEMINI_API_KEY` in Vercel is invalid or expired.
* **Fix:** Generate a fresh key at [Google AI Studio](https://aistudio.google.com/) and paste it into Vercel Project Settings -> Environment Variables, then click **Redeploy**.

### Error: `Vercel Function Size Exceeded (250 MB limit)`
* **Cause:** Heavy deep learning packages (like PyTorch or sentence-transformers) were included in `requirements.txt`.
* **Fix:** LexAI's `requirements.txt` has already been optimized for serverless deployment. It uses `google-genai` embeddings via API, keeping the entire function bundle under 60 MB.

### Error: Uploaded documents disappear after a few minutes
* **Cause:** `STORAGE_PROVIDER` is set to `local` instead of `cloudinary`.
* **Fix:** Add `STORAGE_PROVIDER=cloudinary` and `CLOUDINARY_URL=...` to your Vercel Environment Variables so files are stored persistently in Cloudinary.
