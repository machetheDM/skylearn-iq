using SkyLearnIQ.Tutor.ViewModels;

namespace SkyLearnIQ.Tutor.Views;

public partial class AssessmentsPage : ContentPage
{
    private readonly AssessmentsViewModel _vm;

    public AssessmentsPage(AssessmentsViewModel vm)
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
