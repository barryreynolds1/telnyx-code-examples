// Program.cs
using TelnyxCnamLookup.Services;

DotNetEnv.Env.Load();

var builder = WebApplicationBuilder.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddHttpClient<CnamLookupService>();
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

// Services/CnamLookupService.cs
using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace TelnyxCnamLookup.Services
{
    public class CnamLookupService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;

        public CnamLookupService(HttpClient httpClient)
        {
            _httpClient = httpClient;
            _apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY")
                ?? throw new InvalidOperationException("TELNYX_API_KEY environment variable not set");

            _httpClient.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _apiKey);
            _httpClient.BaseAddress = new Uri("https://api.telnyx.com/v2");
        }

        public async Task<CnamLookupResponse> LookupCnamAsync(string phoneNumber)
        {
            if (string.IsNullOrWhiteSpace(phoneNumber) || !phoneNumber.StartsWith("+"))
            {
                throw new ArgumentException(
                    "Phone number must be in E.164 format (e.g., +15551234567)", 
                    nameof(phoneNumber));
            }

            try
            {
                var response = await _httpClient.GetAsync($"/cnam_lookups/{phoneNumber}");

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    throw new HttpRequestException(
                        $"CNAM lookup failed with status {response.StatusCode}: {errorContent}");
                }

                var result = await response.Content.ReadAsAsync<CnamLookupResponse>();
                return result;
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("401"))
            {
                throw new UnauthorizedAccessException("Invalid API key", ex);
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("429"))
            {
                throw new InvalidOperationException("Rate limit exceeded. Please slow down.", ex);
            }
        }
    }

    public class CnamLookupResponse
    {
        public CnamData Data { get; set; }
    }

    public class CnamData
    {
        public string PhoneNumber { get; set; }
        public string CallerName { get; set; }
        public string CallerNameType { get; set; }
    }
}

// Controllers/CnamController.cs
using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using TelnyxCnamLookup.Services;

namespace TelnyxCnamLookup.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class CnamController : ControllerBase
    {
        private readonly CnamLookupService _cnamService;

        public CnamController(CnamLookupService cnamService)
        {
            _cnamService = cnamService;
        }

        [HttpGet("lookup")]
        public async Task<IActionResult> LookupCnam([FromQuery] string phoneNumber)
        {
            if (string.IsNullOrWhiteSpace(phoneNumber))
            {
                return BadRequest(new { error = "Phone number is required" });
            }

            try
            {
                var result = await _cnamService.LookupCnamAsync(phoneNumber);

                return Ok(new
                {
                    phoneNumber = result.Data.PhoneNumber,
                    callerName = result.Data.CallerName,
                    callerNameType = result.Data.CallerNameType
                });
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (UnauthorizedAccessException)
            {
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (InvalidOperationException ex) when (ex.Message.Contains("Rate limit"))
            {
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"Unexpected error: {ex.Message}" });
            }
        }
    }
}
