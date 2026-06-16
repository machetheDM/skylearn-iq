using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using SkyLearnIQ.Tutor.Models;

namespace SkyLearnIQ.Tutor.Services;

public class ApiService
{
    private const string BaseUrl = "http://localhost:8001";

    private static readonly HttpClient _http = new() { BaseAddress = new Uri(BaseUrl) };

    private static readonly JsonSerializerOptions _json = new()
    {
        PropertyNamingPolicy    = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true,
    };

    private readonly AuthService _auth;
    public ApiService(AuthService auth) => _auth = auth;

    private void SetAuth() =>
        _http.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", _auth.Token);

    private async Task<T> GetAsync<T>(string path)
    {
        SetAuth();
        var res = await _http.GetAsync(path);
        res.EnsureSuccessStatusCode();
        return JsonSerializer.Deserialize<T>(await res.Content.ReadAsStringAsync(), _json)!;
    }

    private async Task PostAsync(string path, object body)
    {
        SetAuth();
        var content = new StringContent(JsonSerializer.Serialize(body, _json), Encoding.UTF8, "application/json");
        (await _http.PostAsync(path, content)).EnsureSuccessStatusCode();
    }

    private async Task PatchAsync(string path, object? body = null)
    {
        SetAuth();
        var content = body is null
            ? new StringContent("", Encoding.UTF8, "application/json")
            : new StringContent(JsonSerializer.Serialize(body, _json), Encoding.UTF8, "application/json");
        (await _http.PatchAsync(path, content)).EnsureSuccessStatusCode();
    }

    // ── Auth ──────────────────────────────────────────────────────────────────
    public async Task<AuthUser> LoginAsync(string phone, string password)
    {
        var body    = new { phone, password };
        var content = new StringContent(JsonSerializer.Serialize(body, _json), Encoding.UTF8, "application/json");
        var res     = await _http.PostAsync("/api/auth/login", content);
        if (!res.IsSuccessStatusCode)
        {
            var raw = await res.Content.ReadAsStringAsync();
            var doc = JsonDocument.Parse(raw);
            throw new Exception(doc.RootElement.GetProperty("detail").GetString() ?? "Login failed");
        }
        return JsonSerializer.Deserialize<AuthUser>(await res.Content.ReadAsStringAsync(), _json)!;
    }

    // ── Learners ──────────────────────────────────────────────────────────────
    public Task<List<LearnerOut>> GetLearnersAsync() =>
        GetAsync<List<LearnerOut>>("/api/users/learners");

    // ── Assessments ───────────────────────────────────────────────────────────
    public Task<List<AssessmentOut>> GetAssessmentsAsync() =>
        GetAsync<List<AssessmentOut>>("/api/assessments");

    public Task PublishAssessmentAsync(int assessmentId) =>
        PatchAsync($"/api/assessments/{assessmentId}/publish");

    // ── Sessions ──────────────────────────────────────────────────────────────
    public Task<List<SessionSummaryOut>> GetAllSessionsAsync() =>
        GetAsync<List<SessionSummaryOut>>("/api/sessions/tutor/sessions");

    public Task<SessionOut> GetSessionAsync(int sessionId) =>
        GetAsync<SessionOut>($"/api/sessions/{sessionId}");

    public Task AddFeedbackAsync(int sessionId, string content, string? strengths, string? weaknesses, string? recommendations) =>
        PostAsync($"/api/sessions/{sessionId}/feedback", new
        {
            content,
            strength_areas   = strengths,
            weakness_areas   = weaknesses,
            recommendations
        });

    public Task MarkAnswerAsync(int sessionId, int answerId, float marksAwarded, bool isCorrect) =>
        PatchAsync($"/api/sessions/{sessionId}/answers/{answerId}/mark",
            new { marks_awarded = marksAwarded, is_correct = isCorrect });
}
