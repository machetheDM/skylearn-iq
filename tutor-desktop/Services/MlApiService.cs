/*
 * Calls the ML Analytics Engine on port 8002.
 * Ensure ml-engine is running: python -m uvicorn main:app --port 8002 (from ml-engine/)
 */
using System.Net.Http.Headers;
using System.Text.Json;
using SkyLearnIQ.Tutor.Models;

namespace SkyLearnIQ.Tutor.Services;

public class MlApiService
{
    private const string MlBaseUrl = "http://localhost:8002";

    private static readonly HttpClient _http = new() { BaseAddress = new Uri(MlBaseUrl) };

    private static readonly JsonSerializerOptions _json = new()
    {
        PropertyNamingPolicy        = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = true,
    };

    private readonly AuthService _auth;
    public MlApiService(AuthService auth) => _auth = auth;

    private async Task<T> GetAsync<T>(string path)
    {
        _http.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", _auth.Token);
        var res = await _http.GetAsync(path);
        res.EnsureSuccessStatusCode();
        return JsonSerializer.Deserialize<T>(await res.Content.ReadAsStringAsync(), _json)!;
    }

    public Task<List<AtRiskResult>>  GetAtRiskAsync()  => GetAsync<List<AtRiskResult>>("/api/ml/at-risk");
    public Task<List<ClusterResult>> GetClustersAsync() => GetAsync<List<ClusterResult>>("/api/ml/clusters");
    public Task<AnalyticsSummary>    GetSummaryAsync()  => GetAsync<AnalyticsSummary>("/api/ml/summary");
}
