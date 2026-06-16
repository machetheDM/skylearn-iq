using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Models;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    [ObservableProperty] bool   isBusy       = false;
    [ObservableProperty] int    totalSessions = 0;
    [ObservableProperty] int    completed     = 0;
    [ObservableProperty] int    inProgress    = 0;
    [ObservableProperty] string avgScore      = "—";
    [ObservableProperty] string tutorName     = "";

    public ObservableCollection<SessionSummaryOut> RecentSessions { get; } = [];

    private readonly ApiService  _api;
    private readonly AuthService _auth;

    public DashboardViewModel(ApiService api, AuthService auth)
    {
        _api  = api;
        _auth = auth;
        TutorName = _auth.FullName ?? "Tutor";
    }

    [RelayCommand]
    async Task LoadAsync()
    {
        IsBusy = true;
        RecentSessions.Clear();
        try
        {
            var sessions = await _api.GetAllSessionsAsync();
            TotalSessions = sessions.Count;
            Completed     = sessions.Count(s => s.Status == "COMPLETED");
            InProgress    = sessions.Count(s => s.Status == "IN_PROGRESS");
            var withScore = sessions.Where(s => s.Score != null).ToList();
            AvgScore = withScore.Count > 0
                ? $"{Math.Round(withScore.Average(s => s.Score!.Percentage))}%"
                : "—";
            foreach (var s in sessions.Take(10))
                RecentSessions.Add(s);
        }
        catch { }
        finally { IsBusy = false; }
    }
}
