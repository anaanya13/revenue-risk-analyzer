SELECT stage, count(*) AS open_deals, fsum(deal_value) AS open_value,
    count(*) FILTER (WHERE is_stalled) AS stalled_deals,
    coalesce(fsum(deal_value) FILTER (WHERE is_stalled), 0) AS revenue_at_risk,
    count(*) FILTER (WHERE is_stalled)::DOUBLE / count(*) AS stalled_share,
    avg(deal_age_days) AS average_open_age, avg(days_inactive) AS average_inactivity,
    count(follow_ups) AS follow_ups_recorded, avg(follow_ups) AS average_follow_ups
FROM assessed WHERE status = 'Open'
GROUP BY stage ORDER BY revenue_at_risk DESC, open_value DESC, stage;
