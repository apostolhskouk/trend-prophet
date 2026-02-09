CREATE TABLE trends (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL,
    source TEXT NOT NULL,
    volume INTEGER,
    velocity NUMERIC(10,2),
    monetization_score NUMERIC(3,2),
    detected_at TIMESTAMP DEFAULT NOW(),
    country TEXT DEFAULT 'GR',
    UNIQUE(keyword, source, DATE(detected_at))
);

CREATE TABLE executions (
    id SERIAL PRIMARY KEY,
    trend_id INTEGER REFERENCES trends(id),
    strategy TEXT,
    platform TEXT,
    published_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue NUMERIC(10,2) DEFAULT 0,
    executed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trends_score ON trends(monetization_score DESC, detected_at DESC);
CREATE INDEX idx_trends_keyword ON trends(keyword);
