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
