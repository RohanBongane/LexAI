import os
import logging
from flask import current_app

# Lazy-loaded globals
_local_model = None
_chroma_client = None
_current_chroma_target = None

def get_embedding_provider():
    try:
        provider = current_app.config.get('EMBEDDING_PROVIDER', 'auto').lower()
    except RuntimeError:
        provider = os.getenv('EMBEDDING_PROVIDER', 'auto').lower()
        
    if provider == 'auto':
        # In serverless environments (or without torch), prefer gemini API embeddings
        try:
            import torch
            import sentence_transformers
            return 'local'
        except ImportError:
            return 'gemini'
    return provider

def get_local_embedding_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _local_model

def generate_embeddings_gemini(texts, api_key=None):
    """Generates embeddings using Google Gemini text-embedding-004 (no local PyTorch required)."""
    from google import genai
    
    if not api_key:
        try:
            api_key = current_app.config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        except RuntimeError:
            api_key = os.getenv('GEMINI_API_KEY')
            
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required for Gemini API embeddings.")
        
    client = genai.Client(api_key=api_key)
    
    # Process texts in small batches to respect API limits
    all_embeddings = []
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            res = client.models.embed_content(
                model="text-embedding-004",
                contents=batch
            )
            for emb in res.embeddings:
                all_embeddings.append(emb.values)
        except Exception as e:
            logging.error(f"Gemini embedding batch failed: {e}")
            raise
    return all_embeddings

def generate_embeddings(texts):
    """Unified embedding generator supporting local sentence-transformers and Google Gemini API."""
    if not texts:
        return []
        
    if isinstance(texts, str):
        texts = [texts]
        
    provider = get_embedding_provider()
    
    if provider == 'local':
        try:
            model = get_local_embedding_model()
            return model.encode(texts, convert_to_numpy=True).tolist()
        except Exception as e:
            logging.warning(f"Local embedding generation failed ({e}), falling back to Gemini API.")
            return generate_embeddings_gemini(texts)
    else:
        try:
            return generate_embeddings_gemini(texts)
        except Exception as e:
            # If Gemini API fails, attempt local fallback if torch is installed
            try:
                model = get_local_embedding_model()
                return model.encode(texts, convert_to_numpy=True).tolist()
            except Exception:
                raise RuntimeError(f"Embedding generation failed: {e}")

def get_chroma_client():
    global _chroma_client, _current_chroma_target
    import chromadb
    
    # Check for Hosted ChromaDB service
    chroma_host = os.getenv('CHROMA_HOST')
    chroma_port = os.getenv('CHROMA_PORT', '8000')
    
    target_key = f"remote:{chroma_host}:{chroma_port}" if chroma_host else "local"
    
    if _chroma_client is not None and _current_chroma_target == target_key:
        return _chroma_client
        
    if chroma_host:
        try:
            ssl_enabled = os.getenv('CHROMA_SSL', 'false').lower() in ('1', 'true', 'yes')
            _chroma_client = chromadb.HttpClient(
                host=chroma_host,
                port=int(chroma_port),
                ssl=ssl_enabled
            )
            _current_chroma_target = target_key
            return _chroma_client
        except Exception as e:
            logging.warning(f"Failed to connect to hosted ChromaDB at {chroma_host}: {e}. Falling back to local/ephemeral client.")

    # Local ChromaDB
    try:
        db_path = current_app.config.get('CHROMA_DB_PATH')
    except RuntimeError:
        db_path = os.getenv('CHROMA_DB_PATH', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chroma_db'))
        
    try:
        os.makedirs(db_path, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=db_path)
    except Exception as e:
        # In serverless environments where local filesystem might be read-only, fallback to EphemeralClient
        logging.warning(f"ChromaDB PersistentClient initialization failed ({e}), falling back to EphemeralClient.")
        _chroma_client = chromadb.EphemeralClient()
        
    _current_chroma_target = target_key
    return _chroma_client

def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name="lexai_documents")

def chunk_text(text, chunk_size=1000, overlap=150):
    """Splits text into meaningful chunks using a word-based sliding window."""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        end = min(i + chunk_size, len(words))
        chunk_words = words[i:end]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size
            
        i += step
        
    return chunks

def index_document(document_id, text, user_id, filename):
    """Chunks document text, generates embeddings, and stores them in ChromaDB."""
    if not text:
        return False
        
    try:
        chunks = chunk_text(text)
        if not chunks:
            return True
            
        embeddings = generate_embeddings(chunks)
        collection = get_collection()
        
        ids = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "user_id": int(user_id),
                "document_id": str(document_id),
                "filename": filename,
                "chunk_index": i
            })
            
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return True
    except Exception as e:
        logging.error(f"Failed to index document {document_id}: {e}")
        return False

def delete_document_vectors(document_id, user_id):
    """Deletes all vectors for a given document from ChromaDB with user isolation check."""
    try:
        collection = get_collection()
        collection.delete(
            where={
                "$and": [
                    {"document_id": {"$eq": str(document_id)}},
                    {"user_id": {"$eq": int(user_id)}}
                ]
            }
        )
        return True
    except Exception as e:
        logging.error(f"Failed to delete vectors for document {document_id}: {e}")
        return False

def embed_question(question):
    """Converts a user question into an embedding."""
    embs = generate_embeddings([question])
    return embs[0] if embs else []

def index_kb_entry(kb_id, title, category, content, source):
    """Chunks a Knowledge Base entry, embeds it, and stores in ChromaDB."""
    if not content:
        return False
    try:
        chunks = chunk_text(content)
        if not chunks:
            return True
            
        embeddings = generate_embeddings(chunks)
        collection = get_collection()
        
        ids = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"kb_{kb_id}_chunk_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "source_type": "knowledge_base",
                "knowledge_base_id": str(kb_id),
                "category": category,
                "title": title,
                "source": source or "LexAI KB",
                "chunk_index": i
            })
            
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return True
    except Exception as e:
        logging.error(f"Failed to index KB entry {kb_id}: {e}")
        return False

def delete_kb_vectors(kb_id):
    """Deletes all vectors for a given KB entry from ChromaDB."""
    try:
        collection = get_collection()
        collection.delete(
            where={"knowledge_base_id": {"$eq": str(kb_id)}}
        )
        return True
    except Exception as e:
        logging.error(f"Failed to delete vectors for KB entry {kb_id}: {e}")
        return False
