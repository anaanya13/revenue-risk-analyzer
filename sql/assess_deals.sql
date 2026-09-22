-- Input: validated selected raw columns, not Python-derived risk or age.
-- Parameters: analysis date, stalled threshold in days.
CREATE TEMP TABLE assessed AS
WITH settings AS (SELECT CAST(? AS DATE) AS analysis_date, CAST(? AS BIGINT) AS threshold),
ages AS (
    SELECT input_deals.*,
        CASE WHEN status = 'Open' THEN date_diff('day', CAST(created_date AS DATE), analysis_date) END AS deal_age_days,
        CASE WHEN status = 'Open' THEN date_diff('day', CAST(last_activity_date AS DATE), analysis_date) END AS days_inactive,
        threshold
    FROM input_deals CROSS JOIN settings
)
SELECT *,
    status = 'Open' AND coalesce(days_inactive >= threshold, false) AS is_stalled,
    CASE WHEN status <> 'Open' THEN 'Closed'
         WHEN days_inactive >= 2 * threshold THEN 'Critical'
         WHEN days_inactive >= threshold THEN 'High'
         WHEN days_inactive >= ceil(threshold / 2.0) THEN 'Medium'
         ELSE 'Low' END AS risk_severity
FROM ages;
