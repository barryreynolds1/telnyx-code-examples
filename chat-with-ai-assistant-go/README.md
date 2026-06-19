# Chat With AI Assistant with Go and Gin

## What Does This Example Do?

Build a production-ready Gin endpoint that enables real-time chat interactions with Telnyx AI Assistants. This tutorial demonstrates the Go SDK client initialization pattern, proper error handling for AI API calls, and secure credential management via environment variables. You'll create a conversational interface where users can send messages and receive intelligent responses from a pre-configured AI assistant.

## Who Is This For?

- **Go developers** building ai features with Gin.
- **Backend engineers** integrating telephony or messaging into existing applications.
- **DevOps teams** looking for containerized, production-ready telecom examples.
- **Startups and enterprises** replacing legacy telecom providers with a modern API-first platform.

## Why Telnyx?

Telnyx is an **AI Communications Infrastructure** platform that gives developers a single API for [voice](https://telnyx.com/products/voice-ai-agents), [messaging](https://telnyx.com/products/sms-api), [SIP](https://telnyx.com/products/sip-trunks), [AI](https://telnyx.com/ai-assistants), and [IoT](https://telnyx.com/products/iot-sim-card) — no Frankenstack required.

- **Integrated platform** — [Voice](https://telnyx.com/products/voice-ai-agents), [SMS](https://telnyx.com/products/sms-api), [SIP trunking](https://telnyx.com/products/sip-trunks), [AI assistants](https://telnyx.com/ai-assistants), and [IoT SIM management](https://telnyx.com/products/iot-sim-card) under one roof. No stitching together multiple vendors.
- **Global private network** — Calls and messages traverse the Telnyx-owned IP network for lower latency and higher reliability than the public internet.
- **Developer-first** — SDKs for Python, Node.js, Go, Ruby, Java, and PHP. Comprehensive webhook event model. Sandbox environment for testing.
- **Competitive pricing** — Pay-as-you-go with no minimums, contracts, or per-seat fees.

## Prerequisites

- Go 1.19 or higher.
- A Telnyx account with an active API key from the [Telnyx Portal](https://portal.telnyx.com).
- An existing AI Assistant ID (create one via the portal or use the [Create AI Assistant](/tutorials/ai/go/create-ai-assistant) tutorial).
- go get (Go package manager).

## Quick Start

### Option 1: Local (recommended)

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-go
cp .env.example .env
# Edit .env with your Telnyx API key and phone number
make setup
make run
```

### Option 2: Docker

```bash
git clone https://github.com/team-telnyx/telnyx-code-examples.git
cd telnyx-code-examples/chat-with-ai-assistant-go
cp .env.example .env
# Edit .env with your credentials
make docker-build
make docker-run
```

### Option 3: Manual

See the [Implementation Details](#implementation-details) section below for step-by-step instructions.

## Implementation Details

Create `main.go` and initialize the Telnyx client using the Go SDK pattern. Define a helper function to handle chat interactions with proper validation:

```go
package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/telnyx/telnyx-go/v2"
	"github.com/telnyx/telnyx-go/v2/ai_assistants"
)

func init() {
	// Load environment variables from .env file
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}
}

// ChatRequest represents the incoming chat message payload
type ChatRequest struct {
	Message string `json:"message" binding:"required"`
}

// ChatResponse represents the AI assistant's response
type ChatResponse struct {
	AssistantID string `json:"assistant_id"`
	UserMessage string `json:"user_message"`
	Response    string `json:"response"`
}

// chatWithAssistant sends a message to the AI assistant and returns the response
func chatWithAssistant(assistantID string, userMessage string) (string, error) {
	client := telnyx.NewClient(telnyx.WithAPIKey(os.Getenv("TELNYX_API_KEY")))

	// Validate inputs before making API call
	if assistantID == "" {
		return "", fmt.Errorf("assistant ID is required")
	}
	if userMessage == "" {
		return "", fmt.Errorf("message cannot be empty")
	}

	// Call the AI assistant chat endpoint
	params := &ai_assistants.ChatParams{
		Messages: []*ai_assistants.ChatMessage{
			{
				Role:    "user",
				Content: userMessage,
			},
		},
	}

	response, err := client.AIAssistants.Chat(assistantID, params)
	if err != nil {
		return "", fmt.Errorf("failed to chat with assistant: %w", err)
	}

	// Extract the assistant's response from the API response
	if response != nil && len(response.Data.Messages) > 0 {
		// Find the assistant's response (last message with role "assistant")
		for i := len(response.Data.Messages) - 1; i >= 0; i-- {
			if response.Data.Messages[i].Role == "assistant" {
				return response.Data.Messages[i].Content, nil
			}
		}
	}

	return "", fmt.Errorf("no response received from assistant")
}

func main() {
	router := gin.Default()

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// Chat endpoint
	router.POST("/chat", func(c *gin.Context) {
		var req ChatRequest

		// Bind and validate JSON request
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		assistantID := os.Getenv("AI_ASSISTANT_ID")
		if assistantID == "" {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "AI_ASSISTANT_ID not configured"})
			return
		}

		// Call helper function to chat with assistant
		response, err := chatWithAssistant(assistantID, req.Message)

		// Handle errors with appropriate HTTP status codes
		if err != nil {
			// Check for specific Telnyx API errors
			if apiErr, ok := err.(*telnyx.APIStatusError); ok {
				c.JSON(apiErr.StatusCode, gin.H{"error": apiErr.Error()})
				return
			}

			// Handle authentication errors
			if _, ok := err.(*telnyx.AuthenticationError); ok {
				c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid API key"})
				return
			}

			// Handle rate limit errors
			if _, ok := err.(*telnyx.RateLimitError); ok {
				c.JSON(http.StatusTooManyRequests, gin.H{"error": "Rate limit exceeded. Please slow down."})
				return
			}

			// Handle connection errors
			if _, ok := err.(*telnyx.APIConnectionError); ok {
				c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Network error connecting to Telnyx"})
				return
			}

			// Generic error handling
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		// Return successful response
		c.JSON(http.StatusOK, ChatResponse{
			AssistantID: assistantID,
			UserMessage: req.Message,
			Response:    response,
		})
	})

	// Start the server
	port := ":8080"
	log.Printf("Starting Gin server on %s\n", port)
	if err := router.Run(port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
```

## Complete Code

See [`main.go`](./main.go) for the full implementation.

## Troubleshooting

| Issue | Problem | Solution |
|-------|---------|----------|
| Authentication Error (401) | The endpoint returns `{"error":"Invalid API key"}` with HTTP 401. | Verify your `TELNYX_API_KEY` in the `.env` file matches the key shown in the [Telnyx Portal](https://portal.telnyx.com). Ensure there are no trailing spaces or quotes. If the key was regenerated recently, update your environment file and restart the Gin server. |
| Assistant Not Found (404) | The API returns a 404 error or "assistant not found" message. | Confirm that the `AI_ASSISTANT_ID` in your `.env` file is correct and matches an existing assistant in your Telnyx account. Verify the assistant ID format—it should be a valid UUID. Check the [Telnyx Portal](https://portal.telnyx.com) to list your assistants and copy the correct ID. |
| Empty Response from Assistant | The endpoint returns `{"error":"no response received from assistant"}`. | Ensure your AI Assistant is properly configured with instructions and enabled features. Test the assistant directly in the Telnyx Portal to confirm it responds to messages. Verify that the message you're sending is not empty and is valid UTF-8 text. Check that the assistant's model is active and not in a disabled state. |
| Environment Variable Not Set | The application returns `{"error":"AI_ASSISTANT_ID not configured"}` or fails to initialize the client. | Confirm your `.env` file exists in the same directory as `main.go` and contains both `TELNYX_API_KEY` and `AI_ASSISTANT_ID`. Ensure the file is named exactly `.env` (not `.env.txt` or `env`). The `godotenv.Load()` call must execute before `os.Getenv()` is called—verify this import order in your code. |
| Rate Limit Error (429) | The endpoint returns `{"error":"Rate limit exceeded. Please slow down."}` with HTTP 429. | You are sending requests too quickly to the Telnyx API. Implement exponential backoff in your client code or add delays between requests. Check your API plan limits in the [Telnyx Portal](https://portal.telnyx.com) and consider upgrading if you need higher throughput. |

## FAQ

**Q: Do I need a Telnyx account to run this example?**

Yes. Sign up at [portal.telnyx.com](https://portal.telnyx.com) to get an API key. Telnyx offers free trial credit for testing.

**Q: Can I use this AI example in production?**

Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.

**Q: What Go version do I need?**

Go 1.22 or higher.

**Q: How is Telnyx different from Twilio?**

Telnyx is an AI Communications Infrastructure platform with a private global network, integrated voice + messaging + AI + SIP + IoT under one API, and significantly lower pricing. No need to stitch together multiple vendors.

**Q: Where do I get a Telnyx phone number?**

Log into the [Telnyx Portal](https://portal.telnyx.com), navigate to Numbers > Search & Buy, and purchase a number with the capabilities you need (SMS, voice, or both).

## Resources

- [AI Assistants Guide](https://developers.telnyx.com/docs/inference/ai-assistants/no-code-voice-assistant)
- [Assistants API Reference](https://developers.telnyx.com/api-reference/assistants/create-an-assistant)
- [Go SDK](https://developers.telnyx.com/development/sdk/go)
- [Telnyx AI Assistants](https://telnyx.com/ai-assistants)
- [Voice AI Agents](https://telnyx.com/products/voice-ai-agents)

## Related Examples

- [List AI Assistants](/tutorials/ai/go/list-ai-assistants).
- [Create an AI Assistant](/tutorials/ai/go/create-ai-assistant).
- [Update an AI Assistant](/tutorials/ai/go/update-ai-assistant).
