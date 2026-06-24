#!/usr/bin/env node
/**
 * Production-ready Express webhook for receiving inbound MMS via Telnyx.
 * Parses MMS payloads, extracts media URLs, and stores message data.
 */

const express = require("express");
const bodyParser = require("body-parser");
const Telnyx = require("telnyx");
require("dotenv").config();

const app = express();
app.use(bodyParser.json());

// Initialize client with the new SDK pattern
const client = new Telnyx({ apiKey: process.env.TELNYX_API_KEY });

/**
 * Parse inbound MMS message and extract media URLs.
 * Returns JSON-serializable message data.
 */
function parseInboundMMS(payload) {
  const event = payload.data;
  
  if (!event || !event.payload) {
    throw new Error("Invalid webhook payload structure");
  }

  const message = event.payload;
  
  // Extract media URLs from the message
  const mediaUrls = [];
  if (message.media && Array.isArray(message.media)) {
    message.media.forEach((mediaItem) => {
      if (mediaItem.url) {
        mediaUrls.push({
          url: mediaItem.url,
          type: mediaItem.type || "unknown",
          size: mediaItem.size || null,
        });
      }
    });
  }

  // Return serializable message data
  return {
    messageId: message.id,
    from: message.from?.phone_number || "unknown",
    to: message.to?.[0]?.phone_number || "unknown",
    text: message.text || "",
    mediaCount: mediaUrls.length,
    media: mediaUrls,
    receivedAt: message.received_at || new Date().toISOString(),
    direction: message.direction || "inbound",
  };
}

/**
 * Store message data (in-memory for demo; use database in production).
 */
const messageStore = [];

function storeMessage(messageData) {
  messageStore.push({
    ...messageData,
    storedAt: new Date().toISOString(),
  });
  // Keep only last 100 messages in memory
  if (messageStore.length > 100) {
    messageStore.shift();
  }
}

/**
 * Webhook endpoint to receive inbound MMS messages.
 * Telnyx sends POST requests to this URL when MMS is received.
 */
app.post("/webhooks/mms", (req, res) => {
  try {
    // Validate webhook payload structure
    if (!req.body || !req.body.data) {
      return res.status(400).json({ error: "Invalid webhook payload" });
    }

    // Parse the inbound MMS message
    const messageData = parseInboundMMS(req.body);

    // Store the message for later retrieval
    storeMessage(messageData);

    console.log(`[MMS Received] From: ${messageData.from}, Media: ${messageData.mediaCount}`);

    // Acknowledge receipt immediately (Telnyx expects 200 within 5 seconds)
    res.status(200).json({
      success: true,
      messageId: messageData.messageId,
      mediaProcessed: messageData.mediaCount,
    });
  } catch (error) {
    console.error("Webhook processing error:", error.message);
    // Return 200 to prevent Telnyx from retrying, but log the error
    res.status(200).json({ error: error.message });
  }
});

/**
 * Endpoint to retrieve stored messages (for testing/debugging).
 */
app.get("/messages", (req, res) => {
  try {
    res.json({
      count: messageStore.length,
      messages: messageStore,
    });
  } catch (error) {
    console.error("Error retrieving messages:", error.message);
    res.status(500).json({ error: "Failed to retrieve messages" });
  }
});

/**
 * Health check endpoint.
 */
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Global error handler for uncaught exceptions
app.use((err, req, res, next) => {
  console.error("Unhandled error:", err);
  res.status(500).json({ error: "Internal server error" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MMS receiver listening on port ${PORT}`);
  console.log(`Webhook URL: ${process.env.WEBHOOK_URL}`);
});
