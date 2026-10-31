# LexAI – Persistent Document Storage Setup Guide (Cloudinary & Local Storage)

This document explains how persistent file storage is handled in **LexAI** and how to configure **Cloudinary** for production deployment on Vercel.

---

## 1. Why Cloud Storage is Essential for Vercel

Vercel Functions are serverless containers. While they offer a temporary `/tmp` directory (up to 500 MB), **any file written to the local filesystem is ephemeral and deleted when the container terminates or recycles**.

If an application saves uploaded PDFs or DOCXs only to a local `uploads/` directory, those files will disappear shortly after upload, causing subsequent re-analysis, retrieval, or viewing to fail.

To resolve this, LexAI includes a pluggable storage abstraction layer in `services/storage_service.py` that seamlessly switches between:
* **`local` mode:** Used during local development. Files are saved in `uploads/{user_id}/{document_id}/{filename}`.
* **`cloudinary` mode:** Used in production on Vercel. Uploads are securely streamed to Cloudinary's raw asset storage, and a permanent HTTPS URL is saved in MySQL.

---

## 2. Setting Up Cloudinary (Free Tier)

Cloudinary provides a generous free tier that includes 25 GB of managed storage with no credit card required.

### Step-by-Step Account Creation:
1. Go to [https://cloudinary.com/](https://cloudinary.com/) and click **Sign Up for Free**.
2. Complete registration.
3. Once logged in to the **Cloudinary Console**, navigate to your **Dashboard**.
4. In the **Product Environment Credentials** box, you will find:
   * **Cloud Name**
   * **API Key**
   * **API Secret**
   * **API Environment Variable** (formatted as `CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>`)
5. Copy the **API Environment Variable** (`CLOUDINARY_URL`).

---

## 3. Configuring LexAI for Cloud Storage

### In Vercel:
In your Vercel Project Settings -> **Environment Variables**, add:
* `STORAGE_PROVIDER`: `cloudinary`
* `CLOUDINARY_URL`: `cloudinary://<api_key>:<api_secret>@<cloud_name>`

*(Alternatively, you can provide `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` as separate variables).*

### In Local Development (`.env`):
If testing Cloudinary locally:
```bash
STORAGE_PROVIDER=cloudinary
CLOUDINARY_URL=cloudinary://1234567890:abcdefghijklmnopqrstuvwxyz@my-cloud-name
```
If working offline or locally without Cloudinary:
```bash
STORAGE_PROVIDER=local
```
*(If `STORAGE_PROVIDER=cloudinary` is set but credentials are missing, LexAI automatically and gracefully falls back to local storage).*

---

## 4. How Document Uploads & Extractions Work Under the Hood

```
[User Browser] 
       │ (Uploads PDF/DOCX)
       ▼
[Flask Route: /upload]
       │
       ▼
[services/document_service.py] ──> Validates extension (.pdf, .docx) & checks size (<= 15MB)
       │
       ▼
[services/storage_service.py] 
       ├──> If STORAGE_PROVIDER == 'cloudinary':
       │       Uploads raw bytes to Cloudinary ('lexai_uploads/user_{id}/{doc_id}/{filename}')
       │       Returns secure HTTPS URL and unique cloud public_id
       │       Saves temporary copy in /tmp for immediate text extraction
       │
       └──> If STORAGE_PROVIDER == 'local':
               Saves to uploads/{user_id}/{document_id}/{filename}
       │
       ▼
[Text Extraction Engine]
       ├──> PyMuPDF extracts text from bytes/stream
       └──> python-docx extracts paragraphs and tables
       │
       ▼
[MySQL Database]
       └──> Stores extracted text, word count, metadata, and persistent cloud file_path
```

---

## 5. Security & Isolation Guarantees

1. **User Isolation:** Each uploaded document is prefixed with the authenticated `user_id` both in cloud storage (`lexai_uploads/user_{user_id}/...`) and on disk.
2. **Access Verification:** All analysis, chat, indexing, and deletion endpoints enforce strict ownership checks:
   ```python
   if doc.user_id != current_user.id and current_user.role != 'admin':
       abort(403)
   ```
3. **Clean Cascade Deletion:** When a document is deleted via `/delete/<id>`, `delete_document_file` destroys the asset in Cloudinary, purges local cached copies, and deletes the MySQL record and ChromaDB vectors.
