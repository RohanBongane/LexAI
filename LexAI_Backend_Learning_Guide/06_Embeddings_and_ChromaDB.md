# 06. Embeddings and ChromaDB

Each chunk is converted into a mathematical vector using `SentenceTransformers (all-MiniLM-L6-v2)`. These vectors are saved in `ChromaDB`, tagged with `user_id` and `document_id` to guarantee data isolation.