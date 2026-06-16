using SkyLearnIQ.Tutor.Models;

namespace SkyLearnIQ.Tutor.Services;

public class AuthService
{
    private const string TokenKey    = "skylearn_token";
    private const string UserNameKey = "skylearn_user_name";
    private const string UserIdKey   = "skylearn_user_id";

    public string? Token    => Preferences.Get(TokenKey,    null);
    public string? FullName => Preferences.Get(UserNameKey, null);
    public int     UserId   => Preferences.Get(UserIdKey,   0);
    public bool    IsLoggedIn => !string.IsNullOrEmpty(Token);

    public void SetUser(AuthUser user)
    {
        Preferences.Set(TokenKey,    user.AccessToken);
        Preferences.Set(UserNameKey, user.FullName);
        Preferences.Set(UserIdKey,   user.UserId);
    }

    public void ClearUser()
    {
        Preferences.Remove(TokenKey);
        Preferences.Remove(UserNameKey);
        Preferences.Remove(UserIdKey);
    }
}
