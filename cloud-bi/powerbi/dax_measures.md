# SKYLearn IQ — Power BI Dataset Schema & DAX Measures

Connect Power BI Desktop to the Synapse serverless SQL endpoint:
**Server:** `skylearn-synapse.sql.azuresynapse.net`  
**Database:** `skylearn_iq`  
**Tables to import:** All `gold_*` tables + all `vw_*` views

---

## Tables & Relationships

```
gold_learner_cohorts (learner_id PK)
    └─ 1:many ─→ gold_monthly_trends  (via learner_id if added)

gold_subject_performance (subject_name PK)
    └─ 1:many ─→ gold_assessment_stats (via subject_name)
```

---

## DAX Measures

```dax
-- ── Overall KPIs ─────────────────────────────────────────────

Total Learners =
    COUNTROWS(gold_learner_cohorts)

At Risk Count =
    CALCULATE(COUNTROWS(gold_learner_cohorts),
              gold_learner_cohorts[risk_flag] = "At Risk")

At Risk % =
    DIVIDE([At Risk Count], [Total Learners], 0) * 100

Platform Avg Score =
    AVERAGE(gold_learner_cohorts[avg_score])

Platform Pass Rate =
    AVERAGE(gold_learner_cohorts[pass_rate]) * 100

-- ── Subject Performance ──────────────────────────────────────

Weakest Subject =
    CALCULATE(
        FIRSTNONBLANK(gold_subject_performance[subject_name], 1),
        TOPN(1, gold_subject_performance, gold_subject_performance[avg_score], ASC)
    )

Strongest Subject =
    CALCULATE(
        FIRSTNONBLANK(gold_subject_performance[subject_name], 1),
        TOPN(1, gold_subject_performance, gold_subject_performance[avg_score], DESC)
    )

Subject Pass Rate % =
    AVERAGE(gold_subject_performance[pass_rate])

-- ── Trend ────────────────────────────────────────────────────

Monthly Sessions =
    SUM(gold_monthly_trends[session_count])

Score Trend (MoM) =
    VAR latest  = CALCULATE(MAX(gold_monthly_trends[avg_score]),
                            LASTDATE(gold_monthly_trends[session_month]))
    VAR previous = CALCULATE(MAX(gold_monthly_trends[avg_score]),
                             PREVIOUSMONTH(gold_monthly_trends[session_month]))
    RETURN DIVIDE(latest - previous, previous, 0) * 100

-- ── Cohort Distribution ──────────────────────────────────────

Distinction Count =
    CALCULATE(COUNTROWS(gold_learner_cohorts),
              gold_learner_cohorts[performance_band] = "Distinction")

Below Pass Count =
    CALCULATE(COUNTROWS(gold_learner_cohorts),
              gold_learner_cohorts[performance_band] = "Below Pass")
```

---

## Recommended Dashboard Pages

| Page | Visuals |
|------|---------|
| **Overview** | KPI cards: Total Learners, At Risk %, Avg Score, Pass Rate |
| **Subject Performance** | Clustered bar: avg score by subject · Gauge: platform pass rate |
| **Learner Cohorts** | Scatter: sessions vs score (colour = risk flag) · Donut: performance bands |
| **Trends** | Line: monthly avg score + session volume · Area: learners active per month |
| **Assessments** | Table: title, subject, attempts, avg score, pass rate, avg duration |
| **At-Risk Drill** | Filtered table of at-risk learners with last active date + grade |
