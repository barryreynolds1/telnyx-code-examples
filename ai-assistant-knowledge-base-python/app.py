#!/usr/bin/env python3
"""AI Assistant Knowledge Base — AI Assistant with document knowledge base for context-aware Q&A over uploaded documents."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "moonshotai/Kimi-K2.6")
API = "https://api.telnyx.com/v2"
INFERENCE_URL = f"{API}/ai/chat/completions"
EMBEDDING_URL = f"{API}/ai/embeddings"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
documents = []
chunks = []

def chunk_text(text, chunk_size=500, overlap=50):
    result = []
    for i in range(0, len(text), chunk_size - overlap):
        result.append(text[i:i + chunk_size])
    return result

def get_embedding(text):
    try:
        resp = requests.post(EMBEDDING_URL, headers=headers,
            json={"model": "telnyx/nomic-embed-text-v1.5", "input": text}, timeout=15)
        return resp.json().get("data", [{}])[0].get("embedding", [])
    except Exception:
        return []

def cosine_sim(a, b):
    if not a or not b:
        return 0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0

@app.route("/documents", methods=["POST"])
def add_document():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    title = data.get("title", f"doc-{int(time.time())}")
    content = data.get("content", "")
    if not content:
        return jsonify({"error": "content required"}), 400
    doc = {"id": len(documents), "title": title, "length": len(content),
        "chunks": 0, "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    text_chunks = chunk_text(content)
    for i, chunk in enumerate(text_chunks):
        embedding = get_embedding(chunk)
        chunks.append({"doc_id": doc["id"], "chunk_index": i, "text": chunk,
            "embedding": embedding})
    doc["chunks"] = len(text_chunks)
    documents.append(doc)
    return jsonify({"status": "indexed", "document": doc}), 200

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    question = data.get("question", "")
    top_k = data.get("top_k", 3)
    if not question:
        return jsonify({"error": "question required"}), 400
    q_embedding = get_embedding(question)
    scored = []
    for chunk in chunks:
        sim = cosine_sim(q_embedding, chunk.get("embedding", []))
        scored.append((sim, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    context_chunks = scored[:top_k]
    context = "\n\n".join(f"[Source: doc {c['doc_id']}, chunk {c['chunk_index']}]\n{c['text']}" for _, c in context_chunks)
    try:
        resp = requests.post(INFERENCE_URL, headers=headers,
            json={"model": AI_MODEL, "messages": [
                {"role": "system", "content": f"Answer based on this knowledge base context. If the answer is not in the context, say so.\n\nContext:\n{context}"},
                {"role": "user", "content": question}], "max_tokens": 400, "temperature": 0.3}, timeout=20)
        answer = resp.json()["choices"][0]["message"]["content"]
        sources = [{"doc_id": c["doc_id"], "chunk": c["chunk_index"], "score": round(s, 3)} for s, c in context_chunks]
        return jsonify({"answer": answer, "sources": sources}), 200
    except Exception:
        app.logger.exception("failed to generate answer")
        return jsonify({"error": "internal error"}), 500

@app.route("/documents", methods=["GET"])
def list_documents():
    return jsonify({"documents": documents, "total_chunks": len(chunks)}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "documents": len(documents), "chunks": len(chunks)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
