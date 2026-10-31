import os

def create_guides():
    folder = "LexAI_Backend_Learning_Guide"
    os.makedirs(folder, exist_ok=True)
    
    files = {
        "00_Project_Overview.md": "# 00. Project Overview\n\nThis guide covers the LexAI backend architecture, explaining how Flask, MySQL, ChromaDB, and Gemini work together to power the AI Legal Assistant.",
        "01_Project_Structure.md": "# 01. Project Structure\n\n- `app.py`: The entry point.\n- `extensions.py`: Database and auth extensions.\n- `config.py`: Environment variables.\n- `models/`: Database schemas (User, Document, etc.).\n- `routes/`: Blueprint controllers.\n- `services/`: Core logic (AI, vector database).",
        "02_Flask_and_Routes.md": "# 02. Flask and Routes\n\nRoutes intercept browser requests. `auth_routes.py` handles login/registration. `document_routes.py` manages file uploads. `chat_routes.py` processes RAG-based conversations.",
        "03_Database_Explained.md": "# 03. Database Explained\n\nThe MySQL database uses Flask-SQLAlchemy. Core tables include:\n1. `users`: Credentials and roles.\n2. `documents`: Metadata for uploaded PDFs/DOCXs.\n3. `document_analysis`: JSON storage for extracted clauses.\n4. `conversations` & `messages`: Chat histories.",
        "04_Authentication.md": "# 04. Authentication\n\nHandled by `Flask-Login` and `Flask-Bcrypt`. Passwords are mathematically hashed so they are never stored in plain text. Routes are protected using `@login_required`.",
        "05_Document_Processing.md": "# 05. Document Processing\n\nWhen a user uploads a PDF, `PyMuPDF` extracts the raw text. If it's a Word file, `python-docx` is used. The text is chunked into overlapping segments (e.g., 500 words) to prevent losing context.",
        "06_Embeddings_and_ChromaDB.md": "# 06. Embeddings and ChromaDB\n\nEach chunk is converted into a mathematical vector using `SentenceTransformers (all-MiniLM-L6-v2)`. These vectors are saved in `ChromaDB`, tagged with `user_id` and `document_id` to guarantee data isolation.",
        "07_Gemini_and_RAG.md": "# 07. Gemini and RAG\n\nRAG (Retrieval-Augmented Generation) prevents hallucinations. When a user asks a question, ChromaDB finds the most relevant document chunks. These chunks are sent to the Gemini API with a strict prompt: *Answer only based on this text.*",
        "08_Error_Handling_and_Testing.md": "# 08. Error Handling and Testing\n\nThe backend features a fallback parser. If Gemini API fails, the system bypasses the LLM and presents the raw relevant chunks retrieved from ChromaDB. `pytest` is used to verify database isolation.",
        "09_Run_and_Troubleshoot.md": "# 09. Run and Troubleshoot\n\n- `venv\\Scripts\\activate`\n- `pip install -r requirements.txt`\n- `python app.py`\n\nTroubleshooting: Ensure MySQL service is running and `FLASK_APP` is set.",
        "10_MCA_Viva_Questions.md": "# 10. MCA Viva Questions\n\nContains 40 highly targeted questions about the Flask architecture, database isolation, RAG, semantic search, and fallback mechanisms."
    }
    
    for filename, content in files.items():
        with open(os.path.join(folder, filename), "w") as f:
            f.write(content)

if __name__ == "__main__":
    create_guides()
