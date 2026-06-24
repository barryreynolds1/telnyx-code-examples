#!/usr/bin/env node
/**
 * Production-ready Express endpoint for cloning AI Assistants via Telnyx.
 * Demonstrates proper error handling, validation, and SDK usage patterns.
 */

const telnyx = require("telnyx");
const express = require("express");
require("dotenv").config();

// Initialize client with the SDK pattern
const client = new telnyx.Telnyx({
  apiKey: process.env.TELNYX_API_KEY,
});

const app = express();
app.use(express.json());

/**
 * Clone an AI Assistant and return JSON-serializable response data.
 * @param {string} assistantId - The ID of the assistant to clone.
 * @param {string} newName - The name for the cloned assistant.
 * @returns {Promise<Object>} Cloned assistant data.
 */
async function cloneAssistant(assistantId, newName) {
  if (!assistantId) {
    throw new Error("Assistant ID is required");
  }

  if (!newName || newName.trim().length === 0) {
    throw new Error("New assistant name is required and cannot be empty");
  }

  // Use client.aiAssistants.clone() to duplicate the assistant
  const response = await client.aiAssistants.clone(assistantId, {
    name: newName,
  });

  // Extract serializable data — SDK objects are NOT JSON-serializable
  return {
    id: response.data.id,
    name: response.data.name,
    model: response.data.model,
    instructions: response.data.instructions,
    tools: response.data.tools || [],
    enabled_features: response.data.enabled_features || [],
    created_at: response.data.created_at,
  };
}

/**
 * POST /assistants/clone
 * Clone an existing AI Assistant with a new name.
 */
app.post("/assistants/clone", async (req, res) => {
  const { assistant_id, name } = req.body;

  // Validate required fields
  if (!assistant_id || !name) {
    return res.status(400).json({
      error: "Missing required fields: 'assistant_id' and 'name'",
    });
  }

  try {
    const clonedAssistant = await cloneAssistant(assistant_id, name);
    return res.status(201).json(clonedAssistant);
  } catch (error) {
    // Handle Telnyx-specific errors
    if (error instanceof telnyx.AuthenticationError) {
      return res.status(401).json({ error: "Invalid API key" });
    }

    if (error instanceof telnyx.RateLimitError) {
      return res.status(429).json({
        error: "Rate limit exceeded. Please slow down.",
      });
    }

    if (error instanceof telnyx.APIStatusError) {
      return res.status(error.status || 500).json({
        error: error.message,
        status_code: error.status,
      });
    }

    if (error instanceof telnyx.APIConnectionError) {
      return res.status(503).json({
        error: "Network error connecting to Telnyx",
      });
    }

    // Handle validation errors
    if (error.message.includes("required")) {
      return res.status(400).json({ error: error.message });
    }

    // Generic error fallback
    return res.status(500).json({
      error: "Internal server error",
      details: error.message,
    });
  }
});

/**
 * GET /assistants/:id
 * Retrieve details of a cloned assistant to verify the clone operation.
 */
app.get("/assistants/:id", async (req, res) => {
  const { id } = req.params;

  if (!id) {
    return res.status(400).json({ error: "Assistant ID is required" });
  }

  try {
    const response = await client.aiAssistants.retrieve(id);

    return res.json({
      id: response.data.id,
      name: response.data.name,
      model: response.data.model,
      instructions: response.data.instructions,
      tools: response.data.tools || [],
      enabled_features: response.data.enabled_features || [],
      created_at: response.data.created_at,
    });
  } catch (error) {
    if (error instanceof telnyx.AuthenticationError) {
      return res.status(401).json({ error: "Invalid API key" });
    }

    if (error instanceof telnyx.APIStatusError) {
      return res.status(error.status || 500).json({
        error: error.message,
        status_code: error.status,
      });
    }

    return res.status(500).json({
      error: "Failed to retrieve assistant",
      details: error.message,
    });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`POST /assistants/clone - Clone an assistant`);
  console.log(`GET /assistants/:id - Retrieve assistant details`);
});
