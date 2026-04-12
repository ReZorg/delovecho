# RAG Knowledge Base Schema for DeltaChat

This document defines the SQLite schema used by `rag_integration.py` for the `deltecho` skill, inspired by the `cragbase` skill.

## Database File

- **`rag_kb.db`**: A single SQLite database file containing all knowledge sources and their embeddings.

## Tables

### 1. `knowledge_sources`

Stores the raw content and metadata for each piece of knowledge.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary Key, auto-incrementing. |
| `source_type` | TEXT | The type of knowledge source. Can be 'text', 'file', or 'url'. |
| `content` | TEXT | The raw content of the knowledge source. |
| `status` | TEXT | The processing status. Defaults to 'pending'. Can be 'pending', 'processing', 'trained', or 'error'. |

### 2. `knowledge_embeddings`

Stores the text chunks and their corresponding vector embeddings.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary Key, auto-incrementing. |
| `source_id` | INTEGER | Foreign Key referencing `knowledge_sources.id`. |
| `chunk_text` | TEXT | A small segment of text from the original content. |
| `embedding` | BLOB | The vector embedding of `chunk_text`, stored as bytes. |

## Workflow

1.  **Add Knowledge**: A new row is added to the `knowledge_sources` table with the `status` as 'pending'.
2.  **Process Source**: The content is read from `knowledge_sources`, chunked, and embedded.
3.  **Store Embeddings**: Each chunk and its embedding are stored as a new row in the `knowledge_embeddings` table.
4.  **Update Status**: The `status` of the source in `knowledge_sources` is updated to 'trained' or 'error'.
5.  **Query**: When a user sends a message, it is embedded and compared against all embeddings in `knowledge_embeddings` to find relevant chunks.
