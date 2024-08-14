CREATE TABLE captions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    tags TEXT[],  -- Assuming tags are stored as an array of strings
    length VARCHAR(20),  -- Short, Medium, Long
    category VARCHAR(50),
    tone VARCHAR(20),
    audience VARCHAR(50) DEFAULT 'general',
    language VARCHAR(10) DEFAULT 'en',
    engagement JSONB DEFAULT '{}',  -- Assuming engagement is stored as a JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
