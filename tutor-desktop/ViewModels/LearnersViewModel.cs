using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Models;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class LearnersViewModel : ObservableObject
{
    [ObservableProperty] bool   isBusy = false;
    [ObservableProperty] string title  = "Learners";

    public ObservableCollection<LearnerOut> Learners { get; } = [];

    private readonly ApiService _api;
    public LearnersViewModel(ApiService api) => _api = api;

    [RelayCommand]
    async Task LoadAsync()
    {
        IsBusy = true;
        Learners.Clear();
        try
        {
            var list = await _api.GetLearnersAsync();
            Title = $"Learners ({list.Count})";
            foreach (var l in list) Learners.Add(l);
        }
        catch { }
        finally { IsBusy = false; }
    }
}
