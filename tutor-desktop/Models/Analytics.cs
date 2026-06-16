namespace SkyLearnIQ.Tutor.Models;

public class AtRiskResult
{
    public int    LearnerId    { get; set; }
    public int    UserId       { get; set; }
    public string FullName     { get; set; } = "";
    public float  AvgScore     { get; set; }
    public float  PassRate     { get; set; }
    public int    TotalSessions { get; set; }
    public float  RiskScore    { get; set; }
    public bool   IsAtRisk     { get; set; }
    public string RiskLabel    { get; set; } = "";

    public string RiskPercentage => $"{Math.Round(RiskScore * 100)}%";
    public string AvgScoreDisplay => $"{Math.Round(AvgScore)}%";
}

public class ClusterResult
{
    public int    LearnerId    { get; set; }
    public string FullName     { get; set; } = "";
    public float  AvgScore     { get; set; }
    public int    ClusterId    { get; set; }
    public string ClusterLabel { get; set; } = "";
    public int    TotalSessions { get; set; }
}

public class AnalyticsSummary
{
    public int                    TotalLearners        { get; set; }
    public int                    AtRiskCount          { get; set; }
    public float                  AvgScoreOverall      { get; set; }
    public Dictionary<string,int> ClusterDistribution  { get; set; } = [];
    public string                 TrendDirection       { get; set; } = "";

    public string AvgScoreDisplay    => $"{Math.Round(AvgScoreOverall)}%";
    public string TrendEmoji         => TrendDirection == "improving" ? "↑ Improving"
                                      : TrendDirection == "declining" ? "↓ Declining"
                                      : "→ Stable";
    public string AtRiskDisplay      => $"{AtRiskCount} / {TotalLearners}";
}
