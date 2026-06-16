namespace SkyLearnIQ.Tutor.Models;

public class SubjectOut
{
    public int    Id   { get; set; }
    public string Name { get; set; } = "";
    public string Code { get; set; } = "";
}

public class OptionOut
{
    public int    Id       { get; set; }
    public string Text     { get; set; } = "";
    public bool   IsCorrect { get; set; }
    public int    OrderNum { get; set; }
}

public class QuestionOut
{
    public int          Id         { get; set; }
    public string       Text       { get; set; } = "";
    public string       QType      { get; set; } = "";
    public float        Marks      { get; set; }
    public string       Difficulty { get; set; } = "";
    public string?      ConceptTag { get; set; }
    public int          OrderNum   { get; set; }
    public List<OptionOut> Options { get; set; } = [];
}

public class AssessmentOut
{
    public int         Id           { get; set; }
    public string      Title        { get; set; } = "";
    public string?     Description  { get; set; }
    public float       TotalMarks   { get; set; }
    public int         TimeLimitMin { get; set; }
    public bool        IsPublished  { get; set; }
    public SubjectOut? Subject      { get; set; }
    public List<QuestionOut> Questions { get; set; } = [];

    public string SubjectName     => Subject?.Name ?? "—";
    public string PublishedStatus => IsPublished ? "✓ Published" : "Draft";
    public int    QuestionCount   => Questions.Count;
}
