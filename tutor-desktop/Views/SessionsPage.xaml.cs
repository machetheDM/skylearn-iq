using SkyLearnIQ.Tutor.ViewModels;

namespace SkyLearnIQ.Tutor.Views;

public partial class SessionsPage : ContentPage
{
    private readonly SessionsViewModel _vm;

    public SessionsPage(SessionsViewModel vm)
    {
        InitializeComponent();
        _vm = vm;
        BindingContext = vm;
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        _vm.LoadCommand.Execute(null);
    }
}
