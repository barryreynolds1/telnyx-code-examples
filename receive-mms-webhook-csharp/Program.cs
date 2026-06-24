// Program.cs
using Microsoft.Extensions.Configuration;
using TelnyxMmsReceiver.Configuration;
using TelnyxMmsReceiver.Services;

var builder = WebApplication.CreateBuilder(args);

// Load secrets from user-secrets in development
if (builder.Environment.IsDevelopment())
{
    builder.Configuration.AddUserSecrets<Program>();
}

// Bind Telnyx configuration
builder.Services.Configure<TelnyxOptions>(
    builder.Configuration.GetSection("Telnyx"));

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddScoped<IMmsService, MmsService>();

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

// ============================================================================

// Configuration/TelnyxOptions.cs
namespace TelnyxMmsReceiver.Configuration
{
    public class TelnyxOptions
    {
        public string ApiKey { get; set; }
        public string WebhookSecret { get; set; }
    }
}

// ============================================================================

// Models/MmsWebhookPayload.cs
using System.Text.Json.Serialization;

namespace TelnyxMmsReceiver.Models
{
    public class MmsWebhookPayload
    {
        [JsonPropertyName("data")]
        public MmsMessageData Data { get; set; }
        
        [JsonPropertyName("meta")]
        public WebhookMeta Meta { get; set; }
    }

    public class MmsMessageData
    {
        [JsonPropertyName("id")]
        public string Id { get; set; }

        [JsonPropertyName("type")]
        public string Type { get; set; }

        [JsonPropertyName("attributes")]
        public MmsAttributes Attributes { get; set; }
    }

    public class MmsAttributes
    {
        [JsonPropertyName("from")]
        public PhoneNumber From { get; set; }

        [JsonPropertyName("to")]
        public List<PhoneNumber> To { get; set; }

        [JsonPropertyName("text")]
        public string Text { get; set; }

        [JsonPropertyName("media_urls")]
        public List<string> MediaUrls { get; set; }

        [JsonPropertyName("received_at")]
        public DateTime ReceivedAt { get; set; }

        [JsonPropertyName("direction")]
        public string Direction { get; set; }
    }

    public class PhoneNumber
    {
        [JsonPropertyName("phone_number")]
        public string Number { get; set; }

        [JsonPropertyName("status")]
        public string Status { get; set; }
    }

    public class WebhookMeta
    {
        [JsonPropertyName("attempt_number")]
        public int AttemptNumber { get; set; }

        [JsonPropertyName("delivered_at")]
        public DateTime DeliveredAt { get; set; }
    }
}

// ============================================================================

// Services/MmsService.cs
using Microsoft.Extensions.Logging;
using TelnyxMmsReceiver.Models;

namespace TelnyxMmsReceiver.Services
{
    public interface IMmsService
    {
        Task<MmsMessageResponse> ProcessInboundMmsAsync(MmsWebhookPayload payload);
    }

    public class MmsService : IMmsService
    {
        private readonly ILogger<MmsService> _logger;

        public MmsService(ILogger<MmsService> logger)
        {
            _logger = logger;
        }

        public async Task<MmsMessageResponse> ProcessInboundMmsAsync(MmsWebhookPayload payload)
        {
            if (payload?.Data?.Attributes == null)
            {
                throw new ArgumentException("Invalid MMS payload structure");
            }

            var attributes = payload.Data.Attributes;

            if (attributes.From == null || string.IsNullOrEmpty(attributes.From.Number))
            {
                throw new ArgumentException("Sender phone number is required");
            }

            if (attributes.To == null || attributes.To.Count == 0)
            {
                throw new ArgumentException("Recipient phone number is required");
            }

            _logger.LogInformation(
                "Received MMS from {From} to {To} with {MediaCount} attachments at {ReceivedAt}",
                attributes.From.Number,
                string.Join(", ", attributes.To.Select(t => t.Number)),
                attributes.MediaUrls?.Count ?? 0,
                attributes.ReceivedAt);

            var processedMediaUrls = new List<string>();
            if (attributes.MediaUrls != null && attributes.MediaUrls.Count > 0)
            {
                foreach (var mediaUrl in attributes.MediaUrls)
                {
                    if (Uri.TryCreate(mediaUrl, UriKind.Absolute, out var uri))
                    {
                        processedMediaUrls.Add(mediaUrl);
                        _logger.LogInformation("Processed media attachment: {MediaUrl}", mediaUrl);
                    }
                    else
                    {
                        _logger.LogWarning("Invalid media URL format: {MediaUrl}", mediaUrl);
                    }
                }
            }

            await Task.Delay(100);

            return new MmsMessageResponse
            {
                MessageId = payload.Data.Id,
                From = attributes.From.Number,
                To = attributes.To.First().Number,
                Text = attributes.Text ?? string.Empty,
                MediaCount = processedMediaUrls.Count,
                ReceivedAt = attributes.ReceivedAt,
                ProcessedAt = DateTime.UtcNow
            };
        }
    }

    public class MmsMessageResponse
    {
        public string MessageId { get; set; }
        public string From { get; set; }
        public string To { get; set; }
        public string Text { get; set; }
        public int MediaCount { get; set; }
        public DateTime ReceivedAt { get; set; }
        public DateTime ProcessedAt { get; set; }
    }
}

// ============================================================================

// Controllers/MmsWebhookController.cs
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;
using System.Security.Cryptography;
using System.Text;
using TelnyxMmsReceiver.Configuration;
using TelnyxMmsReceiver.Models;
using TelnyxMmsReceiver.Services;

namespace TelnyxMmsReceiver.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MmsWebhookController : ControllerBase
    {
        private readonly IMmsService _mmsService;
        private readonly ILogger<MmsWebhookController> _logger;
        private readonly TelnyxOptions _telnyxOptions;

        public MmsWebhookController(
            IMmsService mmsService,
            ILogger<MmsWebhookController> logger,
            IOptions<TelnyxOptions> telnyxOptions)
        {
            _mmsService = mmsService;
            _logger = logger;
            _telnyxOptions = telnyxOptions.Value;
        }

        [HttpPost("receive")]
        public async Task<IActionResult> ReceiveMms([FromBody] MmsWebhookPayload payload)
        {
            if (!string.IsNullOrEmpty(_telnyxOptions.WebhookSecret))
            {
                if (!ValidateWebhookSignature(Request, _telnyxOptions.WebhookSecret))
                {
                    _logger.LogWarning("Webhook signature validation failed");
                    return Unauthorized(new { error = "Invalid webhook signature" });
                }
            }

            if (payload == null || payload.Data == null)
            {
                _logger.LogWarning("Received invalid MMS webhook payload");
                return BadRequest(new { error = "Invalid payload structure" });
            }

            try
            {
                var result = await _mmsService.ProcessInboundMmsAsync(payload);

                _logger.LogInformation(
                    "Successfully processed MMS {MessageId} from {From}",
                    result.MessageId,
                    result.From);

                return Ok(new
                {
                    messageId = result.MessageId,
                    from = result.From,
                    to = result.To,
                    text = result.Text,
                    mediaCount = result.MediaCount,
                    receivedAt = result.ReceivedAt,
                    processedAt = result.ProcessedAt
                });
            }
            catch (ArgumentException ex)
            {
                _logger.LogError("Validation error processing MMS: {Error}", ex.Message);
                return BadRequest(new { error = ex.Message });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error processing MMS webhook");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        private bool ValidateWebhookSignature(HttpRequest request, string secret)
        {
            if (!request.Headers.TryGetValue("X-Telnyx-Signature-V2", out var signatureHeader))
            {
                _logger.LogWarning("Missing webhook signature header");
                return false;
            }

            request.Body.Position = 0;
            using (var reader = new StreamReader(request.Body, Encoding.UTF8, leaveOpen: true))
            {
                var body = reader.ReadToEndAsync().Result;
                request.Body.Position = 0;

                using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret)))
                {
                    var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(body));
                    var computedSignature = Convert.ToBase64String(hash);

                    return CryptographicOperations.FixedTimeEquals(
                        Encoding.UTF8.GetBytes(signatureHeader.ToString()),
                        Encoding.UTF8.GetBytes(computedSignature));
                }
            }
        }
    }
}
