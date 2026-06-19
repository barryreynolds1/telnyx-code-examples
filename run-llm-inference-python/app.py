#!/usr/bin/env python3
"""Run LLM inference on Telnyx — OpenAI-compatible chat completions API."""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "meta-llama/Llama-3.3-70B-Instruct")
INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions"


def chat_completion(messages, model=None, max_tokens=500, temperature=0.7):
    """Send a chat completion request to Telnyx Inference API.

    The API is OpenAI-compatible — same request/response format, different endpoint.
    """
    response = requests.post(
        INFERENCE_URL,
        headers={
            "Authorization": f"Bearer {TELNYX_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model or AI_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def simple_ask(question, system_prompt=None):
    """Ask a single question and get a text response."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})

    result = chat_completion(messages)
    return result["choices"][0]["message"]["content"]


@app.route("/inference/chat", methods=["POST"])
def chat_endpoint():
    """HTTP endpoint for chat completions — pass through to Telnyx Inference."""
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Request body must include 'messages' array"}), 400

    try:
        result = chat_completion(
            messages=data["messages"],
            model=data.get("model"),
            max_tokens=data.get("max_tokens", 500),
            temperature=data.get("temperature", 0.7),
        )
        return jsonify(result), 200
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 500
        return jsonify({"error": f"Inference API error: {status}"}), status
    except requests.ConnectionError:
        return jsonify({"error": "Cannot connect to Telnyx Inference API"}), 503
    except requests.Timeout:
        return jsonify({"error": "Inference request timed out"}), 504


@app.route("/inference/ask", methods=["POST"])
def ask_endpoint():
    """Simplified endpoint — send a question, get an answer."""
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Request body must include 'question'"}), 400

    try:
        answer = simple_ask(
            question=data["question"],
            system_prompt=data.get("system_prompt"),
        )
        return jsonify({"answer": answer}), 200
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else 500
        return jsonify({"error": f"Inference API error: {status}"}), status


@app.route("/health", methods=["GET"])
def health():
    """Health check."""
    return jsonify({"status": "ok", "model": AI_MODEL}), 200


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--serve":
        # CLI mode: python app.py "What is SIP trunking?"
        question = " ".join(sys.argv[1:])
        print(f"Model: {AI_MODEL}")
        print(f"Question: {question}\n")
        answer = simple_ask(question)
        print(f"Answer: {answer}")
    else:
        app.run(
            debug=False,
            host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", 5000)),
        )
