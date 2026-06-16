/*
 * SKYLearn IQ — .NET MAUI Tutor Desktop App  (Phase 3 — COMPLETE)
 * ================================================================
 * Purpose  : Windows desktop portal for tutors to manage learners, publish
 *            assessments, review session results, mark short-answer questions,
 *            and add written feedback.
 * Platform : Windows only (net9.0-windows10.0.19041.0)
 * Run      : dotnet run -f net9.0-windows10.0.19041.0  (from tutor-desktop/)
 * API      : Connects to FastAPI backend on http://localhost:8001
 *
 * DI Registration (this file)
 *   Singleton  — AuthService, ApiService
 *   Transient  — all ViewModels, all Pages, AppShell
 *
 * Navigation
 *   Unauthenticated  → LoginPage (NavigationPage wrapper)
 *   Authenticated    → AppShell (Locked flyout: Dashboard/Learners/Assessments/Sessions)
 *   Session detail   → Shell route "session-detail?sessionId={id}"
 *
 * See CONTEXT.md at the project root for full architecture and phase progress.
 */
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
