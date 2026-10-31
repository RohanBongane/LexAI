import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class Config:
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')

    if DATABASE_URL:
        # Standardize MySQL scheme for PyMySQL
        if DATABASE_URL.startswith('mysql://'):
            DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
        elif DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        # On Vercel, if no remote DATABASE_URL is configured, fallback to ephemeral SQLite in /tmp
        # so the application boots and runs gracefully without crashing on unreachable localhost:3306
        import tempfile
        db_path = os.path.join(tempfile.gettempdir(), 'lexai_ephemeral.db').replace('\\', '/')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    else:
        DB_USER     = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_HOST     = os.getenv('DB_HOST', 'localhost')
        DB_PORT     = os.getenv('DB_PORT', '3306')
        DB_NAME     = os.getenv('DB_NAME', 'lexai_db')

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Serverless-Optimized Connection Pool
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        # Ensures connections don't drop or stale in stateless serverless environments
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 280,
            "pool_timeout": 20,
        }

        # SSL Support for Hosted MySQL (e.g. TiDB Cloud, Aiven, PlanetScale)
        DB_SSL_CA = os.getenv('DB_SSL_CA')
        if DB_SSL_CA:
            SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {"ssl": {"ca": DB_SSL_CA}}
        elif os.getenv('DB_SSL', 'false').lower() in ('1', 'true', 'yes'):
            # Enable default SSL context for providers with valid public certificates
            import ssl
            ctx = ssl.create_default_context()
            SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {"ssl": ctx}

    # Production Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Secure cookies in production or when not in explicit local debug
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() in ('1', 'true', 'yes')

    # AI Configuration
    AI_PROVIDER    = os.getenv('AI_PROVIDER', 'gemini')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    AI_MODEL       = os.getenv('AI_MODEL', 'gemini-3.6-flash')

    # Storage Configuration (Local vs Cloud Object Storage)
    STORAGE_PROVIDER       = os.getenv('STORAGE_PROVIDER', 'local')  # 'local' or 'cloudinary'
    UPLOAD_FOLDER          = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
    MAX_CONTENT_LENGTH     = 15 * 1024 * 1024  # 15 MB
    
    # Cloudinary Settings
    CLOUDINARY_CLOUD_NAME  = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY     = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET  = os.getenv('CLOUDINARY_API_SECRET', '')
    CLOUDINARY_URL         = os.getenv('CLOUDINARY_URL', '')

    # Vector & RAG Configuration
    # 'auto': uses Gemini API embeddings if PyTorch is absent (Vercel serverless mode), else local
    EMBEDDING_PROVIDER     = os.getenv('EMBEDDING_PROVIDER', 'auto') # 'auto', 'gemini', 'local'
    CHROMA_DB_PATH         = os.getenv('CHROMA_DB_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma_db'))


class TestConfig(Config):
    TESTING                = True
    DEBUG                  = True
    DB_NAME                = 'lexai_test'
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{Config.DB_USER if hasattr(Config, 'DB_USER') else 'root'}:{urllib.parse.quote_plus(os.getenv('DB_PASSWORD', ''))}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/lexai_test"
    )
    WTF_CSRF_ENABLED       = False
    CHROMA_DB_PATH         = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma_db_test')
    STORAGE_PROVIDER       = 'local'
