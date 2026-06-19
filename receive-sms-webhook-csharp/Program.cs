// Program.cs
using DotNetEnv;

var builder = WebApplicationBuilder.CreateBuilder(args);

// Load environment variables from .env file
Env.Load();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();

// Models/WebhookEvent.cs
namespace TelnyxSmsWebhook.Models
{
    public class WebhookEvent
    {
        public string? EventType { get; set; }
        public MessageData? Data { get; set; }
    }

    public class MessageData
    {
        public string? Id { get; set; }
        public string? Direction { get; set; }
        public string? From { get; set; }
        public string? To { get; set; }
        public string? Text { get; set; }
        public string? Type { get; set; }
        public DateTime? CreatedAt { get; set; }
    }
}

// Controllers/WebhookController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxSmsWebhook.Models;
using System.Security.Cryptography;
using System.Text;

namespace TelnyxSmsWebhook.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class WebhookController : ControllerBase
    {
        private readonly ILogger<WebhookController> _logger;

        public WebhookController(ILogger<WebhookController> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Receives inbound SMS webhooks from Telnyx.
        /// Validates webhook signature and processes message.received events.
        /// </summary>
        [HttpPost("sms")]
        public IActionResult ReceiveSmsWebhook([FromBody] WebhookEvent? webhookEvent)
        {
            // Validate request body
            if (webhookEvent == null)
            {
                _logger.LogWarning("Received webhook with null body");
                return BadRequest(new { error = "Request body required" });
            }

            // Validate webhook signature from request headers
            var signatureHeader = Request.Headers["Telnyx-Signature-Token"].ToString();
            if (string.IsNullOrEmpty(signatureHeader))
            {
                _logger.LogWarning("Received webhook without signature token");
                return Unauthorized(new { error = "Missing signature token" });
            }

            // Verify signature to ensure request came from Telnyx
            if (!VerifyWebhookSignature(signatureHeader))
            {
                _logger.LogWarning("Webhook signature verification failed");
                return Unauthorized(new { error = "Invalid signature" });
            }

            // Process only message.received events (inbound SMS)
            if (webhookEvent.EventType != "message.received")
            {
                _logger.LogInformation($"Ignoring event type: {webhookEvent.EventType}");
                return Ok(new { status = "ignored" });
            }

            // Extract message data
            var messageData = webhookEvent.Data;
            if (messageData == null)
            {
                _logger.LogWarning("Received message.received event with null data");
                return BadRequest(new { error = "Message data missing" });
            }

            // Log the inbound message
            _logger.LogInformation(
                $"Inbound SMS received - ID: {messageData.Id}, From: {messageData.From}, To: {messageData.To}, Text: {messageData.Text}"
            );

            // Return success response to Telnyx (prevents retry)
            return Ok(new
            {
                status = "received",
                message_id = messageData.Id,
                from = messageData.From,
                to = messageData.To,
                text = messageData.Text
            });
        }

        /// <summary>
        /// Verifies the webhook signature using HMAC-SHA256.
        /// Telnyx signs each webhook with your webhook signing secret.
        /// </summary>
        private bool VerifyWebhookSignature(string signature)
        {
            var secret = Environment.GetEnvironmentVariable("WEBHOOK_SIGNING_SECRET");
            if (string.IsNullOrEmpty(secret))
            {
                _logger.LogError("WEBHOOK_SIGNING_SECRET environment variable not set");
                return false;
            }

            try
            {
                // Read the raw request body for signature verification
                Request.Body.Position = 0;
                using (var reader = new StreamReader(Request.Body))
                {
                    var body = reader.ReadToEndAsync().Result;
                    Request.Body.Position = 0;

                    // Compute HMAC-SHA256 of the request body
                    using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret)))
                    {
                        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(body));
                        var computedSignature = Convert.ToBase64String(hash);

                        // Compare computed signature with provided signature
                        return computedSignature == signature;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError($"Error verifying webhook signature: {ex.Message}");
                return false;
            }
        }
    }
}
