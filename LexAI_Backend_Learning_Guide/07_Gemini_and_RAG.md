# 07. Gemini and RAG

RAG (Retrieval-Augmented Generation) prevents hallucinations. When a user asks a question, ChromaDB finds the most relevant document chunks. These chunks are sent to the Gemini API with a strict prompt: *Answer only based on this text.*