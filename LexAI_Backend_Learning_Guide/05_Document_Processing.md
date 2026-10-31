# 05. Document Processing

When a user uploads a PDF, `PyMuPDF` extracts the raw text. If it's a Word file, `python-docx` is used. The text is chunked into overlapping segments (e.g., 500 words) to prevent losing context.