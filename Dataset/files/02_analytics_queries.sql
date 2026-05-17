-- ============================================================
-- HAOAP - Advanced Analytics Queries
-- Demonstrates: CTEs, Window Functions, Ranking, Aggregates
-- ============================================================

USE HAOAP_DW;
GO

-- ── 1. Region Aid Ranking (Window Function) ───────────────────────────────
SELECT
    l.country,
    l.camp_name,
    SUM(f.total_cost_usd)          AS total_aid_usd,
    COUNT(DISTINCT f.beneficiary_sk) AS unique_beneficiaries,
    RANK()   OVER (ORDER BY SUM(f.total_cost_usd) DESC)           AS aid_rank,
    PERCENT_RANK() OVER (ORDER BY SUM(f.total_cost_usd) DESC)     AS aid_pct_rank,
    SUM(SUM(f.total_cost_usd)) OVER ()                            AS grand_total_usd,
    ROUND(100.0 * SUM(f.total_cost_usd)
          / SUM(SUM(f.total_cost_usd)) OVER (), 2)                AS pct_of_total
FROM Fact_AidDistribution f
JOIN Dim_Location l  ON f.location_sk  = l.location_sk
JOIN Dim_Time     t  ON f.time_sk      = t.time_sk
WHERE t.[year] = 2024
GROUP BY l.country, l.camp_name
ORDER BY aid_rank;
GO

-- ── 2. Monthly Aid Trend with Running Total ───────────────────────────────
WITH monthly AS (
    SELECT
        t.[year],
        t.[month],
        t.month_name,
        SUM(f.total_cost_usd)            AS monthly_aid_usd,
        COUNT(*)                         AS distributions,
        COUNT(DISTINCT f.beneficiary_sk) AS beneficiaries
    FROM Fact_AidDistribution f
    JOIN Dim_Time t ON f.time_sk = t.time_sk
    GROUP BY t.[year], t.[month], t.month_name
)
SELECT
    [year], [month], month_name,
    monthly_aid_usd,
    distributions,
    beneficiaries,
    SUM(monthly_aid_usd) OVER (PARTITION BY [year]
                                ORDER BY [month] ROWS UNBOUNDED PRECEDING) AS ytd_aid_usd,
    LAG(monthly_aid_usd, 1) OVER (ORDER BY [year],[month])                AS prev_month_aid,
    ROUND(100.0 * (monthly_aid_usd
        - LAG(monthly_aid_usd,1) OVER (ORDER BY [year],[month]))
        / NULLIF(LAG(monthly_aid_usd,1) OVER (ORDER BY [year],[month]),0), 2) AS mom_growth_pct
FROM monthly
ORDER BY [year], [month];
GO

-- ── 3. Cost Per Beneficiary by Program ───────────────────────────────────
WITH program_costs AS (
    SELECT
        p.program_name,
        p.sector,
        SUM(f.total_cost_usd)            AS total_cost,
        COUNT(DISTINCT f.beneficiary_sk) AS unique_bens,
        p.target_beneficiaries,
        p.budget_usd
    FROM Fact_AidDistribution f
    JOIN Dim_Program p ON f.program_sk = p.program_sk
    GROUP BY p.program_name, p.sector, p.target_beneficiaries, p.budget_usd
)
SELECT
    program_name,
    sector,
    total_cost,
    unique_bens,
    ROUND(total_cost / NULLIF(unique_bens,0), 2)     AS cost_per_beneficiary,
    budget_usd,
    ROUND(100.0 * total_cost / NULLIF(budget_usd,0), 2) AS budget_utilisation_pct,
    ROUND(100.0 * unique_bens / NULLIF(target_beneficiaries,0), 2) AS reach_pct,
    DENSE_RANK() OVER (ORDER BY total_cost / NULLIF(unique_bens,0)) AS efficiency_rank
FROM program_costs
ORDER BY efficiency_rank;
GO

-- ── 4. Delivery Delay Analysis ────────────────────────────────────────────
SELECT
    l.country,
    l.camp_name,
    f.aid_type,
    COUNT(*)                                        AS total_deliveries,
    SUM(CASE WHEN f.delay_days > 3 THEN 1 ELSE 0 END) AS delayed_gt3_days,
    ROUND(100.0 * SUM(CASE WHEN f.delay_days > 3 THEN 1 ELSE 0 END)
          / COUNT(*), 2)                             AS delay_rate_pct,
    AVG(CAST(f.delay_days AS FLOAT))                AS avg_delay_days,
    MAX(f.delay_days)                               AS max_delay_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY f.delay_days)
        OVER (PARTITION BY l.country)               AS median_delay_country
FROM Fact_AidDistribution f
JOIN Dim_Location l ON f.location_sk = l.location_sk
GROUP BY l.country, l.camp_name, f.aid_type
ORDER BY delay_rate_pct DESC;
GO

-- ── 5. Funding Utilisation Dashboard ─────────────────────────────────────
WITH funding_summary AS (
    SELECT
        d.donor_name,
        d.donor_type,
        p.program_name,
        p.sector,
        SUM(fn.pledged_amount_usd)   AS total_pledged,
        SUM(fn.received_amount_usd)  AS total_received,
        SUM(fn.utilised_amount_usd)  AS total_utilised,
        SUM(fn.balance_usd)          AS total_balance,
        AVG(fn.utilisation_rate_pct) AS avg_utilisation_pct
    FROM Fact_Funding fn
    JOIN Dim_Donor   d ON fn.donor_sk   = d.donor_sk
    JOIN Dim_Program p ON fn.program_sk = p.program_sk
    GROUP BY d.donor_name, d.donor_type, p.program_name, p.sector
)
SELECT *,
    RANK() OVER (ORDER BY total_pledged DESC)    AS donor_rank_by_pledge,
    RANK() OVER (ORDER BY avg_utilisation_pct DESC) AS efficiency_rank
FROM funding_summary
ORDER BY total_pledged DESC;
GO

-- ── 6. Health Outcomes Heatmap ────────────────────────────────────────────
SELECT
    l.country,
    h.condition_diagnosed,
    h.severity,
    COUNT(*)                                          AS cases,
    SUM(CASE WHEN h.outcome = 'Recovered' THEN 1 ELSE 0 END)  AS recovered,
    SUM(CASE WHEN h.outcome = 'Deceased'  THEN 1 ELSE 0 END)  AS deaths,
    ROUND(100.0 * SUM(CASE WHEN h.outcome='Recovered' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*),0), 2)                    AS recovery_rate_pct,
    ROUND(AVG(CAST(h.days_in_treatment AS FLOAT)),1)  AS avg_treatment_days,
    ROUND(AVG(h.cost_per_patient_usd), 2)             AS avg_cost_usd
FROM Fact_HealthServices h
JOIN Dim_Location l ON h.location_sk = l.location_sk
GROUP BY l.country, h.condition_diagnosed, h.severity
ORDER BY cases DESC;
GO

-- ── 7. Data Quality Dashboard Query ──────────────────────────────────────
SELECT
    'Fact_AidDistribution' AS table_name,
    COUNT(*)                                     AS total_records,
    SUM(CAST(data_quality_flag AS INT))          AS flagged_records,
    ROUND(100.0 * SUM(CAST(data_quality_flag AS INT)) / COUNT(*), 2) AS error_pct,
    SUM(CASE WHEN beneficiary_confirmed = 0 THEN 1 ELSE 0 END)       AS unconfirmed_beneficiaries,
    MAX(inserted_at)                             AS last_refresh
FROM Fact_AidDistribution
UNION ALL
SELECT
    'Fact_HealthServices',
    COUNT(*),
    SUM(CAST(data_quality_flag AS INT)),
    ROUND(100.0 * SUM(CAST(data_quality_flag AS INT)) / COUNT(*), 2),
    NULL,
    MAX(inserted_at)
FROM Fact_HealthServices;
GO

-- ── 8. Row-Level Security Setup ───────────────────────────────────────────
-- Creates RLS so regional managers only see their region
CREATE SCHEMA Security;
GO
CREATE FUNCTION Security.fn_rls_location_filter(@country SYSNAME)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS fn_result
    WHERE @country = USER_NAME()
       OR USER_NAME() = 'GlobalAdmin';
GO

CREATE SECURITY POLICY Fact_AidDistribution_RLS
ADD FILTER PREDICATE Security.fn_rls_location_filter(
    (SELECT l.country FROM Dim_Location l
     WHERE l.location_sk = Fact_AidDistribution.location_sk)
)
ON dbo.Fact_AidDistribution
WITH (STATE = ON);
GO
