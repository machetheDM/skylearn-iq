using SkyLearnIQ.Tutor.ViewModels;

namespace SkyLearnIQ.Tutor.Views;

public partial class SessionDetailPage : ContentPage, IQueryAttributable
{
    private readonly SessionDetailViewModel _vm;

    public SessionDetailPage(SessionDetailViewModel vm)
    {
        InitializeComponent();
        _vm = vm;
        BindingContext = vm;
    }

    public void ApplyQueryAttributes(IDictionary<string, object> query)
    {
        if (query.TryGetValue("sessionId", out var val))
            _vm.LoadSessionAsync(Convert.ToInt32(val)).ContinueWith(_ => { });
    }
}
