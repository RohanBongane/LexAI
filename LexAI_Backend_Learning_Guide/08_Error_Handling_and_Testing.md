# 08. Error Handling and Testing

The backend features a fallback parser. If Gemini API fails, the system bypasses the LLM and presents the raw relevant chunks retrieved from ChromaDB. `pytest` is used to verify database isolation.