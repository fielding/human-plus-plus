-- Human++ SQL Sample
--
-- Analytics queries for user activity dashboard

-- Create tables with proper indexes
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- !! This index is critical for dashboard query performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_user_created
    ON events (user_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_type_created
    ON events (event_type, created_at DESC);

-- Daily active users for the last 30 days
WITH daily_active AS (
    SELECT
        DATE_TRUNC('day', e.created_at) AS day,
        COUNT(DISTINCT e.user_id) AS active_users
    FROM events e
    JOIN users u ON e.user_id = u.id
    WHERE e.created_at >= NOW() - INTERVAL '30 days'
      AND u.deleted_at IS NULL
    GROUP BY DATE_TRUNC('day', e.created_at)
)
SELECT
    day,
    active_users,
    AVG(active_users) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_avg
FROM daily_active
ORDER BY day DESC;

-- ?? Should we add a materialized view for this aggregation?
-- User engagement metrics
SELECT
    u.id,
    u.name,
    u.email,
    COUNT(e.id) AS total_events,
    COUNT(DISTINCT DATE_TRUNC('day', e.created_at)) AS active_days,
    MAX(e.created_at) AS last_active,
    MIN(e.created_at) AS first_active,
    EXTRACT(EPOCH FROM (MAX(e.created_at) - MIN(e.created_at))) / 86400 AS tenure_days
FROM users u
LEFT JOIN events e ON e.user_id = u.id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.name, u.email
HAVING COUNT(e.id) > 0
ORDER BY total_events DESC
LIMIT 100;

-- Event type breakdown by week
SELECT
    DATE_TRUNC('week', created_at) AS week,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users
FROM events
WHERE created_at >= NOW() - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', created_at), event_type
ORDER BY week DESC, event_count DESC;

-- >> Soft delete preserves data for audit - never hard delete users
UPDATE users
SET deleted_at = NOW(),
    updated_at = NOW()
WHERE id = $1
  AND deleted_at IS NULL
RETURNING id, email, deleted_at;

-- Cleanup old events (retention policy)
DELETE FROM events
WHERE created_at < NOW() - INTERVAL '2 years'
  AND id IN (
    SELECT id FROM events
    WHERE created_at < NOW() - INTERVAL '2 years'
    LIMIT 10000
);
