# LexAI – Database Migration Guide (Local MySQL to Hosted Cloud MySQL)

This guide provides step-by-step instructions to migrate your existing local `lexai_db` MySQL database to a cloud-hosted MySQL service suitable for Vercel production deployment.

---

## 1. Choosing a Hosted MySQL Provider

For MCA final-year projects and serverless applications on Vercel, the two best free options are:

### Recommended Option: TiDB Cloud Serverless (Free Forever)
* **Website:** [https://tidbcloud.com/](https://tidbcloud.com/)
* **Why it fits:** 
  * 100% MySQL 8.0 wire-compatible (works seamlessly with SQLAlchemy & PyMySQL).
  * 5 GB free storage with zero credit card required.
  * Serverless architecture scales to zero and handles sleep/wake gracefully.
  * Full SSL encryption enabled by default.

### Alternative Option: Aiven for MySQL
* **Website:** [https://aiven.io/](https://aiven.io/)
* **Features:** Dedicated cloud MySQL instance with generous free trial credits.

---

## 2. Creating Your Cloud Database (TiDB Cloud Example)

1. Sign up at [https://tidbcloud.com/](https://tidbcloud.com/) (using your Google or GitHub account).
2. Click **Create Cluster** and select **Serverless**.
3. Choose your nearest cloud region (e.g., `AWS / ap-south-1 Mumbai` or `ap-southeast-1 Singapore`).
4. Set a cluster name (e.g., `lexai-cluster`).
5. Set a strong root password (save this securely).
6. Click **Create**. Your cluster will provision in ~20 seconds.
7. Click **Connect** -> Select **General** or **SQLAlchemy/Python**.
8. Note your connection details:
   * **Host:** e.g., `gateway01.ap-south-1.prod.aws.tidbcloud.com`
   * **Port:** `4000`
   * **User:** e.g., `<prefix>.root`
   * **Database:** `lexai_db` (or default `test`)

---

## 3. Exporting Your Local Database

Open PowerShell in your project folder and run `mysqldump` to export your local tables and data:

```powershell
# Export all tables, schema, and existing records from local MySQL
mysqldump -u root -p lexai_db > lexai_backup.sql
```
*(Enter your local MySQL password when prompted: `LexAI@2026#Root`)*

Verify that `lexai_backup.sql` was created and contains your existing tables (`users`, `documents`, `document_analysis`, `conversations`, `messages`, `knowledge_base`).

---

## 4. Importing into the Hosted Cloud Database

### Method A: Via MySQL CLI
```powershell
# Import into your hosted cloud MySQL database
mysql -h <HOST> -P <PORT> -u <USER> -p --ssl-mode=REQUIRED <DATABASE_NAME> < lexai_backup.sql
```

### Method B: Via TiDB Web SQL Editor
1. In the TiDB Cloud Console, click **SQL Editor**.
2. Run:
   ```sql
   CREATE DATABASE IF NOT EXISTS lexai_db;
   USE lexai_db;
   ```
3. Paste the contents of `lexai_backup.sql` into the editor and click **Run**.

### Method C: Automatic SQLAlchemy Initialization (Clean Schema Setup)
If you prefer to start with a fresh schema and populate your default Knowledge Base entries:
Run the built-in LexAI initialization script against the cloud database:

```powershell
# In PowerShell:
$env:DATABASE_URL="mysql+pymysql://<user>:<password>@<host>:<port>/lexai_db"
$env:DB_SSL="true"
.\venv\Scripts\python.exe -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('Cloud tables created successfully!')"
```

---

## 5. Configuring the Production Connection String

In Vercel (or in your local `.env`), set `DATABASE_URL`:

```bash
DATABASE_URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<PORT>/lexai_db?ssl_accept=strict
DB_SSL=true
```

LexAI's `config.py` automatically detects this URL, applies the required `mysql+pymysql` driver dialect, and configures serverless pooling:
* `pool_pre_ping=True`: Tests connections before executing queries to prevent `"MySQL server has gone away"` errors.
* `pool_recycle=280`: Refreshes connections before provider idle timeouts drop them.
* `pool_timeout=20`: Prevents serverless functions from hanging indefinitely on stalled networks.

---

## 6. Verifying Connectivity

Test the cloud connection using Python:

```powershell
.\venv\Scripts\python.exe -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); result = db.session.execute(db.text('SELECT 1')).scalar(); print('Database connection test successful:', result == 1)"
```

When deployed to Vercel, navigate to:
`https://your-lexai-app.vercel.app/health/detailed`

Expected Response:
```json
{
  "application": "LexAI",
  "checks": {
    "database": "ok",
    "chromadb": "ok"
  },
  "status": "ok"
}
```
