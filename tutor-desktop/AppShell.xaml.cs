using SkyLearnIQ.Tutor.Services;
using SkyLearnIQ.Tutor.Views;

namespace SkyLearnIQ.Tutor;

public partial class AppShell : Shell
{
    private readonly AuthService _auth;

    public AppShell(
        AuthService     auth,
        DashboardPage   dashboard,
        LearnersPage    learners,
        AssessmentsPage assessments,
        SessionsPage    sessions,
        IServiceProvider services)
    {
        InitializeComponent();
        _auth = auth;

        dashboardContent.Content   = dashboard;
        learnersContent.Content    = learners;
        assessmentsContent.Content = assessments;
        sessionsContent.Content    = sessions;

        TutorNameLabel.Text = auth.FullName ?? "";

        Routing.RegisterRoute("session-detail", typeof(SessionDetailPage));
    }

    private void OnSignOut_Clicked(object sender, EventArgs e)
    {
        _auth.ClearUser();
        if (Application.Current is App app)
            app.NavigateToLogin();
    }
}
