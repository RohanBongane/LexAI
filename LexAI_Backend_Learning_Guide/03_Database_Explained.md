# 03. Database Explained

The MySQL database uses Flask-SQLAlchemy. Core tables include:
1. `users`: Credentials and roles.
2. `documents`: Metadata for uploaded PDFs/DOCXs.
3. `document_analysis`: JSON storage for extracted clauses.
4. `conversations` & `messages`: Chat histories.