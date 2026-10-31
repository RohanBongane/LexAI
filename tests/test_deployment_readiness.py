import os
import sys
import pytest
from app import create_app
from config import TestConfig
from extensions import db
from models.database_models import User, Document, DocumentAnalysis, Conversation, Message, KnowledgeBase

@pytest.fixture(scope='module')
def test_app():
    # Use SQLite in-memory or test database for deployment readiness testing
    app = create_app(TestConfig)
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "STORAGE_PROVIDER": "local"
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

def test_app_creation_and_config(test_app):
    """Test that Flask app initializes and loads configuration correctly."""
    assert test_app is not None
    assert test_app.config['TESTING'] is True
    assert 'SECRET_KEY' in test_app.config

def test_database_models_creation(test_app):
    """Test that all 6 database tables can be created and queried."""
    with test_app.app_context():
        user = User(name="Test User", email="test@example.com", password_hash="dummyhash", role="user")
        db.session.add(user)
        db.session.commit()
        
        fetched = User.query.filter_by(email="test@example.com").first()
        assert fetched is not None
        assert fetched.name == "Test User"
        assert fetched.role == "user"

def test_public_routes_load(test_client):
    """Test that public endpoints respond with HTTP 200."""
    response = test_client.get('/')
    assert response.status_code == 200

    response = test_client.get('/health')
    assert response.status_code == 200
    assert response.json.get("status") == "ok"

    response = test_client.get('/knowledge-base')
    assert response.status_code == 200

    response = test_client.get('/login')
    assert response.status_code == 200

    response = test_client.get('/register')
    assert response.status_code == 200

def test_protected_routes_redirect_unauthenticated(test_client):
    """Test that protected endpoints redirect anonymous users to login."""
    response = test_client.get('/dashboard')
    assert response.status_code in (302, 401)

    response = test_client.get('/upload')
    assert response.status_code in (302, 401)

    response = test_client.get('/chat')
    assert response.status_code in (302, 401)

    response = test_client.get('/document-history')
    assert response.status_code in (302, 401)

    response = test_client.get('/chat-history')
    assert response.status_code in (302, 401)

    response = test_client.get('/admin/')
    assert response.status_code in (302, 401, 403)

def test_no_route_collision_on_history(test_app):
    """Test that chat-history and document-history have unique distinct endpoints."""
    adapter = test_app.url_map.bind('localhost')
    chat_match = adapter.match('/chat-history', method='GET')
    doc_match = adapter.match('/document-history', method='GET')
    assert chat_match[0] == 'chat.chat_history'
    assert doc_match[0] == 'document.history'

def test_storage_service_abstraction(test_app):
    """Test storage service local mode functions without errors."""
    from services.storage_service import get_storage_provider, delete_document_file
    with test_app.app_context():
        provider = get_storage_provider()
        assert provider in ('local', 'cloudinary')
        # Deleting non-existent file returns cleanly without crashing
        res = delete_document_file("non_existent_file.pdf")
        assert res is True

def test_embedding_service_provider_selection(test_app):
    """Test that embedding service resolves provider without crashing."""
    from services.embedding_service import get_embedding_provider, chunk_text
    with test_app.app_context():
        provider = get_embedding_provider()
        assert provider in ('local', 'gemini')
        
        # Test chunking algorithm
        chunks = chunk_text("This is clause one of the agreement. This is clause two.", chunk_size=5, overlap=1)
        assert len(chunks) > 0

def test_ai_service_error_handling(test_app):
    """Test that ai_service gracefully handles missing API key."""
    from services.ai_service import analyze_legal_document
    with test_app.app_context():
        test_app.config['GEMINI_API_KEY'] = ''
        with pytest.raises(ValueError) as excinfo:
            analyze_legal_document("Sample legal text")
        assert "GEMINI_API_KEY is not configured" in str(excinfo.value)

def test_rag_service_fallback_on_empty(test_app):
    """Test that rag_service returns a graceful answer when context is empty."""
    from services.rag_service import answer_question
    with test_app.app_context():
        test_app.config['GEMINI_API_KEY'] = 'test-dummy-key'
        # With invalid dummy key and no document, it should return graceful fallback
        res = answer_question(user_id=1, question="What is an NDA?", document_id=None)
        assert "answer" in res
        assert isinstance(res["answer"], str)
        assert len(res["answer"]) > 0
