// Program.cs
using TelnyxDeviceLocation.Models;
using TelnyxDeviceLocation.Services;

var builder = WebApplication.CreateBuilder(args);

// Load environment variables from .env file
var apiKey = Environment.GetEnvironmentVariable("TELNYX_API_KEY");
var apiBaseUrl = Environment.GetEnvironmentVariable("TELNYX_API_BASE_URL") 
    ?? "https://api.telnyx.com/v2";

// Register configuration
builder.Services.Configure<TelnyxConfig>(config =>
{
    config.ApiKey = apiKey;
    config.ApiBaseUrl = apiBaseUrl;
});

// Register HttpClient with Telnyx API configuration
builder.Services.AddHttpClient("TelnyxClient", client =>
{
    client.BaseAddress = new Uri(apiBaseUrl);
    client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}");
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});

builder.Services.AddScoped<ISimCardService, SimCardService>();
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

// Models/TelnyxConfig.cs
namespace TelnyxDeviceLocation.Models
{
    public class TelnyxConfig
    {
        public string ApiKey { get; set; }
        public string ApiBaseUrl { get; set; }
    }
}

// Models/SimCardLocation.cs
namespace TelnyxDeviceLocation.Models
{
    public class SimCardLocation
    {
        public string Id { get; set; }
        public string Iccid { get; set; }
        public string Status { get; set; }
        public LocationData Location { get; set; }
        public string SimCardGroupId { get; set; }
    }

    public class LocationData
    {
        public double Latitude { get; set; }
        public double Longitude { get; set; }
        public string Country { get; set; }
        public string Carrier { get; set; }
        public long? Timestamp { get; set; }
    }
}

// Services/ISimCardService.cs
namespace TelnyxDeviceLocation.Services
{
    public interface ISimCardService
    {
        Task<SimCardLocation> GetSimCardLocationAsync(string simCardId);
        Task<List<SimCardLocation>> ListSimCardsWithLocationAsync();
    }
}

// Services/SimCardService.cs
using System.Net.Http.Json;
using TelnyxDeviceLocation.Models;

namespace TelnyxDeviceLocation.Services
{
    public class SimCardService : ISimCardService
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<SimCardService> _logger;

        public SimCardService(IHttpClientFactory httpClientFactory, ILogger<SimCardService> logger)
        {
            _httpClient = httpClientFactory.CreateClient("TelnyxClient");
            _logger = logger;
        }

        public async Task<SimCardLocation> GetSimCardLocationAsync(string simCardId)
        {
            try
            {
                var response = await _httpClient.GetAsync($"/sim_cards/{simCardId}");
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError($"Failed to fetch SIM card {simCardId}: {response.StatusCode}");
                    throw new HttpRequestException($"API returned {response.StatusCode}");
                }

                var jsonContent = await response.Content.ReadAsAsync<dynamic>();
                
                var simCard = new SimCardLocation
                {
                    Id = jsonContent.data.id,
                    Iccid = jsonContent.data.iccid,
                    Status = jsonContent.data.status,
                    SimCardGroupId = jsonContent.data.sim_card_group_id,
                    Location = ExtractLocationFromResponse(jsonContent.data)
                };

                return simCard;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error retrieving SIM card location: {ex.Message}");
                throw;
            }
        }

        public async Task<List<SimCardLocation>> ListSimCardsWithLocationAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/sim_cards?limit=100");
                
                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError($"Failed to list SIM cards: {response.StatusCode}");
                    throw new HttpRequestException($"API returned {response.StatusCode}");
                }

                var jsonContent = await response.Content.ReadAsAsync<dynamic>();
                var simCards = new List<SimCardLocation>();

                foreach (var item in jsonContent.data)
                {
                    simCards.Add(new SimCardLocation
                    {
                        Id = item.id,
                        Iccid = item.iccid,
                        Status = item.status,
                        SimCardGroupId = item.sim_card_group_id,
                        Location = ExtractLocationFromResponse(item)
                    });
                }

                return simCards;
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"HTTP error listing SIM cards: {ex.Message}");
                throw;
            }
        }

        private LocationData ExtractLocationFromResponse(dynamic simCardData)
        {
            try
            {
                return new LocationData
                {
                    Latitude = simCardData.location?.latitude ?? 0,
                    Longitude = simCardData.location?.longitude ?? 0,
                    Country = simCardData.location?.country ?? "Unknown",
                    Carrier = simCardData.carrier_name ?? "Unknown",
                    Timestamp = simCardData.location?.timestamp ?? null
                };
            }
            catch
            {
                return new LocationData
                {
                    Latitude = 0,
                    Longitude = 0,
                    Country = "Unknown",
                    Carrier = "Unknown",
                    Timestamp = null
                };
            }
        }
    }
}

// Controllers/DeviceLocationController.cs
using Microsoft.AspNetCore.Mvc;
using TelnyxDeviceLocation.Models;
using TelnyxDeviceLocation.Services;

namespace TelnyxDeviceLocation.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DeviceLocationController : ControllerBase
    {
        private readonly ISimCardService _simCardService;
        private readonly ILogger<DeviceLocationController> _logger;

        public DeviceLocationController(ISimCardService simCardService, ILogger<DeviceLocationController> logger)
        {
            _simCardService = simCardService;
            _logger = logger;
        }

        [HttpGet("{simCardId}")]
        public async Task<IActionResult> GetSimCardLocation(string simCardId)
        {
            if (string.IsNullOrWhiteSpace(simCardId))
            {
                return BadRequest(new { error = "SIM card ID is required" });
            }

            try
            {
                var location = await _simCardService.GetSimCardLocationAsync(simCardId);
                
                return Ok(new
                {
                    id = location.Id,
                    iccid = location.Iccid,
                    status = location.Status,
                    sim_card_group_id = location.SimCardGroupId,
                    location = new
                    {
                        latitude = location.Location.Latitude,
                        longitude = location.Location.Longitude,
                        country = location.Location.Country,
                        carrier = location.Location.Carrier,
                        timestamp = location.Location.Timestamp
                    }
                });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("404"))
            {
                _logger.LogWarning($"SIM card not found: {simCardId}");
                return NotFound(new { error = "SIM card not found" });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("401"))
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("429"))
            {
                _logger.LogWarning("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }

        [HttpGet]
        public async Task<IActionResult> ListSimCardsWithLocation()
        {
            try
            {
                var simCards = await _simCardService.ListSimCardsWithLocationAsync();
                
                var result = simCards.Select(s => new
                {
                    id = s.Id,
                    iccid = s.Iccid,
                    status = s.Status,
                    sim_card_group_id = s.SimCardGroupId,
                    location = new
                    {
                        latitude = s.Location.Latitude,
                        longitude = s.Location.Longitude,
                        country = s.Location.Country,
                        carrier = s.Location.Carrier,
                        timestamp = s.Location.Timestamp
                    }
                }).ToList();

                return Ok(result);
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("401"))
            {
                _logger.LogError("Authentication failed: Invalid API key");
                return Unauthorized(new { error = "Invalid API key" });
            }
            catch (HttpRequestException ex) when (ex.Message.Contains("429"))
            {
                _logger.LogWarning("Rate limit exceeded");
                return StatusCode(429, new { error = "Rate limit exceeded. Please slow down." });
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError($"API error: {ex.Message}");
                return StatusCode(503, new { error = "Network error connecting to Telnyx" });
            }
            catch (Exception ex)
            {
                _logger.LogError($"Unexpected error: {ex.Message}");
                return StatusCode(500, new { error = "Internal server error" });
            }
        }
    }
}
