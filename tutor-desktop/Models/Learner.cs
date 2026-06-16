namespace SkyLearnIQ.Tutor.Models;

public class LearnerOut
{
    public int     UserId        { get; set; }
    public int     LearnerId     { get; set; }
    public string  FullName      { get; set; } = "";
    public string  Phone         { get; set; } = "";
    public string? Grade         { get; set; }
    public string  Track         { get; set; } = "";
    public int     TotalSessions { get; set; }

    public string TrackDisplay => Track switch
    {
        "CAPS_FULL_TIME" => "CAPS Full-Time",
        "MATRIC_UPGRADE" => "Matric Upgrade",
        "CODING"         => "Coding",
        "CYBER"          => "Cybersecurity",
        _                => Track
    };

    public string GradeDisplay => string.IsNullOrEmpty(Grade) ? "—" : $"Gr {Grade}";
}
