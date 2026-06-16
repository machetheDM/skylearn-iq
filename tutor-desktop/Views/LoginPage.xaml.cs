using SkyLearnIQ.Tutor.ViewModels;

namespace SkyLearnIQ.Tutor.Views;

public partial class LoginPage : ContentPage
{
    public LoginPage(LoginViewModel vm)
    {
        InitializeComponent();
        BindingContext = vm;
    }
}
