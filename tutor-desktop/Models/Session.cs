namespace SkyLearnIQ.Tutor.Models;

public class AnswerOut
{
    public int     Id               { get; set; }
    public int     QuestionId       { get; set; }
    public int?    SelectedOptionId { get; set; }
    public string? TextAnswer       { get; set; }
    public bool?   IsCorrect        { get; set; }
    public float   MarksAwarded     { get; set; }
    public bool    AutoMarked       { get; set; }

    public string CorrectDisplay => IsCorrect == true ? "✓ Correct"
                                  : IsCorrect == false ? "✗ Wrong"
                                  : "⏳ Pending";
}

public class ScoreOut
{
    public float  TotalMarksAwarded  { get; set; }
    public int    TotalMarksPossible { get; set; }
    public float  Percentage         { get; set; }
    public bool?  PassFail           { get; set; }

    public string PercentageDisplay => $"{Math.Round(Percentage)}%";
    public string PassFailDisplay   => PassFail == true ? "PASS" : PassFail == false ? "FAIL" : "Pending";
}

public class FeedbackOut
{
    public int      Id              { get; set; }
    public string   GeneratedBy     { get; set; } = "";
    public string   Content         { get; set; } = "";
    public string?  StrengthAreas   { get; set; }
    public string?  WeaknessAreas   { get; set; }
    public string?  Recommendations { get; set; }
    public DateTime CreatedAt       { get; set; }

    public string SourceDisplay => GeneratedBy == "AI" ? "🧠 AI Feedback" : "👨‍🏫 Tutor Feedback";
}

public class SessionSummaryOut
{
    public int       Id               { get; set; }
    public int       AssessmentId     { get; set; }
    public string    AssessmentTitle  { get; set; } = "";
    public int       LearnerId        { get; set; }
    public string    LearnerName      { get; set; } = "";
    public string    LearnerPhone     { get; set; } = "";
    public string    Status           { get; set; } = "";
    public DateTime  StartedAt        { get; set; }
    public DateTime? CompletedAt      { get; set; }
    public ScoreOut? Score            { get; set; }

    public string StatusDisplay  => Status switch
    {
        "COMPLETED"   => "✓ Completed",
        "IN_PROGRESS" => "⏳ In Progress",
        "ABANDONED"   => "✗ Abandoned",
        _             => Status
    };
    public string ScoreDisplay => Score != null ? $"{Math.Round(Score.Percentage)}%" : "—";
    public string DateDisplay  => (CompletedAt ?? StartedAt).ToString("dd MMM yyyy");
}

public class SessionOut
{
    public int              Id           { get; set; }
    public int              AssessmentId { get; set; }
    public int              LearnerId    { get; set; }
    public string           Status       { get; set; } = "";
    public DateTime         StartedAt    { get; set; }
    public DateTime?        CompletedAt  { get; set; }
    public List<AnswerOut>  Answers      { get; set; } = [];
    public ScoreOut?        Score        { get; set; }
    public List<FeedbackOut> Feedbacks   { get; set; } = [];
}
