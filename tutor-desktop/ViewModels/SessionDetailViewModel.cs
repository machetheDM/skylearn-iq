using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Models;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class SessionDetailViewModel : ObservableObject
{
    [ObservableProperty] bool        isBusy          = false;
    [ObservableProperty] SessionOut? session;
    [ObservableProperty] string      statusMessage   = "";
    [ObservableProperty] string      feedbackContent = "";
    [ObservableProperty] string      fbStrengths     = "";
    [ObservableProperty] string      fbWeaknesses    = "";
    [ObservableProperty] string      fbRecommend     = "";

    public ObservableCollection<AnswerOut>   Answers   { get; } = [];
    public ObservableCollection<FeedbackOut> Feedbacks { get; } = [];

    private readonly ApiService _api;
    public SessionDetailViewModel(ApiService api) => _api = api;

    public async Task LoadSessionAsync(int sessionId)
    {
        IsBusy = true;
        Answers.Clear();
        Feedbacks.Clear();
        StatusMessage = "";
        try
        {
            var s = await _api.GetSessionAsync(sessionId);
            Session = s;
            foreach (var a in s.Answers.OrderBy(a => a.QuestionId)) Answers.Add(a);
            foreach (var f in s.Feedbacks) Feedbacks.Add(f);
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error loading session: {ex.Message}";
        }
        finally { IsBusy = false; }
    }

    [RelayCommand]
    async Task MarkAnswerAsync(AnswerOut answer)
    {
        if (Session is null) return;
        var input = await Shell.Current.DisplayPromptAsync(
            "Mark Answer",
            $"Enter marks awarded (max {answer.MarksAwarded} recorded):",
            initialValue: answer.MarksAwarded.ToString(),
            keyboard: Keyboard.Numeric);
        if (input is null) return;
        if (!float.TryParse(input, out var marks)) { StatusMessage = "Invalid marks value."; return; }

        var correct = await Shell.Current.DisplayAlert("Correct?", "Is this answer correct?", "Yes", "No");
        try
        {
            await _api.MarkAnswerAsync(Session.Id, answer.Id, marks, correct);
            answer.MarksAwarded = marks;
            answer.IsCorrect    = correct;
            StatusMessage = "✓ Answer marked.";
            await LoadSessionAsync(Session.Id);
        }
        catch (Exception ex) { StatusMessage = $"Error: {ex.Message}"; }
    }

    [RelayCommand]
    async Task AddFeedbackAsync()
    {
        if (Session is null || string.IsNullOrWhiteSpace(FeedbackContent))
        {
            StatusMessage = "Feedback content is required.";
            return;
        }
        IsBusy = true;
        try
        {
            await _api.AddFeedbackAsync(Session.Id, FeedbackContent,
                string.IsNullOrWhiteSpace(FbStrengths)    ? null : FbStrengths,
                string.IsNullOrWhiteSpace(FbWeaknesses)   ? null : FbWeaknesses,
                string.IsNullOrWhiteSpace(FbRecommend)    ? null : FbRecommend);
            StatusMessage    = "✓ Feedback saved.";
            FeedbackContent  = "";
            FbStrengths      = "";
            FbWeaknesses     = "";
            FbRecommend      = "";
            await LoadSessionAsync(Session.Id);
        }
        catch (Exception ex) { StatusMessage = $"Error: {ex.Message}"; }
        finally { IsBusy = false; }
    }

    [RelayCommand]
    async Task GoBackAsync() => await Shell.Current.GoToAsync("..");
}
