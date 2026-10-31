import os
import uuid
import shutil
from flask import current_app
from werkzeug.utils import secure_filename

def get_storage_provider():
    """Returns the active storage provider ('local' or 'cloudinary')."""
    try:
        provider = current_app.config.get('STORAGE_PROVIDER', 'local').lower()
    except RuntimeError:
        provider = os.getenv('STORAGE_PROVIDER', 'local').lower()
        
    # If cloudinary is requested, verify credentials exist; otherwise fallback to local
    if provider == 'cloudinary':
        has_url = bool(os.getenv('CLOUDINARY_URL') or current_app.config.get('CLOUDINARY_URL'))
        has_keys = bool(
            (os.getenv('CLOUDINARY_CLOUD_NAME') or current_app.config.get('CLOUDINARY_CLOUD_NAME')) and
            (os.getenv('CLOUDINARY_API_KEY') or current_app.config.get('CLOUDINARY_API_KEY')) and
            (os.getenv('CLOUDINARY_API_SECRET') or current_app.config.get('CLOUDINARY_API_SECRET'))
        )
        if not (has_url or has_keys):
            return 'local'
    return provider

def configure_cloudinary():
    """Configures the cloudinary library if credentials exist."""
    import cloudinary
    import cloudinary.uploader
    
    url = current_app.config.get('CLOUDINARY_URL') or os.getenv('CLOUDINARY_URL')
    if url:
        cloudinary.config(cloudinary_url=url)
    else:
        cloudinary.config(
            cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME') or os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=current_app.config.get('CLOUDINARY_API_KEY') or os.getenv('CLOUDINARY_API_KEY'),
            api_secret=current_app.config.get('CLOUDINARY_API_SECRET') or os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
    return cloudinary

def save_document_file(file, user_id, document_uuid=None):
    """
    Saves an uploaded document either locally or to Cloudinary.
    Returns a dict with:
        - file_path: storage URL or local filesystem path
        - storage_key: cloud public_id or local relative path
        - storage_provider: 'local' or 'cloudinary'
        - file_size: size in bytes
        - temp_local_path: path to a local copy for extraction (in /tmp or uploads)
    """
    if document_uuid is None:
        document_uuid = str(uuid.uuid4())
        
    safe_filename = secure_filename(file.filename)
    provider = get_storage_provider()
    
    # Read file content or get size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if provider == 'cloudinary':
        try:
            cloudinary = configure_cloudinary()
            import cloudinary.uploader
            
            # Cloudinary public ID under a dedicated folder per user
            cloud_public_id = f"lexai_uploads/user_{user_id}/{document_uuid}/{safe_filename}"
            
            upload_result = cloudinary.uploader.upload(
                file,
                resource_type="raw",
                public_id=cloud_public_id,
                unique_filename=False,
                overwrite=True
            )
            
            # Keep a temporary copy in /tmp for immediate text extraction
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "lexai_temp", str(user_id), document_uuid)
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, safe_filename)
            file.seek(0)
            file.save(temp_path)
            
            return {
                "file_path": upload_result.get("secure_url", upload_result.get("url", cloud_public_id)),
                "storage_key": cloud_public_id,
                "storage_provider": "cloudinary",
                "file_size": file_size,
                "temp_local_path": temp_path
            }
        except Exception as e:
            import logging
            logging.warning(f"Cloudinary upload failed, falling back to local storage: {e}")
            provider = 'local'
            file.seek(0)

    # Local storage fallback
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    target_dir = os.path.join(upload_folder, str(user_id), document_uuid)
    
    # Path traversal validation
    abs_upload = os.path.abspath(upload_folder)
    abs_target = os.path.abspath(target_dir)
    if not abs_target.startswith(abs_upload):
        raise ValueError("Path traversal attempt detected in upload target.")
        
    os.makedirs(target_dir, exist_ok=True)
    local_path = os.path.join(target_dir, safe_filename)
    file.seek(0)
    file.save(local_path)
    
    return {
        "file_path": local_path,
        "storage_key": os.path.relpath(local_path, upload_folder),
        "storage_provider": "local",
        "file_size": file_size,
        "temp_local_path": local_path
    }

def delete_document_file(file_path, storage_key=None, storage_provider='local'):
    """
    Deletes the document from Cloudinary or local disk.
    """
    try:
        if storage_provider == 'cloudinary' or (file_path and file_path.startswith(('http://', 'https://'))):
            try:
                cloudinary = configure_cloudinary()
                import cloudinary.uploader
                pub_id = storage_key or file_path
                cloudinary.uploader.destroy(pub_id, resource_type="raw")
            except Exception as e:
                import logging
                logging.warning(f"Failed to delete Cloudinary file {file_path}: {e}")
                
        # Also clean up local file if it exists
        if file_path and os.path.exists(file_path):
            file_dir = os.path.dirname(file_path)
            if os.path.exists(file_dir):
                shutil.rmtree(file_dir, ignore_errors=True)
        return True
    except Exception as e:
        import logging
        logging.error(f"Error during file deletion: {e}")
        return False
