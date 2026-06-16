using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SkyLearnIQ.Tutor.Services;

namespace SkyLearnIQ.Tutor.ViewModels;

public partial class LoginViewModel : ObservableObject
{
    [ObservableProperty] string  phone        = "";
    [ObservableProperty] string  password     = "";
    [ObservableProperty] bool    isLoading    = false;
    [ObservableProperty] string  errorMessage = "";

    private readonly ApiService  _api;
    private readonly AuthService _auth;

    public LoginViewModel(ApiService api, AuthService auth)
    {
        _api  = api;
        _auth = auth;
    }

    [RelayCommand]
    async Task LoginAsync()
    {
        ErrorMessage = "";
        if (string.IsNullOrWhiteSpace(Phone) || string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "Phone and password are required.";
            return;
        }
        IsLoading = true;
        try
        {
            var user = await _api.LoginAsync(Phone.Trim(), Password);
            if (user.Role != "TUTOR" && user.Role != "ADMIN")
            {
                ErrorMessage = "Access denied. This portal is for tutors only.";
                return;
            }
            _auth.SetUser(user);
            if (Application.Current is App app)
                app.NavigateToShell();
        }
        catch (Exception ex)
        {
            ErrorMessage = ex.Message;
        }
        finally
        {
            IsLoading = false;
        }
    }
}
