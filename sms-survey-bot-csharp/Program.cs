// Program.cs
using DotNetEnv;
using TelnyxSMSSurvey.Models;
using TelnyxSMSSurvey.Services;

Env.Load();

var builder = WebApplication.CreateBuilder(args);

var surveyConfig = new SurveyConfig
{
    TelnyxApiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY"),
    TelnyxPhoneNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER"),
    WebhookUrl = Environment.GetEnvironmentVariable("WEBHOOK_URL")
};

builder.Services.AddSingleton(surveyConfig);
builder.Services.AddSingleton<SurveyService>();
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

// Models/SurveyConfig.cs
namespace TelnyxSMSSurvey.Models
{
    public class SurveyConfig
    {
        public string TelnyxApiKey { get; set; }
        public string TelnyxPhoneNumber { get; set; }
        public string WebhookUrl { get; set; }
    }
}

// Models/SurveyState.cs
namespace TelnyxSMSSurvey.Models
{
    public class SurveyState
    {
        public string PhoneNumber { get; set; }
        public int CurrentQuestion { get; set; }
        public Dictionary<int, string> Responses { get; set; } = new();
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public bool IsComplete { get; set; } = false;
    }
}

// Models/WebhookPayload.cs
namespace TelnyxSMSSurvey.Models
{
    public class WebhookPayload
    {
        [Newtonsoft.Json.JsonProperty("data")]
        public WebhookData Data { get; set; }
    }

    public class WebhookData
    {
        [Newtonsoft.Json.JsonProperty("id")]
        public string Id { get; set; }

        [Newtonsoft.Json.JsonProperty("from")]
        public WebhookPhone From { get; set; }

        [Newtonsoft.Json.JsonProperty("to")]
        public List<WebhookPhone> To { get; set; }

        [Newtonsoft.Json.JsonProperty("text")]
        public string Text { get; set; }

        [Newtonsoft.Json.JsonProperty("direction")]
        public string Direction { get; set; }
    }

    public class WebhookPhone
    {
        [Newtonsoft.Json.JsonProperty("phone_number")]
        public string PhoneNumber { get; set; }
    }
}

// Services/SurveyService.cs
using System.Net.Http.Headers;
using Newtonsoft.Json;
using TelnyxSMSSurvey.Models;

namespace TelnyxSMSSurvey.Services
{
    public class SurveyService
    {
        private readonly HttpClient _httpClient;
        private readonly SurveyConfig _config;
        private readonly Dictionary<string, SurveyState> _surveyStates;

        private readonly List<string> _questions = new()
        {
            "How satisfied are you with our service? Reply: 1 (Very Satisfied), 2 (Satisfied), 3 (Neutral), 4 (Dissatisfied)",
            "How likely are you to recommend us? Reply: 1 (Very Likely), 2 (Likely), 3 (Unlikely), 4 (Very Unlikely)",
            "What is your primary use case? Reply: 1 (Business), 2 (Personal), 3 (Other)"
        };

        public SurveyService(SurveyConfig config)
        {
            _config = config;
            _surveyStates = new Dictionary<string, SurveyState>();
            
            _httpClient = new HttpClient();
            _httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", _config.TelnyxApiKey);
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "TelnyxSMSSurvey/1.0");
        }

        public async Task<Dictionary<string, object>> StartSurveyAsync(string toNumber)
        {
            if (!toNumber.StartsWith("+"))
                throw new ArgumentException("Phone number must be in E.164 format (e.g., +15551234567)");

            _surveyStates[toNumber] = new SurveyState
            {
                PhoneNumber = toNumber,
                CurrentQuestion = 0
            };

            await SendSurveyQuestionAsync(toNumber, 0);

            return new Dictionary<string, object>
            {
                { "message", "Survey started" },
                { "phone_number", toNumber },
                { "question_count", _questions.Count }
            };
        }

        private async Task SendSurveyQuestionAsync(string toNumber, int questionIndex)
        {
            if (questionIndex >= _questions.Count)
                return;

            var question = _questions[questionIndex];
            await SendSmsAsync(toNumber, $"Question {questionIndex + 1}/{_questions.Count}: {question}");
        }

        public async Task<Dictionary<string, object>> ProcessResponseAsync(string fromNumber, string responseText)
        {
            if (!_surveyStates.ContainsKey(fromNumber))
            {
                await SendSmsAsync(fromNumber, "No active survey found. Reply START to begin.");
                return new Dictionary<string, object> { { "status", "no_survey" } };
            }

            var state = _surveyStates[fromNumber];

            state.Responses[state.CurrentQuestion] = responseText.Trim();
            state.CurrentQuestion++;

            if (state.CurrentQuestion >= _questions.Count)
            {
                state.IsComplete = true;
                await SendSmsAsync(fromNumber, "Thank you for completing the survey! Your responses have been recorded.");
                return new Dictionary<string, object>
                {
                    { "status", "complete" },
                    { "responses", state.Responses }
                };
            }

            await SendSurveyQuestionAsync(fromNumber, state.CurrentQuestion);

            return new Dictionary<string, object>
            {
                { "status", "in_progress" },
                { "current_question", state.CurrentQuestion + 1 },
                { "total_questions", _questions.Count }
            };
        }

        private async Task SendSmsAsync(string toNumber, string messageText)
        {
            var payload = new
            {
                from_ = _config.TelnyxPhoneNumber,
                to = toNumber,
                text = messageText
            };

            var content = new StringContent(
                JsonConvert.SerializeObject(payload),
                System.Text.Encoding.UTF8,
                "application/json"
            );

            var response = await _httpClient.PostAsync(
                "https://api.telnyx.com/v2/messages",
                content
            );

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                throw new HttpRequestException(
                    $"Telnyx API error: {response.StatusCode} - {errorContent}"
                );
            }
        }

        public Dictionary<string, object> GetSurveyResults(string phoneNumber)
        {
            if (!_surveyStates.ContainsKey(phoneNumber))
                throw new KeyNotFoundException($"No survey found for {phoneNumber}");

            var state = _surveyStates[phoneNumber];
            return new Dictionary<string, object>
            {
                { "phone_number", phoneNumber },
                { "is_complete", state.IsComplete },
                { "responses", state.Responses },
                { "created_at", state.CreatedAt }
            };
        }
    }
}

// Controllers/SurveyController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxSMSSurvey.Models;
using TelnyxSMSSurvey.Services;

namespace TelnyxSMSSurvey.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SurveyController : ControllerBase
    {
        private readonly SurveyService _surveyService;

        public SurveyController(SurveyService surveyService)
        {
            _surveyService = surveyService;
        }

        [HttpPost("start")]
        public async Task<IActionResult> StartSurvey([FromBody] StartSurveyRequest request)
        {
            if (string.IsNullOrEmpty(request?.PhoneNumber))
                return BadRequest(new { error = "Phone number is required" });

            try
            {
                var result = await _surveyService.StartSurveyAsync(request.PhoneNumber);
                return Ok(result);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (HttpRequestException ex)
            {
                return StatusCode(503, new { error = "Failed to send SMS", details = ex.Message });
            }
        }

        [HttpPost("webhooks/sms")]
        public async Task<IActionResult> ReceiveSmsWebhook([FromBody] WebhookPayload payload)
        {
            if (payload?.Data == null)
                return BadRequest(new { error = "Invalid webhook payload" });

            if (payload.Data.Direction != "inbound")
                return Ok(new { status = "ignored" });

            var fromNumber = payload.Data.From?.PhoneNumber;
            var messageText = payload.Data.Text;

            if (string.IsNullOrEmpty(fromNumber) || string.IsNullOrEmpty(messageText))
                return BadRequest(new { error = "Missing required fields" });

            try
            {
                var result = await _surveyService.ProcessResponseAsync(fromNumber, messageText);
                return Ok(result);
            }
            catch (HttpRequestException ex)
            {
                return StatusCode(503, new { error = "Failed to process response", details = ex.Message });
            }
        }

        [HttpGet("results/{phoneNumber}")]
        public IActionResult GetResults(string phoneNumber)
        {
            try
            {
                var results = _surveyService.GetSurveyResults(phoneNumber);
                return Ok(results);
            }
            catch (KeyNotFoundException ex)
            {
                return NotFound(new { error = ex.Message });
            }
        }
    }

    public class StartSurveyRequest
    {
        public string PhoneNumber { get; set; }
    }
}
