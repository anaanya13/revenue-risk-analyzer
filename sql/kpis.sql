WITH totals AS (
    SELECT count(*) AS deal_count,
        count(*) FILTER (WHERE status = 'Open') AS open_deals,
        count(*) FILTER (WHERE status = 'Won') AS won_deals,
        count(*) FILTER (WHERE status = 'Lost') AS lost_deals,
        coalesce(fsum(deal_value), 0) AS total_deal_value,
        coalesce(fsum(deal_value) FILTER (WHERE status = 'Open'), 0) AS open_pipeline_value,
        coalesce(fsum(deal_value) FILTER (WHERE status = 'Won'), 0) AS won_deal_value,
        coalesce(fsum(deal_value) FILTER (WHERE status = 'Lost'), 0) AS lost_deal_value,
        avg(deal_age_days) AS average_open_age,
        avg(days_inactive) AS average_inactivity,
        count(*) FILTER (WHERE is_stalled) AS stalled_deals,
        coalesce(fsum(deal_value) FILTER (WHERE is_stalled), 0) AS revenue_at_risk
    FROM assessed
)
SELECT *, total_deal_value / nullif(deal_count, 0) AS average_deal_value,
    won_deals::DOUBLE / nullif(won_deals + lost_deals, 0) AS win_rate,
    revenue_at_risk / nullif(open_pipeline_value, 0) AS revenue_at_risk_share
FROM totals;
