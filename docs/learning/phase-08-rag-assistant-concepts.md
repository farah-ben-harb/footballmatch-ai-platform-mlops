# Concepts — Phase 08 (Planned)

## RAG, embeddings, and LLMs

### Definition

An LLM generates text. An embedding converts text into a numeric vector. Retrieval
Augmented Generation retrieves relevant vectors/documents before asking an LLM to answer.

### Why it exists

RAG grounds responses in a changing, inspectable knowledge base without retraining the LLM.

### Architecture position

The optional assistant consumes stored analysis reports after the core platform creates them.

### Alternatives

Fine-tuning changes model weights and needs data/training; RAG changes context at query
time. A chatbot may answer without retrieval; a RAG system must cite retrieved context.

### Interview questions

Embedding versus LLM? RAG versus fine-tuning? PostgreSQL versus pgvector?

### Interview answers

Embeddings represent semantic similarity; LLMs generate text. RAG retrieves context at
inference time, while fine-tuning changes weights. pgvector adds vector indexing and
similarity search to PostgreSQL.
