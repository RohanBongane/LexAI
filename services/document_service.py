import os
import io
import urllib.request
import pymupdf  # PyMuPDF
from docx import Document as DocxDocument
from werkzeug.utils import secure_filename
from models.database_models import Document
from extensions import db

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file):
    if not file or file.filename == '':
        return False, "No selected file"
    if not allowed_file(file.filename):
        return False, "Invalid file type. Only PDF and DOCX are allowed."
    return True, None

def get_file_bytes(filepath_or_url):
    """Retrieves file bytes from local disk or remote HTTP/HTTPS URL."""
    if filepath_or_url.startswith(('http://', 'https://')):
        req = urllib.request.Request(filepath_or_url, headers={'User-Agent': 'LexAI-Serverless/1.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()
    else:
        with open(filepath_or_url, 'rb') as f:
            return f.read()

def save_uploaded_file(file, user_id, upload_folder=None):
    """
    Saves the file using the pluggable storage service (Cloudinary or Local disk).
    Creates an initial database record.
    """
    original_filename = file.filename
    safe_filename = secure_filename(original_filename)
    file_type = safe_filename.rsplit('.', 1)[1].lower()
    
    from services.storage_service import save_document_file
    
    storage_meta = save_document_file(file, user_id)
    
    # Store the primary persistent path (or URL)
    new_doc = Document(
        user_id=user_id,
        filename=safe_filename,
        original_filename=original_filename,
        file_path=storage_meta["file_path"],
        file_type=file_type,
        file_size=storage_meta["file_size"],
        status='processing'
    )
    db.session.add(new_doc)
    db.session.commit()
    
    # Stash the temp local path on the document object in memory if available for immediate processing
    if storage_meta.get("temp_local_path"):
        new_doc._temp_local_path = storage_meta["temp_local_path"]
        
    return new_doc

def clean_text(text):
    """Cleans extracted text to remove excessive whitespace."""
    if not text:
        return ""
    return " ".join(text.split())

def extract_pdf_text(filepath_or_url):
    """Extracts text from a PDF file using PyMuPDF (supports disk path, memory stream, or remote URL)."""
    text_content = ""
    page_count = 0
    doc = None
    try:
        if filepath_or_url.startswith(('http://', 'https://')):
            file_bytes = get_file_bytes(filepath_or_url)
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        elif os.path.exists(filepath_or_url):
            doc = pymupdf.open(filepath_or_url)
        else:
            return False, "File path does not exist", 0

        page_count = len(doc)
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"
        doc.close()
        return True, clean_text(text_content), page_count
    except Exception as e:
        if doc:
            try:
                doc.close()
            except Exception:
                pass
        print(f"Error extracting PDF text: {e}")
        return False, "", 0

def extract_docx_text(filepath_or_url):
    """Extracts text from a DOCX file using python-docx (supports disk path or remote URL)."""
    text_content = ""
    try:
        if filepath_or_url.startswith(('http://', 'https://')):
            file_bytes = get_file_bytes(filepath_or_url)
            doc = DocxDocument(io.BytesIO(file_bytes))
        elif os.path.exists(filepath_or_url):
            doc = DocxDocument(filepath_or_url)
        else:
            return False, "File path does not exist", 0

        for para in doc.paragraphs:
            if para.text.strip():
                text_content += para.text + "\n"
        words = len(text_content.split())
        page_count = max(1, words // 500)
        return True, clean_text(text_content), page_count
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return False, "", 0

def analyze_document_statistics(text, page_count):
    """Calculates document statistics."""
    word_count = len(text.split())
    character_count = len(text)
    return {
        "page_count": page_count,
        "word_count": word_count,
        "character_count": character_count
    }

def process_document(document_id):
    """Main pipeline for text extraction and vector indexing."""
    doc = db.session.get(Document, document_id)
    if not doc:
        return False
        
    try:
        # Check if an in-memory or temp path exists first, else use doc.file_path
        target_path = getattr(doc, '_temp_local_path', None) or doc.file_path
        
        # Extract text based on file type
        if doc.file_type == 'pdf':
            success, text, page_count = extract_pdf_text(target_path)
        elif doc.file_type == 'docx':
            success, text, page_count = extract_docx_text(target_path)
        else:
            success = False
            
        if success and text:
            stats = analyze_document_statistics(text, page_count)
            doc.extracted_text = text
            doc.page_count = stats["page_count"]
            doc.word_count = stats["word_count"]
            doc.character_count = stats["character_count"]
            
            # Index document for RAG
            from services.embedding_service import index_document
            index_success = index_document(str(doc.id), text, doc.user_id, doc.original_filename)
            if index_success:
                doc.status = 'completed'
            else:
                doc.status = 'indexed_failed'
        else:
            doc.status = 'failed'
            doc.extracted_text = "Text extraction failed or format unsupported."
            
        db.session.commit()
        return success
    except Exception as e:
        print(f"Document processing failed for {document_id}: {e}")
        doc.status = 'failed'
        db.session.commit()
        return False
