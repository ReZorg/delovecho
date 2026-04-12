#!/usr/bin/env python3

import logging
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np

# Inspired by cragbase skill

class RAGIntegration:
    def __init__(self, db_path='rag_kb.db'):
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL, -- 'text', 'file', 'url'
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending' -- 'pending', 'processing', 'trained', 'error'
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                chunk_text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                FOREIGN KEY(source_id) REFERENCES knowledge_sources(id)
            )
            ''')
            conn.commit()

    def add_knowledge_source(self, source_type, content):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO knowledge_sources (source_type, content) VALUES (?, ?)", (source_type, content))
            conn.commit()
            return cursor.lastrowid

    def process_source(self, source_id, chunk_size=1000, chunk_overlap=200):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM knowledge_sources WHERE id = ?", (source_id,))
            result = cursor.fetchone()
            if not result:
                logging.error(f"Source ID {source_id} not found.")
                return

            content = result[0]
            cursor.execute("UPDATE knowledge_sources SET status = 'processing' WHERE id = ?", (source_id,))
            conn.commit()

            try:
                chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                embeddings = self.model.encode(chunks)

                for chunk, embedding in zip(chunks, embeddings):
                    cursor.execute("INSERT INTO knowledge_embeddings (source_id, chunk_text, embedding) VALUES (?, ?, ?)",
                                   (source_id, chunk, embedding.tobytes()))

                cursor.execute("UPDATE knowledge_sources SET status = 'trained' WHERE id = ?", (source_id,))
                conn.commit()
                logging.info(f"Successfully processed and embedded source ID {source_id}")
            except Exception as e:
                cursor.execute("UPDATE knowledge_sources SET status = 'error' WHERE id = ?", (source_id,))
                conn.commit()
                logging.error(f"Error processing source ID {source_id}: {e}")

    def _chunk_text(self, text, chunk_size, chunk_overlap):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - chunk_overlap
        return chunks

    def find_relevant_chunks(self, query, top_k=3, min_similarity=0.5):
        query_embedding = self.model.encode([query])[0]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chunk_text, embedding FROM knowledge_embeddings")
            results = cursor.fetchall()

        if not results:
            return []

        chunks, embeddings = zip(*results)
        embeddings = [np.frombuffer(e, dtype=np.float32) for e in embeddings]
        
        similarities = self._cosine_similarity(query_embedding, np.array(embeddings))
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_chunks = []
        for i in top_indices:
            if similarities[i] >= min_similarity:
                relevant_chunks.append({
                    "text": chunks[i],
                    "similarity": similarities[i]
                })
        return relevant_chunks

    def _cosine_similarity(self, vec_a, matrix_b):
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(matrix_b, axis=1)
        return np.dot(matrix_b, vec_a) / (norm_a * norm_b)

    def build_rag_context(self, query, **kwargs):
        chunks = self.find_relevant_chunks(query, **kwargs)
        return "\n\n".join([chunk['text'] for chunk in chunks])
