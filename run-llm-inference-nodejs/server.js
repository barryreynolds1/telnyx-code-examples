#!/usr/bin/env node
"use strict";

/**
 * Run LLM inference on Telnyx — OpenAI-compatible chat completions API.
 */

require("dotenv").config();
const express = require("express");

const app = express();
app.use(express.json());

const TELNYX_API_KEY = process.env.TELNYX_API_KEY;
const AI_MODEL = process.env.AI_MODEL || "meta-llama/Llama-3.3-70B-Instruct";
const INFERENCE_URL = "https://api.telnyx.com/v2/ai/chat/completions";
const PORT = parseInt(process.env.PORT || "5000", 10);

/**
 * Send a chat completion request to Telnyx Inference API.
 */
async function chatCompletion(messages, options = {}) {
  const response = await fetch(INFERENCE_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${TELNYX_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: options.model || AI_MODEL,
      messages,
      max_tokens: options.maxTokens || 500,
      temperature: options.temperature || 0.7,
    }),
  });

  if (!response.ok) {
    throw new Error(`Inference API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Ask a single question and get a text response.
 */
async function simpleAsk(question, systemPrompt) {
  const messages = [];
  if (systemPrompt) {
    messages.push({ role: "system", content: systemPrompt });
  }
  messages.push({ role: "user", content: question });

  const result = await chatCompletion(messages);
  return result.choices[0].message.content;
}

// Chat completions endpoint
app.post("/inference/chat", async (req, res) => {
  const { messages, model, max_tokens, temperature } = req.body;
  if (!messages) {
    return res.status(400).json({ error: "Request body must include 'messages' array" });
  }

  try {
    const result = await chatCompletion(messages, {
      model,
      maxTokens: max_tokens,
      temperature,
    });
    return res.json(result);
  } catch (err) {
    console.error("Inference error:", err.message);
    return res.status(500).json({ error: err.message });
  }
});

// Simple ask endpoint
app.post("/inference/ask", async (req, res) => {
  const { question, system_prompt } = req.body;
  if (!question) {
    return res.status(400).json({ error: "Request body must include 'question'" });
  }

  try {
    const answer = await simpleAsk(question, system_prompt);
    return res.json({ answer });
  } catch (err) {
    console.error("Inference error:", err.message);
    return res.status(500).json({ error: err.message });
  }
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", model: AI_MODEL });
});

// CLI mode or server mode
if (process.argv.length > 2 && process.argv[2] !== "--serve") {
  const question = process.argv.slice(2).join(" ");
  console.log(`Model: ${AI_MODEL}`);
  console.log(`Question: ${question}\n`);
  simpleAsk(question)
    .then((answer) => console.log(`Answer: ${answer}`))
    .catch((err) => {
      console.error("Error:", err.message);
      process.exit(1);
    });
} else {
  app.listen(PORT, () => {
    console.log(`Inference server listening on port ${PORT}`);
  });
}
