using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Models;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class AnalyticsViewModel : ObservableObject
{
    [ObservableProperty] bool              isBusy        = false;
    [ObservableProperty] string            statusMessage = "";
    [ObservableProperty] AnalyticsSummary? summary;
    [ObservableProperty] bool              mlOffline     = false;

    public ObservableCollection<AtRiskResult>  AtRiskLearners { get; } = [];
    public ObservableCollection<ClusterResult> Clusters       { get; } = [];

    private readonly MlApiService _ml;
    public AnalyticsViewModel(MlApiService ml) => _ml = ml;

    [RelayCommand]
    async Task LoadAsync()
    {
        IsBusy = true;
        MlOffline = false;
        StatusMessage = "";
        AtRiskLearners.Clear();
        Clusters.Clear();

        try
        {
            var sumTask     = _ml.GetSummaryAsync();
            var riskTask    = _ml.GetAtRiskAsync();
            var clusterTask = _ml.GetClustersAsync();
            await Task.WhenAll(sumTask, riskTask, clusterTask);

            Summary = sumTask.Result;
            foreach (var l in riskTask.Result)    AtRiskLearners.Add(l);
            foreach (var c in clusterTask.Result) Clusters.Add(c);
        }
        catch (HttpRequestException)
        {
            MlOffline     = true;
            StatusMessage = "ML Engine offline. Start: python -m uvicorn main:app --port 8002";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
        finally { IsBusy = false; }
    }
}
