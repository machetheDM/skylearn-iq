namespace SkyLearnIQ.Tutor.Models;

public class AuthUser
{
    public string AccessToken { get; set; } = "";
    public string TokenType  { get; set; } = "bearer";
    public string Role       { get; set; } = "";
    public int    UserId     { get; set; }
    public string FullName   { get; set; } = "";
}
