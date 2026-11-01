-- Analytical views on top of the star schema.
-- All sign conventions and ratio formulas live here, in one place.

DROP VIEW IF EXISTS vw_cob_quarterly;
DROP VIEW IF EXISTS vw_fact_cob;

-- Wide fact view (used by Power BI):
-- one row per quarter + class of business + state.
-- Expenses are flipped to positive numbers (APRA reports them as negatives).
CREATE VIEW vw_fact_cob AS
WITH pivoted AS (
    SELECT
        f.quarter_id,
        f.class_id,
        f.state_id,
        SUM(CASE WHEN m.metric_name = 'insurance_revenue'         THEN f.value END) AS insurance_revenue,
        -SUM(CASE WHEN m.metric_name = 'incurred_claims'           THEN f.value END) AS incurred_claims,
        -SUM(CASE WHEN m.metric_name = 'insurance_service_expense' THEN f.value END) AS insurance_service_expense,
        SUM(CASE WHEN m.metric_name = 'service_result_gross'      THEN f.value END) AS service_result_gross,
        SUM(CASE WHEN m.metric_name = 'service_result_net'        THEN f.value END) AS service_result_net,
        SUM(CASE WHEN m.metric_name = 'gross_written_premium'     THEN f.value END) AS gross_written_premium
    FROM fact_cob_metric AS f
    JOIN dim_metric AS m ON m.metric_id = f.metric_id
    GROUP BY f.quarter_id, f.class_id, f.state_id
)
SELECT
    p.*,
    -- Matched denominators: only count revenue where the numerator is not masked,
    -- so ratios summed across rows are not biased downwards by masked values.
    CASE WHEN p.incurred_claims IS NOT NULL
         THEN p.insurance_revenue END AS revenue_claims_base,
    CASE WHEN p.insurance_service_expense IS NOT NULL
         THEN p.insurance_revenue END AS revenue_expense_base
FROM pivoted AS p;

-- Readable view for SQL analysis and validation:
-- descriptive attributes plus quarterly ratios.
CREATE VIEW vw_cob_quarterly AS
SELECT
    q.quarter_id,
    q.period_end,
    q.quarter_label,
    q.financial_year,
    c.class_of_business,
    c.class_category,
    c.class_group,
    s.state_name,
    s.state_code,
    x.insurance_revenue,
    x.incurred_claims,
    x.insurance_service_expense,
    x.service_result_gross,
    x.revenue_claims_base,
    x.revenue_expense_base,
    x.incurred_claims           / NULLIF(x.insurance_revenue, 0) AS loss_ratio,
    x.insurance_service_expense / NULLIF(x.insurance_revenue, 0) AS combined_ratio
FROM vw_fact_cob AS x
JOIN dim_quarter AS q ON q.quarter_id = x.quarter_id
JOIN dim_class   AS c ON c.class_id   = x.class_id
JOIN dim_state   AS s ON s.state_id   = x.state_id;