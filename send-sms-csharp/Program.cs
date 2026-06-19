using Telnyx;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// Initialize client using new pattern — NOT Telnyx.api_key = ...
var client = new TelnyxClient(apiKey: Environment.GetEnvironmentVariable("TELNYX_API_KEY"));
builder.Services.AddSingleton(client);

var app = builder.Build();

// Request model for JSON binding
public class SendSmsRequest
{
    [JsonPropertyName("to")]
    public string To { get; set; }
    
    [JsonPropertyName("message")]
    public string Message { get; set; }
}

app.MapPost("/sms/send", async (SendSmsRequest request, TelnyxClient client) =>
{
    if (string.IsNullOrEmpty(request.To) || string.IsNullOrEmpty(request.Message))
    {
        return Results.BadRequest(new { error = "Missing required fields: 'to' and 'message'" });
    }

    var fromNumber = Environment.GetEnvironmentVariable("TELNYX_PHONE_NUMBER");
    if (string.IsNullOrEmpty(fromNumber))
    {
        return Results.BadRequest(new { error = "TELNYX_PHONE_NUMBER environment variable not set" });
    }

    // Validate E.164 format to prevent API errors
    if (!request.To.StartsWith("+"))
    {
        return Results.BadRequest(new { error = "Phone number must be in E.164 format (e.g., +15551234567)" });
    }

    try
    {
        // Use client.Messages.CreateAsync() — NOT Telnyx.Message.Create()
        var response = await client.Messages.CreateAsync(new MessageCreateOptions
        {
            From = fromNumber,
            To = request.To,
            Text = request.Message
        });

        // Extract serializable data — do not return raw response object
        return Results.Ok(new 
        {
            message_id = response.Id,
            status = response.To?.FirstOrDefault()?.Status ?? "unknown",
            from = fromNumber,
            to = request.To
        });
    }
    catch (Telnyx.AuthenticationError)
    {
        return Results.Json(new { error = "Invalid API key" }, statusCode: 401);
    }
    catch (Telnyx.RateLimitError)
    {
        return Results.Json(new { error = "Rate limit exceeded. Please slow down." }, statusCode: 429);
    }
    catch (Telnyx.APIStatusError e)
    {
        return Results.Json(new { error = e.Message, status_code = e.StatusCode }, statusCode: e.StatusCode);
    }
    catch (Telnyx.APIConnectionError)
    {
        return Results.Json(new { error = "Network error connecting to Telnyx" }, statusCode: 503);
    }
});

app.Run();
