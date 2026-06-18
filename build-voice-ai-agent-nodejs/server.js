#!/usr/bin/env node
"use strict";

/**
 * Build a complete voice AI agent with Telnyx — inbound call handling,
 * AI conversation via Telnyx Inference, and call control.
 */

require("dotenv").config();
const express = require("express");
const Telnyx = require("telnyx");

const app = express();
app.use(express.json());

const telnyx = new Telnyx(process.env.TELNYX_API_KEY);

const AI_MODEL = process.env.AI_MODEL || "meta-llama/Llama-3.3-70B-Instruct";
const SYSTEM_PROMPT =
  process.env.SYSTEM_PROMPT ||
  "You are a helpful voice AI agent for a business. " +
    "Keep responses concise — under 2 sentences — since this is a phone call. " +
    "Be natural and conversational.";
const TRANSFER_NUMBER = process.env.TRANSFER_NUMBER || "";
const PORT = parseInt(process.env.PORT || "5000", 10);

// In-memory conversation store (use Redis in production)
const conversations = new Map();

/**
 * Call Telnyx Inference API (OpenAI-compatible).
 */
async function callTelnyxInference(messages) {
  const response = await fetch("https://api.telnyx.com/v2/ai/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.TELNYX_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: AI_MODEL,
      messages,
      max_tokens: 150,
      temperature: 0.7,
    }),
  });

  if (!response.ok) {
    throw new Error(`Inference API error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

/**
 * Get AI response with conversation history.
 */
async function getAiResponse(callControlId, userInput) {
  if (!conversations.has(callControlId)) {
    conversations.set(callControlId, [{ role: "system", content: SYSTEM_PROMPT }]);
  }

  const history = conversations.get(callControlId);
  history.push({ role: "user", content: userInput });

  const aiResponse = await callTelnyxInference(history);
  history.push({ role: "assistant", content: aiResponse });

  // Keep history manageable
  if (history.length > 21) {
    conversations.set(callControlId, [history[0], ...history.slice(-20)]);
  }

  return aiResponse;
}

/**
 * Handle all voice webhook events.
 */
app.post("/webhooks/voice", async (req, res) => {
  try {
    const { data } = req.body;
    if (!data) return res.status(400).json({ error: "No payload" });

    const { event_type: eventType, call_control_id: callControlId } = data;

    switch (eventType) {
      case "call.initiated":
        if (data.direction === "incoming") {
          await telnyx.calls.actions.answer(callControlId);
        }
        return res.json({ status: "answering" });

      case "call.answered":
        await telnyx.calls.actions.speak(callControlId, {
          payload: "Hi, thanks for calling. How can I help you today?",
          voice: "female",
          language_code: "en-US",
        });
        return res.json({ status: "greeting" });

      case "call.speak.ended":
        await telnyx.calls.actions.gather(callControlId, {
          input_type: "speech",
          end_silence_timeout_secs: 2,
          timeout_secs: 15,
          language_code: "en-US",
        });
        return res.json({ status: "listening" });

      case "call.gather.ended": {
        const speech = data.speech?.result || "";

        if (!speech) {
          await telnyx.calls.actions.speak(callControlId, {
            payload: "I didn't catch that. Could you repeat?",
            voice: "female",
            language_code: "en-US",
          });
          return res.json({ status: "reprompting" });
        }

        const aiResponse = await getAiResponse(callControlId, speech);

        await telnyx.calls.actions.speak(callControlId, {
          payload: aiResponse,
          voice: "female",
          language_code: "en-US",
        });
        return res.json({ status: "responding", response: aiResponse });
      }

      case "call.hangup":
        conversations.delete(callControlId);
        return res.json({ status: "call_ended" });

      default:
        return res.json({ status: "event_received", event_type: eventType });
    }
  } catch (err) {
    console.error("Webhook error:", err.message);
    return res.status(500).json({ error: "Internal error" });
  }
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", active_calls: conversations.size });
});

app.listen(PORT, () => {
  console.log(`Voice AI agent listening on port ${PORT}`);
});
