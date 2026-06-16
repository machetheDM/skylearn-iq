using Microsoft.Extensions.Logging;
using SkyLearnIQ.Tutor.Services;
using SkyLearnIQ.Tutor.ViewModels;
using SkyLearnIQ.Tutor.Views;

namespace SkyLearnIQ.Tutor;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf",    "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf",   "OpenSansSemibold");
            });

        // Services
        builder.Services.AddSingleton<AuthService>();
        builder.Services.AddSingleton<ApiService>();

        // ViewModels
        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<LearnersViewModel>();
        builder.Services.AddTransient<AssessmentsViewModel>();
        builder.Services.AddTransient<SessionsViewModel>();
        builder.Services.AddTransient<SessionDetailViewModel>();

        // Pages
        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<LearnersPage>();
        builder.Services.AddTransient<AssessmentsPage>();
        builder.Services.AddTransient<SessionsPage>();
        builder.Services.AddTransient<SessionDetailPage>();

        // Shell (transient so a fresh one is created on each login)
        builder.Services.AddTransient<AppShell>();

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}
