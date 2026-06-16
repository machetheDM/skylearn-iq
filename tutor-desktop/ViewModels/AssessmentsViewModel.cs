using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Models;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class AssessmentsViewModel : ObservableObject
{
    [ObservableProperty] bool   isBusy = false;
    [ObservableProperty] string title  = "Assessments";
    [ObservableProperty] string statusMessage = "";

    public ObservableCollection<AssessmentOut> Assessments { get; } = [];

    private readonly ApiService _api;
    public AssessmentsViewModel(ApiService api) => _api = api;

    [RelayCommand]
    async Task LoadAsync()
    {
        IsBusy = true;
        Assessments.Clear();
        StatusMessage = "";
        try
        {
            var list = await _api.GetAssessmentsAsync();
            Title = $"Assessments ({list.Count})";
            foreach (var a in list) Assessments.Add(a);
        }
        catch { }
        finally { IsBusy = false; }
    }

    [RelayCommand]
    async Task PublishAsync(AssessmentOut assessment)
    {
        if (assessment.IsPublished)
        {
            StatusMessage = $"'{assessment.Title}' is already published.";
            return;
        }
        try
        {
            await _api.PublishAssessmentAsync(assessment.Id);
            assessment.IsPublished = true;
            StatusMessage = $"✓ '{assessment.Title}' published successfully.";
            await LoadAsync();
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
    }
}
