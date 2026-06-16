using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Models;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class SessionsViewModel : ObservableObject
{
    [ObservableProperty] bool   isBusy = false;
    [ObservableProperty] string title  = "Sessions";

    public ObservableCollection<SessionSummaryOut> Sessions { get; } = [];

    private readonly ApiService _api;
    public SessionsViewModel(ApiService api) => _api = api;

    [RelayCommand]
    async Task LoadAsync()
    {
        IsBusy = true;
        Sessions.Clear();
        try
        {
            var list = await _api.GetAllSessionsAsync();
            Title = $"Sessions ({list.Count})";
            foreach (var s in list) Sessions.Add(s);
        }
        catch { }
        finally { IsBusy = false; }
    }

    [RelayCommand]
    async Task OpenSessionAsync(SessionSummaryOut session) =>
        await Shell.Current.GoToAsync($"session-detail?sessionId={session.Id}");
}
