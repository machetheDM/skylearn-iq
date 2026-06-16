using SkyLearnIQ.Tutor.Services;
using SkyLearnIQ.Tutor.Views;

namespace SkyLearnIQ.Tutor;

public partial class App : Application
{
    private readonly AuthService     _auth;
    private readonly IServiceProvider _services;

    public App(AuthService auth, IServiceProvider services)
    {
        InitializeComponent();
        _auth     = auth;
        _services = services;
    }

    protected override Window CreateWindow(IActivationState? activationState)
    {
        Page startPage = _auth.IsLoggedIn
            ? _services.GetRequiredService<AppShell>()
            : new NavigationPage(_services.GetRequiredService<LoginPage>());

        return new Window(startPage) { Title = "SKYLearn IQ — Tutor Portal" };
    }

    public void NavigateToShell() => MainThread.BeginInvokeOnMainThread(() =>
    {
        var win = Windows.FirstOrDefault();
        if (win is not null) win.Page = _services.GetRequiredService<AppShell>();
    });

    public void NavigateToLogin() => MainThread.BeginInvokeOnMainThread(() =>
    {
        var win = Windows.FirstOrDefault();
        if (win is not null) win.Page = new NavigationPage(_services.GetRequiredService<LoginPage>());
    });
}